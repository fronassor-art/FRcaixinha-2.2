"""Offline password/session tests; no operational account or token is issued."""

import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID

from app.offline_credentials import (
    CredentialError, PasswordDigest, SessionFacts, prepare_password_digest,
    session_is_current, verify_password,
)


SUBJECT = UUID("00000000-0000-4000-8000-000000000101")
OTHER = UUID("00000000-0000-4000-8000-000000000102")
NOW = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)


class OfflineCredentialsTests(unittest.TestCase):
    def test_versioned_scrypt_digest_and_generic_verification(self):
        password = "synthetic test phrase 123!"
        first = prepare_password_digest(password)
        second = prepare_password_digest(password)
        self.assertIsInstance(first, PasswordDigest)
        self.assertTrue(first.encoded.startswith("scrypt$v1$16384$8$1$"))
        self.assertNotEqual(first.encoded, second.encoded)
        self.assertTrue(verify_password(password, first).valid)
        self.assertFalse(verify_password("incorrect test phrase", first).valid)
        self.assertFalse(verify_password(password, None).valid)
        self.assertFalse(verify_password(password, PasswordDigest("broken")).valid)
        self.assertFalse(verify_password(password, first).needs_rehash)
        self.assertNotIn(password, repr(first))

    def test_password_size_and_malformed_digest_fail_closed(self):
        for value in ("short", "x" * 1025, "bad\x00password123", None):
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaisesRegex(CredentialError, "PASSWORD_POLICY_INVALID"):
                    prepare_password_digest(value)
        stored = prepare_password_digest("synthetic test phrase 123!")
        for bad in ("scrypt$v2$16384$8$1$AA==$AA==", stored.encoded + "$extra"):
            self.assertFalse(verify_password("synthetic test phrase 123!", PasswordDigest(bad)).valid)

    def test_session_requires_subject_bounded_lifetime_and_no_revocation(self):
        facts = SessionFacts(SUBJECT, NOW - timedelta(minutes=1),
                             NOW + timedelta(minutes=14), None)
        self.assertTrue(session_is_current(facts, subject_id=SUBJECT, now=NOW))
        self.assertFalse(session_is_current(facts, subject_id=OTHER, now=NOW))
        self.assertFalse(session_is_current(replace(facts, revoked_at=NOW),
                                            subject_id=SUBJECT, now=NOW))
        self.assertFalse(session_is_current(replace(facts, expires_at=NOW),
                                            subject_id=SUBJECT, now=NOW))
        self.assertFalse(session_is_current(replace(facts, expires_at=NOW + timedelta(hours=1)),
                                            subject_id=SUBJECT, now=NOW))
        self.assertFalse(session_is_current(facts, subject_id=SUBJECT,
                                            now=datetime(2026, 10, 22, 12)))

    def test_no_file_network_or_database_access(self):
        with patch("builtins.open") as open_file, patch("socket.socket") as socket:
            with patch("psycopg.connect") as connect, patch("sqlalchemy.create_engine") as engine:
                digest = prepare_password_digest("synthetic test phrase 123!")
                self.assertTrue(verify_password("synthetic test phrase 123!", digest).valid)
        open_file.assert_not_called()
        socket.assert_not_called()
        connect.assert_not_called()
        engine.assert_not_called()


if __name__ == "__main__":
    unittest.main()
