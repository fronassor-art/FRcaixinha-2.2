"""Bootstrap sintético sem sessão, API ou PostgreSQL."""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID

from app.crypto_documents import DocumentCrypto, DocumentKeySet
from app.initial_registration_bootstrap import (
    InitialRegistrationError, equivalent_initial_attempt,
    prepare_initial_registration,
)
from app.offline_credentials import PasswordDigest, verify_password


NOW = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)
PERSON = dict(name="Pessoa Exemplo", cpf="529.982.247-25",
              email="PESSOA@Example.COM", phone="(91) 91234-5678")


class Ids:
    def __init__(self, start=1):
        self.next = start

    def new_uuid(self):
        value = UUID(int=self.next)
        self.next += 1
        return value


class Entropy:
    def generate(self, length):
        return b"C" * length


class Probe:
    def __init__(self, found=False):
        self.found = found

    def cpf_exists(self, _value): return self.found
    def email_exists(self, _value): return self.found
    def cnpj_exists(self, _value): return self.found


class InitialRegistrationBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.crypto = DocumentCrypto({"synthetic": DocumentKeySet(
            "synthetic", b"E" * 32, b"L" * 32)},
            current_key_id="synthetic")
        self.params = dict(
            party_type="PF", **PERSON, password="synthetic-long-password",
            ids=Ids(), crypto=self.crypto, probe=Probe(),
            challenge_entropy=Entropy(), origin_scope=b"O" * 32,
            attempt_key=b"attempt-key-synthetic-0001",
            fingerprint_key=b"F" * 32, now=NOW,
        )

    def prepare(self, **changes):
        args = dict(self.params)
        args.update(changes)
        return prepare_initial_registration(**args)

    def test_pf_bootstrap_has_no_prior_session_or_privilege(self):
        result = self.prepare()
        intent = result.intent
        self.assertEqual(intent.auth_subject,
                         f"local:{intent.registration.identity.id}")
        self.assertEqual(intent.registration.identity.status, "PENDENTE")
        self.assertEqual(intent.registration.party.status, "PRELIMINAR")
        self.assertEqual(intent.credential_state, "PENDING_EMAIL")
        self.assertIsInstance(intent.password_digest, PasswordDigest)
        self.assertTrue(verify_password("synthetic-long-password",
                                        intent.password_digest).valid)
        self.assertEqual(len(intent.challenge.verifier_sha256), 32)
        self.assertEqual(len(result.delivery_secret), 32)
        self.assertFalse(hasattr(intent, "session"))
        self.assertFalse(hasattr(intent, "role_grant"))
        self.assertFalse(hasattr(intent, "tenant_id"))

    def test_pj_stays_preliminary_without_representation_grant(self):
        result = self.prepare(party_type="PJ",
                              legal_name="Empresa Exemplo Ltda",
                              cnpj="12.ABC.345/01DE-35")
        party = result.intent.registration.party
        self.assertEqual(party.party_type, "PJ")
        self.assertEqual(party.status, "PRELIMINAR")
        self.assertIsNone(party.pf_user_id)
        self.assertEqual(party.representative_user_id,
                         result.intent.registration.identity.id)
        self.assertIsNotNone(party.tax_id_lookup_hmac)
        self.assertFalse(hasattr(party, "representation_verified_at"))

    def test_same_attempt_replays_and_divergent_request_conflicts(self):
        first = self.prepare()
        repeated = self.prepare(ids=Ids(11))
        self.assertTrue(equivalent_initial_attempt(first.intent,
                                                   repeated.intent, now=NOW + timedelta(minutes=1)))
        self.assertNotEqual(first.intent.registration.identity.id,
                            repeated.intent.registration.identity.id)
        changed = self.prepare(ids=Ids(21), name="Outra Pessoa")
        with self.assertRaisesRegex(InitialRegistrationError,
                                    "^INITIAL_ATTEMPT_CONFLICT$"):
            equivalent_initial_attempt(first.intent, changed.intent, now=NOW + timedelta(minutes=1))
        new_attempt = self.prepare(ids=Ids(31),
                                   attempt_key=b"attempt-key-synthetic-0002")
        self.assertFalse(equivalent_initial_attempt(first.intent,
                                                     new_attempt.intent, now=NOW + timedelta(minutes=1)))

    def test_expired_or_malformed_attempt_fails_closed(self):
        from dataclasses import replace
        first = self.prepare()
        repeated = self.prepare(ids=Ids(11))
        with self.assertRaisesRegex(InitialRegistrationError,
                                    "^INITIAL_ATTEMPT_EXPIRED$"):
            equivalent_initial_attempt(
                first.intent, repeated.intent, now=NOW + timedelta(minutes=15))
        malformed = replace(first.intent, attempt_digest=b"short")
        with self.assertRaisesRegex(InitialRegistrationError,
                                    "^INITIAL_REGISTRATION_INVALID$"):
            equivalent_initial_attempt(
                malformed, repeated.intent, now=NOW + timedelta(minutes=1))


    def test_duplicate_probe_blocks_new_identity(self):
        with self.assertRaisesRegex(InitialRegistrationError,
                                    "^INITIAL_REGISTRATION_INVALID$"):
            self.prepare(probe=Probe(found=True))

    def test_bad_password_entropy_ids_or_context_fail_closed(self):
        class BrokenIds:
            def new_uuid(self): raise RuntimeError("PRIVATE_DETAIL")

        class BrokenEntropy:
            def generate(self, _length): raise RuntimeError("PRIVATE_DETAIL")

        for changed in (dict(password="short"), dict(ids=BrokenIds()),
                        dict(challenge_entropy=BrokenEntropy()),
                        dict(origin_scope=b"short"),
                        dict(attempt_key=b"short"),
                        dict(now=NOW.replace(tzinfo=None))):
            with self.subTest(changed=list(changed)):
                with self.assertRaises(InitialRegistrationError) as caught:
                    self.prepare(**changed)
                self.assertNotIn("PRIVATE_DETAIL", str(caught.exception))

    def test_redaction_and_no_implicit_io(self):
        with patch("builtins.open") as file, patch("socket.socket") as net:
            with patch("psycopg.connect") as db:
                result = self.prepare()
        file.assert_not_called()
        net.assert_not_called()
        db.assert_not_called()
        for rendered in (repr(result), repr(result.intent)):
            for secret in ("52998224725", "synthetic-long-password",
                           "pessoa@example.com", "CCCC"):
                self.assertNotIn(secret, rendered)
