"""Sessões sintéticas: emissão preparatória e consulta de revogação por uso."""

import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID

from app.offline_credentials import PasswordCheck
from app.opaque_sessions_offline import (
    OpaqueSessionError, prepare_opaque_session, resolve_opaque_session,
)


NOW = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)
IDENTITY = UUID("00000000-0000-4000-8000-000000000701")
SESSION = UUID("00000000-0000-4000-8000-000000000702")


class Ids:
    def new_uuid(self): return SESSION


class Entropy:
    def generate(self, length): return b"T" * length


class Store:
    def __init__(self, record):
        self.record = record
        self.calls = 0

    def find_by_verifier(self, _digest):
        self.calls += 1
        return self.record


class OpaqueSessionsOfflineTests(unittest.TestCase):
    def setUp(self):
        self.args = dict(
            identity_id=IDENTITY, identity_status="ATIVA",
            email_verified_at=NOW - timedelta(minutes=1),
            password_check=PasswordCheck(True, False), now=NOW,
            entropy=Entropy(), ids=Ids(),
        )

    def prepare(self, **changes):
        args = dict(self.args)
        args.update(changes)
        return prepare_opaque_session(**args)

    def test_token_is_opaque_hash_only_and_bounded(self):
        prepared = self.prepare()
        self.assertEqual(len(prepared.delivery_token), 32)
        self.assertEqual(len(prepared.record.verifier_sha256), 32)
        self.assertNotEqual(prepared.delivery_token,
                            prepared.record.verifier_sha256)
        self.assertEqual(prepared.record.expires_at - prepared.record.issued_at,
                         timedelta(minutes=15))
        self.assertNotIn("TTTT", repr(prepared))
        self.assertNotIn("TTTT", repr(prepared.record))

    def test_each_use_reloads_revocation_and_rejects_replay_after_revoke(self):
        prepared = self.prepare()
        store = Store(prepared.record)
        self.assertIsNotNone(resolve_opaque_session(
            token=prepared.delivery_token, now=NOW, store=store))
        store.record = replace(prepared.record, revoked_at=NOW)
        self.assertIsNone(resolve_opaque_session(
            token=prepared.delivery_token, now=NOW, store=store))
        self.assertEqual(store.calls, 2)

    def test_expired_tampered_or_unknown_token_rejected(self):
        prepared = self.prepare()
        store = Store(prepared.record)
        for token, when in (
            (prepared.delivery_token, NOW + timedelta(minutes=15)),
            (b"X" * 32, NOW), (b"short", NOW),
        ):
            with self.subTest(when=when, token_length=len(token)):
                self.assertIsNone(resolve_opaque_session(
                    token=token, now=when, store=store))

    def test_pending_identity_unverified_contact_or_bad_password_blocked(self):
        for change in (
            dict(identity_status="PENDENTE"),
            dict(email_verified_at=None),
            dict(password_check=PasswordCheck(False, False)),
            dict(now=NOW.replace(tzinfo=None)),
        ):
            with self.subTest(change=list(change)):
                with self.assertRaisesRegex(OpaqueSessionError,
                                            "^SESSION_PREPARATION_BLOCKED$"):
                    self.prepare(**change)

    def test_entropy_and_store_errors_fail_closed(self):
        class BrokenEntropy:
            def generate(self, _length): raise RuntimeError("SECRET")

        with self.assertRaises(OpaqueSessionError) as caught:
            self.prepare(entropy=BrokenEntropy())
        self.assertNotIn("SECRET", str(caught.exception))
        prepared = self.prepare()
        class BrokenStore:
            def find_by_verifier(self, _digest): raise RuntimeError("PRIVATE")
        self.assertIsNone(resolve_opaque_session(
            token=prepared.delivery_token, now=NOW, store=BrokenStore()))

    def test_no_implicit_network_file_or_database_access(self):
        with patch("builtins.open") as file, patch("socket.socket") as net:
            with patch("psycopg.connect") as db:
                prepared = self.prepare()
                self.assertIsNotNone(resolve_opaque_session(
                    token=prepared.delivery_token, now=NOW,
                    store=Store(prepared.record)))
        file.assert_not_called()
        net.assert_not_called()
        db.assert_not_called()
