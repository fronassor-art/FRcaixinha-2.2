"""Porta autenticadora simulada; não gera login nem sessão operacional."""

import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID

from app.offline_credentials import SessionFacts
from app.trusted_auth_subject import (
    AuthTrustError, VerifiedAuthAssertion, resolve_auth_subject,
)


NOW = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)
SUBJECT = UUID("00000000-0000-4000-8000-000000000201")
OTHER = UUID("00000000-0000-4000-8000-000000000202")
ASSERTION = b"synthetic-opaque-assertion-only"


class FakeVerifier:
    def __init__(self, fact):
        self.fact = fact
        self.calls = 0

    def verify_assertion(self, assertion):
        self.calls += 1
        return self.fact


class TrustedAuthSubjectTests(unittest.TestCase):
    def setUp(self):
        self.session = SessionFacts(
            SUBJECT, NOW - timedelta(minutes=1),
            NOW + timedelta(minutes=14), None)
        self.fact = VerifiedAuthAssertion(
            "local", "frcaixinha-api", SUBJECT, self.session)

    def resolve(self, fact=None, **changes):
        args = dict(assertion=ASSERTION, verifier=FakeVerifier(
            self.fact if fact is None else fact), expected_issuer="local", now=NOW)
        args.update(changes)
        return resolve_auth_subject(**args)

    def test_subject_is_namespaced_stable_uuid_not_pii_or_role(self):
        resolved = self.resolve()
        self.assertEqual(resolved.value, f"local:{SUBJECT}")
        self.assertEqual(resolved.subject_id, SUBJECT)
        self.assertNotIn("@", resolved.value)
        self.assertFalse(hasattr(resolved, "tenant_id"))
        self.assertFalse(hasattr(resolved, "role"))
        self.assertNotIn(str(SUBJECT), repr(resolved))

    def test_expired_revoked_and_identity_mismatch_are_rejected(self):
        for session in (
            replace(self.session, expires_at=NOW),
            replace(self.session, revoked_at=NOW),
            replace(self.session, subject_id=OTHER),
            replace(self.session, expires_at=NOW + timedelta(hours=1)),
        ):
            with self.subTest(session=session):
                with self.assertRaisesRegex(AuthTrustError,
                                            "^AUTH_ASSERTION_REJECTED$"):
                    self.resolve(replace(self.fact, session=session))

    def test_wrong_issuer_audience_or_untrusted_fact_is_rejected(self):
        for fact in (replace(self.fact, issuer="other"),
                     replace(self.fact, audience="untrusted-api"),
                     replace(self.fact, subject_id=OTHER),
                     {"subject": str(SUBJECT)}):
            with self.subTest(type=type(fact).__name__):
                with self.assertRaises(AuthTrustError):
                    self.resolve(fact)

    def test_missing_verifier_bad_assertion_or_policy_fails_closed(self):
        for args in (dict(verifier=None), dict(assertion=b"short"),
                     dict(assertion="client-header"),
                     dict(expected_issuer="local@example.com"),
                     dict(now=NOW.replace(tzinfo=None))):
            with self.subTest(changed=list(args)):
                with self.assertRaises(AuthTrustError):
                    self.resolve(**args)

    def test_verifier_exception_is_redacted(self):
        class BrokenVerifier:
            def verify_assertion(self, _assertion):
                raise RuntimeError("DOCUMENT_OR_SECRET")

        with self.assertRaises(AuthTrustError) as caught:
            self.resolve(verifier=BrokenVerifier())
        self.assertEqual(str(caught.exception), "AUTH_ASSERTION_REJECTED")
        self.assertNotIn("DOCUMENT_OR_SECRET", repr(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_no_implicit_file_network_or_database_access(self):
        with patch("builtins.open") as file, patch("socket.socket") as network:
            with patch("psycopg.connect") as db:
                self.resolve()
        file.assert_not_called()
        network.assert_not_called()
        db.assert_not_called()
