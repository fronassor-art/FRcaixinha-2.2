"""Desafios sintéticos; nenhuma mensagem é transmitida."""

import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID

from app.email_confirmation_offline import (
    EmailChallengeError, prepare_email_challenge,
    verify_and_consume_email_challenge,
)


NOW = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)
IDENTITY = UUID("00000000-0000-4000-8000-000000000301")
OTHER = UUID("00000000-0000-4000-8000-000000000302")
CHALLENGE = UUID("00000000-0000-4000-8000-000000000303")
EMAIL = "person@example.com"


class SyntheticEntropy:
    def generate(self, length):
        if length != 32:
            raise AssertionError("unexpected length")
        return b"S" * length


class MemoryConsumption:
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


class EmailConfirmationOfflineTests(unittest.TestCase):
    def setUp(self):
        self.prepared = prepare_email_challenge(
            challenge_id=CHALLENGE, identity_id=IDENTITY,
            email="PERSON@Example.COM", now=NOW,
            entropy=SyntheticEntropy())
        self.store = MemoryConsumption()

    def verify(self, **changes):
        args = dict(record=self.prepared.record,
                    candidate=self.prepared.delivery_secret,
                    identity_id=IDENTITY, email=EMAIL,
                    now=NOW + timedelta(minutes=1), consumption=self.store)
        args.update(changes)
        return verify_and_consume_email_challenge(**args)

    def test_hash_only_record_and_one_time_confirmation(self):
        self.assertEqual(self.prepared.record.email, EMAIL)
        self.assertEqual(len(self.prepared.record.verifier_sha256), 32)
        self.assertNotEqual(self.prepared.record.verifier_sha256,
                            self.prepared.delivery_secret)
        self.assertTrue(self.verify())
        self.assertFalse(self.verify())
        self.assertEqual(self.store.calls, 2)

    def test_expiry_revocation_and_future_time_fail_before_consumption(self):
        for changed in (
            dict(now=NOW + timedelta(minutes=10)),
            dict(now=NOW - timedelta(seconds=1)),
            dict(record=replace(self.prepared.record, revoked_at=NOW)),
            dict(record=replace(self.prepared.record,
                                expires_at=NOW + timedelta(hours=1))),
        ):
            with self.subTest(changed=list(changed)):
                self.assertFalse(self.verify(**changed))
        self.assertEqual(self.store.calls, 0)

    def test_wrong_identity_contact_secret_or_purpose_context_fails(self):
        for changed in (dict(identity_id=OTHER),
                        dict(email="other@example.com"),
                        dict(candidate=b"T" * 32),
                        dict(record=replace(self.prepared.record, id=OTHER)),
                        dict(record=replace(self.prepared.record, email="other@example.com"))):
            with self.subTest(changed=list(changed)):
                self.assertFalse(self.verify(**changed))
        self.assertEqual(self.store.calls, 0)

    def test_invalid_entropy_and_context_are_rejected_without_leak(self):
        class BrokenEntropy:
            def generate(self, _length):
                raise RuntimeError("SECRET")

        with self.assertRaises(EmailChallengeError) as caught:
            prepare_email_challenge(
                challenge_id=CHALLENGE, identity_id=IDENTITY,
                email=EMAIL, now=NOW, entropy=BrokenEntropy())
        self.assertEqual(str(caught.exception),
                         "EMAIL_CHALLENGE_PREPARATION_FAILED")
        self.assertIsNone(caught.exception.__cause__)
        for bad in (dict(challenge_id=UUID(int=0)),
                    dict(email="bad"), dict(now=NOW.replace(tzinfo=None))):
            args = dict(challenge_id=CHALLENGE, identity_id=IDENTITY,
                        email=EMAIL, now=NOW, entropy=SyntheticEntropy())
            args.update(bad)
            with self.assertRaises(EmailChallengeError):
                prepare_email_challenge(**args)

    def test_uncertain_storage_response_and_exception_fail_closed(self):
        class BrokenConsumption:
            def consume_once(self, _id, _verifier):
                raise RuntimeError("DATABASE_DETAIL")

        self.assertFalse(self.verify(consumption=BrokenConsumption()))
        with patch.object(self.store, "consume_once", return_value=None):
            self.assertFalse(self.verify())

    def test_secret_email_and_hash_are_redacted_in_repr(self):
        for value in (repr(self.prepared), repr(self.prepared.record)):
            self.assertNotIn(EMAIL, value)
            self.assertNotIn("SSSS", value)
            self.assertNotIn("b'", value)

    def test_no_implicit_file_network_or_database_access(self):
        with patch("builtins.open") as file, patch("socket.socket") as network:
            with patch("psycopg.connect") as db:
                prepared = prepare_email_challenge(
                    challenge_id=CHALLENGE, identity_id=IDENTITY,
                    email=EMAIL, now=NOW, entropy=SyntheticEntropy())
                self.assertTrue(verify_and_consume_email_challenge(
                    record=prepared.record, candidate=prepared.delivery_secret,
                    identity_id=IDENTITY, email=EMAIL, now=NOW,
                    consumption=self.store))
        file.assert_not_called()
        network.assert_not_called()
        db.assert_not_called()
