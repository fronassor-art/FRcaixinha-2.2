"""G3-C.4 / IN-01, IN-02: limites verificaveis dos contratos OFFLINE.

Nao usa banco, rede, API, criacao de schema, migration ou concorrencia real.
Os ensaios transacionais em PostgreSQL permanecem um gate separado.
"""

import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.crypto_documents import DocumentCrypto, DocumentKeySet
from app.identity_persistence_contract import (
    PersistenceContractError, prepare_preliminary_write_intent,
)
from app.identity_registration_offline import (
    prepare_pf_registration, prepare_pj_registration,
)
from app.initial_registration_bootstrap import (
    PreparedInitialRegistration, prepare_or_replay_initial_registration,
)
from app.offline_credentials import SessionFacts
from app.trusted_auth_subject import (
    VerifiedAuthAssertion, resolve_auth_subject,
)


NOW = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)


class _EmptyProbe:
    def cpf_exists(self, _value): return False
    def email_exists(self, _value): return False
    def cnpj_exists(self, _value): return False


class _Verifier:
    def __init__(self, assertion):
        self.assertion = assertion

    def verify_assertion(self, _value):
        return self.assertion


class _Ids:
    def __init__(self, start):
        self.next = start

    def new_uuid(self):
        result = UUID(int=self.next)
        self.next += 1
        return result


class _Entropy:
    def generate(self, length):
        return b"C" * length


class _NoCompletedAttempts:
    def find_completed(self, _origin, _attempt):
        return None


class G3C4In01In02OfflineTests(unittest.TestCase):
    def setUp(self):
        self.crypto = DocumentCrypto(
            {"synthetic": DocumentKeySet("synthetic", b"E" * 32, b"L" * 32)},
            current_key_id="synthetic",
        )
        subject = UUID(int=401)
        session = SessionFacts(
            subject, NOW - timedelta(minutes=1),
            NOW + timedelta(minutes=14), None,
        )
        verified = VerifiedAuthAssertion(
            "local", "frcaixinha-api", subject, session,
        )
        self.auth = resolve_auth_subject(
            assertion=b"synthetic-opaque-assertion-only",
            verifier=_Verifier(verified), expected_issuer="local", now=NOW,
        )

    def _write_intent(self, registration):
        return prepare_preliminary_write_intent(
            registration=registration, auth=self.auth,
            idempotency_key=b"synthetic-request-key-001", now=NOW,
        )

    def _pf(self):
        return prepare_pf_registration(
            name="Pessoa Exemplo", cpf="529.982.247-25",
            email="person@example.com", phone="(91) 91234-5678",
            identity_id=UUID(int=501), party_id=UUID(int=502),
            crypto=self.crypto, probe=_EmptyProbe(),
        )

    def _pj(self):
        return prepare_pj_registration(
            legal_name="Empresa Exemplo Ltda",
            cnpj="12.ABC.345/01DE-35",
            representative_name="Pessoa Exemplo",
            representative_cpf="529.982.247-25",
            representative_email="person@example.com",
            representative_phone="(91) 91234-5678",
            identity_id=UUID(int=601), party_id=UUID(int=602),
            crypto=self.crypto, probe=_EmptyProbe(),
        )

    def test_in01_pf_identity_link_matches_or_rejects_before_write(self):
        valid = self._pf()
        self.assertEqual(valid.party.pf_user_id, valid.identity.id)
        self.assertIsNone(valid.party.representative_user_id)
        self.assertEqual(self._write_intent(valid).registration, valid)

        wrong_party = replace(
            valid.party, pf_user_id=UUID(int=999),
        )
        with self.assertRaisesRegex(
            PersistenceContractError, "^WRITE_INTENT_INVALID$"
        ):
            self._write_intent(replace(valid, party=wrong_party))

    def test_in01_pj_representative_link_matches_or_rejects_before_write(self):
        valid = self._pj()
        self.assertEqual(valid.party.representative_user_id, valid.identity.id)
        self.assertIsNone(valid.party.pf_user_id)
        self.assertEqual(self._write_intent(valid).registration, valid)

        wrong_party = replace(
            valid.party, representative_user_id=UUID(int=999),
        )
        with self.assertRaisesRegex(
            PersistenceContractError, "^WRITE_INTENT_INVALID$"
        ):
            self._write_intent(replace(valid, party=wrong_party))

    def test_in02_two_negative_lookups_only_create_competing_candidates(self):
        """Same digest + different provisional IDs proves a missing SQL arbiter.

        A PASS here must never be reported as a test of PostgreSQL concurrency.
        """
        common = dict(
            party_type="PF", name="Pessoa Exemplo", cpf="529.982.247-25",
            email="person@example.com", phone="(91) 91234-5678",
            password="synthetic-long-password",
            crypto=self.crypto, probe=_EmptyProbe(),
            challenge_entropy=_Entropy(), origin_scope=b"O" * 32,
            attempt_key=b"attempt-key-synthetic-0001",
            fingerprint_key=b"F" * 32, now=NOW,
        )
        first = prepare_or_replay_initial_registration(
            **common, ids=_Ids(701), lookup=_NoCompletedAttempts(),
        )
        second = prepare_or_replay_initial_registration(
            **common, ids=_Ids(801), lookup=_NoCompletedAttempts(),
        )
        self.assertIsInstance(first, PreparedInitialRegistration)
        self.assertIsInstance(second, PreparedInitialRegistration)
        left, right = first.intent, second.intent
        self.assertEqual(left.origin_digest, right.origin_digest)
        self.assertEqual(left.attempt_digest, right.attempt_digest)
        self.assertEqual(left.request_fingerprint, right.request_fingerprint)
        self.assertNotEqual(
            left.registration.identity.id, right.registration.identity.id,
        )
        self.assertNotEqual(
            left.registration.party.id, right.registration.party.id,
        )
        self.assertFalse(hasattr(first, "committed"))
        self.assertFalse(hasattr(second, "committed"))


if __name__ == "__main__":
    unittest.main()
