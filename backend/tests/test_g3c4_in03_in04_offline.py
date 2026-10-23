"""G3-C.4 IN-03/IN-04: evidencias OFFLINE, inclusive lacunas explicitadas.

Testes com stubs sinteticos, sem banco, e-mail real, login ou concorrencia SQL.
Os casos de "limite" demonstram falta de garantia operacional, NAO seguranca PASS.
"""

import unittest
from dataclasses import fields, replace
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID

from app.email_confirmation_offline import (
    EmailChallengeRecord, prepare_email_challenge,
    verify_and_consume_email_challenge,
)
from app.offline_credentials import PasswordCheck
from app.opaque_sessions_offline import (
    prepare_opaque_session, resolve_opaque_session,
)


NOW = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)
IDENTITY = UUID(int=101)
CHALLENGE = UUID(int=102)
SESSION = UUID(int=103)
EMAIL = "person@example.com"


class _Entropy:
    def generate(self, length):
        return b"S" * length


class _Ids:
    def new_uuid(self):
        return SESSION


class _AtomicSequentialConsumption:
    def __init__(self):
        self.used = set()
        self.calls = 0

    def consume_once(self, challenge_id, verifier):
        self.calls += 1
        key = (challenge_id, verifier)
        if key in self.used:
            return False
        self.used.add(key)
        return True


class _UnsafeAlwaysTrueConsumption:
    def __init__(self):
        self.calls = 0

    def consume_once(self, _challenge_id, _verifier):
        self.calls += 1
        return True


class _MutableSessionStore:
    def __init__(self, record):
        self.record = record
        self.calls = 0
        self.identity_status = "ATIVA"
        self.password_revision = 1

    def find_by_verifier(self, _verifier):
        self.calls += 1
        return self.record


class G3C4In03In04OfflineTests(unittest.TestCase):
    def setUp(self):
        self.challenge = prepare_email_challenge(
            challenge_id=CHALLENGE, identity_id=IDENTITY,
            email="PERSON@EXAMPLE.COM", now=NOW, entropy=_Entropy(),
        )
        self.session = prepare_opaque_session(
            identity_id=IDENTITY, identity_status="ATIVA",
            email_verified_at=NOW - timedelta(minutes=1),
            password_check=PasswordCheck(True, False),
            now=NOW, entropy=_Entropy(), ids=_Ids(),
        )

    def _verify(self, consumption, *, email=EMAIL, record=None, now=None):
        return verify_and_consume_email_challenge(
            record=self.challenge.record if record is None else record,
            candidate=self.challenge.delivery_secret,
            identity_id=IDENTITY,
            email=email, now=NOW + timedelta(minutes=1) if now is None else now,
            consumption=consumption,
        )

    def test_in03_matching_contact_consumes_once_with_cooperating_stub(self):
        consumer = _AtomicSequentialConsumption()
        self.assertTrue(self._verify(consumer))
        self.assertFalse(self._verify(consumer))
        self.assertEqual(consumer.calls, 2)
        self.assertEqual(self.challenge.record.email, EMAIL)
        self.assertEqual(len(self.challenge.record.verifier_sha256), 32)

    def test_in03_changed_email_input_fails_before_storage_call(self):
        consumer = _AtomicSequentialConsumption()
        self.assertFalse(self._verify(consumer, email="updated@example.com"))
        self.assertEqual(consumer.calls, 0)
        self.assertFalse(self._verify(
            consumer, now=NOW + timedelta(minutes=10),
        ))
        self.assertEqual(consumer.calls, 0)

    def test_in03_limit_old_contact_input_does_not_prove_current_email(self):
        """Counterexample: caller can supply old email; no authoritative read."""
        authoritative_current_email = "updated@example.com"
        self.assertNotEqual(authoritative_current_email,
                            self.challenge.record.email)
        consumer = _AtomicSequentialConsumption()
        self.assertTrue(self._verify(consumer, email=EMAIL))
        # This PASS demonstrates missing trusted-current-email enforcement,
        # not that changed-contact confirmation is operationally secure.

    def test_in03_limit_unconditional_stub_allows_duplicate_consumption(self):
        """Counterexample: offline function trusts consume_once's atomicity."""
        consumer = _UnsafeAlwaysTrueConsumption()
        self.assertTrue(self._verify(consumer))
        self.assertTrue(self._verify(consumer))
        self.assertEqual(consumer.calls, 2)
        # Only a transactional adapter can enforce exactly-once use.

    def test_in03_limit_purpose_not_present_in_record_contract(self):
        """Purpose exists in proposed migration, not in offline record."""
        self.assertNotIn("purpose", {x.name for x in fields(EmailChallengeRecord)})
        self.assertTrue(self._verify(_AtomicSequentialConsumption()))

    def test_in04_session_store_is_requeried_and_revocation_denies(self):
        store = _MutableSessionStore(self.session.record)
        self.assertIsNotNone(resolve_opaque_session(
            token=self.session.delivery_token, now=NOW, store=store,
        ))
        store.record = replace(store.record, revoked_at=NOW)
        self.assertIsNone(resolve_opaque_session(
            token=self.session.delivery_token, now=NOW, store=store,
        ))
        self.assertEqual(store.calls, 2)

    def test_in04_limit_suspension_without_revoke_not_in_record_contract(self):
        """Counterexample: only the session row is queried for validity."""
        store = _MutableSessionStore(self.session.record)
        self.assertIsNotNone(resolve_opaque_session(
            token=self.session.delivery_token, now=NOW, store=store,
        ))
        store.identity_status = "SUSPENSA"
        self.assertIsNotNone(resolve_opaque_session(
            token=self.session.delivery_token, now=NOW, store=store,
        ))
        self.assertEqual(store.calls, 2)

    def test_in04_limit_password_change_without_revoke_not_in_record(self):
        """Counterexample: credential revision is not consulted by this API."""
        store = _MutableSessionStore(self.session.record)
        self.assertIsNotNone(resolve_opaque_session(
            token=self.session.delivery_token, now=NOW, store=store,
        ))
        store.password_revision += 1
        self.assertIsNotNone(resolve_opaque_session(
            token=self.session.delivery_token, now=NOW, store=store,
        ))
        self.assertEqual(store.calls, 2)

    def test_in04_bad_token_and_expiry_are_rejected(self):
        store = _MutableSessionStore(self.session.record)
        self.assertIsNone(resolve_opaque_session(
            token=b"X" * 32, now=NOW, store=store,
        ))
        self.assertIsNone(resolve_opaque_session(
            token=self.session.delivery_token,
            now=NOW + timedelta(minutes=15), store=store,
        ))

    def test_in03_in04_no_implicit_database_network_or_file_access(self):
        consumer = _AtomicSequentialConsumption()
        store = _MutableSessionStore(self.session.record)
        with patch("builtins.open") as files, patch("socket.socket") as net:
            with patch("psycopg.connect") as pg:
                self.assertTrue(self._verify(consumer))
                self.assertIsNotNone(resolve_opaque_session(
                    token=self.session.delivery_token, now=NOW, store=store,
                ))
        files.assert_not_called()
        net.assert_not_called()
        pg.assert_not_called()


if __name__ == "__main__":
    unittest.main()
