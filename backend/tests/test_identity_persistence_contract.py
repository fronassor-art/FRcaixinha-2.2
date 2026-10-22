"""Intenções de escrita sintéticas; nenhuma porta SQL é implementada."""

import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID

from app.crypto_documents import DocumentCrypto, DocumentKeySet
from app.identity_persistence_contract import (
    PersistenceContractError, PreliminaryRegistrationStore,
    prepare_preliminary_write_intent,
)
from app.identity_registration_offline import prepare_pf_registration
from app.offline_credentials import SessionFacts
from app.trusted_auth_subject import VerifiedAuthAssertion, resolve_auth_subject


NOW = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)
SUBJECT = UUID("00000000-0000-4000-8000-000000000401")
OTHER_SUBJECT = UUID("00000000-0000-4000-8000-000000000402")
IDENTITY = UUID("00000000-0000-4000-8000-000000000403")
PARTY = UUID("00000000-0000-4000-8000-000000000404")
OTHER_IDENTITY = UUID("00000000-0000-4000-8000-000000000405")
OTHER_PARTY = UUID("00000000-0000-4000-8000-000000000406")


class EmptyProbe:
    def cpf_exists(self, _value): return False
    def email_exists(self, _value): return False
    def cnpj_exists(self, _value): return False


class FixedVerifier:
    def __init__(self, fact): self.fact = fact
    def verify_assertion(self, _assertion): return self.fact


class PersistenceContractTests(unittest.TestCase):
    def setUp(self):
        crypto = DocumentCrypto({"synthetic": DocumentKeySet(
            "synthetic", b"E" * 32, b"L" * 32)},
            current_key_id="synthetic")
        self.crypto = crypto
        self.registration = self.registration_for(IDENTITY, PARTY)
        self.auth = self.auth_for(SUBJECT)

    def registration_for(self, identity_id, party_id):
        return prepare_pf_registration(
            name="Pessoa Exemplo", cpf="529.982.247-25",
            email="person@example.com", phone="(91) 91234-5678",
            identity_id=identity_id, party_id=party_id,
            crypto=self.crypto, probe=EmptyProbe())

    def auth_for(self, subject):
        session = SessionFacts(subject, NOW - timedelta(minutes=1),
                               NOW + timedelta(minutes=14), None)
        fact = VerifiedAuthAssertion("local", "frcaixinha-api", subject, session)
        return resolve_auth_subject(
            assertion=b"synthetic-opaque-assertion-only",
            verifier=FixedVerifier(fact), expected_issuer="local", now=NOW)

    def intent(self, **changes):
        args = dict(registration=self.registration, auth=self.auth,
                    idempotency_key=b"synthetic-request-key-001", now=NOW)
        args.update(changes)
        return prepare_preliminary_write_intent(**args)

    def test_preliminary_contract_is_not_a_sql_adapter(self):
        intent = self.intent()
        self.assertEqual(intent.auth_subject, f"local:{SUBJECT}")
        self.assertEqual(len(intent.idempotency_digest), 32)
        self.assertEqual(intent.registration.identity.status, "PENDENTE")
        self.assertEqual(intent.registration.party.status, "PRELIMINAR")
        self.assertNotIn("person@example.com", repr(intent))
        self.assertNotIn("52998224725", repr(intent))
        self.assertFalse(hasattr(PreliminaryRegistrationStore, "connect"))

    def test_idempotency_is_stable_and_scoped_to_authenticated_subject(self):
        first = self.intent()
        self.assertEqual(first.idempotency_digest, self.intent().idempotency_digest)
        other = self.intent(auth=self.auth_for(OTHER_SUBJECT))
        self.assertNotEqual(first.idempotency_digest, other.idempotency_digest)
        with_new_key = self.intent(idempotency_key=b"synthetic-request-key-002")
        self.assertNotEqual(first.idempotency_digest,
                            with_new_key.idempotency_digest)

    def test_expired_revoked_or_forged_auth_fails_closed(self):
        for auth in (
            replace(self.auth, value="local:52998224725"),
            replace(self.auth, session=replace(self.auth.session, revoked_at=NOW)),
            replace(self.auth, session=replace(self.auth.session, expires_at=NOW)),
            None,
        ):
            with self.subTest(auth_type=type(auth).__name__):
                with self.assertRaisesRegex(PersistenceContractError,
                                            "^WRITE_INTENT_INVALID$"):
                    self.intent(auth=auth)

    def test_invalid_key_or_registration_fails_closed(self):
        for changed in (dict(idempotency_key=b"short"),
                        dict(idempotency_key="client-header"),
                        dict(registration=None)):
            with self.subTest(changed=list(changed)):
                with self.assertRaises(PersistenceContractError):
                    self.intent(**changed)

    def test_simultaneous_candidates_expose_need_for_database_unique(self):
        second = self.registration_for(OTHER_IDENTITY, OTHER_PARTY)
        self.assertEqual(self.registration.identity.cpf_lookup_hmac,
                         second.identity.cpf_lookup_hmac)
        self.assertNotEqual(self.registration.identity.cpf_ciphertext,
                            second.identity.cpf_ciphertext)
        self.assertEqual(second.party.pf_user_id, OTHER_IDENTITY)
        # EmptyProbe cannot arbitrate two candidates. PostgreSQL UNIQUE and one
        # transaction are a separate, expressly authorized integration gate.

    def test_no_implicit_file_network_or_database_access(self):
        with patch("builtins.open") as file, patch("socket.socket") as network:
            with patch("psycopg.connect") as db:
                self.intent()
        file.assert_not_called()
        network.assert_not_called()
        db.assert_not_called()

    def test_unicode_issuer_uses_controlled_error(self):
        issuer = "lócal"
        auth = replace(self.auth, issuer=issuer,
                       value=f"{issuer}:{SUBJECT}")
        with self.assertRaisesRegex(PersistenceContractError,
                                    "^WRITE_INTENT_INVALID$"):
            self.intent(auth=auth)

    def test_issuer_beyond_policy_length_uses_controlled_error(self):
        issuer = "a" * 33
        auth = replace(self.auth, issuer=issuer,
                       value=f"{issuer}:{SUBJECT}")
        with self.assertRaisesRegex(PersistenceContractError,
                                    "^WRITE_INTENT_INVALID$"):
            self.intent(auth=auth)

    def test_issuer_beyond_digest_length_uses_controlled_error(self):
        issuer = "a" * 65536
        auth = replace(self.auth, issuer=issuer,
                       value=f"{issuer}:{SUBJECT}")
        with self.assertRaisesRegex(PersistenceContractError,
                                    "^WRITE_INTENT_INVALID$"):
            self.intent(auth=auth)
