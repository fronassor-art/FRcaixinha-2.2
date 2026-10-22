"""Cadastro sintético e inteiramente offline; sem identidade ou chave reais."""

import unittest
from dataclasses import FrozenInstanceError, fields, replace
from unittest.mock import patch
from uuid import UUID

from app.crypto_documents import DocumentCrypto, DocumentCryptoError, DocumentKeySet
from app.db.models import ContractingParty, UserIdentity
from app.identity_registration_offline import (
    RegistrationPreparationError,
    prepare_pf_registration,
    prepare_pj_registration,
)


IDENTITY_ID = UUID("00000000-0000-4000-8000-000000000011")
PARTY_ID = UUID("00000000-0000-4000-8000-000000000012")
OTHER_ID = UUID("00000000-0000-4000-8000-000000000013")
PERSON = dict(name="Pessoa Exemplo", cpf="529.982.247-25",
              email="PESSOA@Example.COM", phone="(91) 91234-5678")


class MemoryProbe:
    def __init__(self):
        self.cpfs = set()
        self.emails = set()
        self.cnpjs = set()
        self.calls = []

    def cpf_exists(self, value):
        self.calls.append("cpf")
        return value in self.cpfs

    def email_exists(self, value):
        self.calls.append("email")
        return value in self.emails

    def cnpj_exists(self, value):
        self.calls.append("cnpj")
        return value in self.cnpjs


class RegistrationOfflineTests(unittest.TestCase):
    def setUp(self):
        keys = {"synthetic": DocumentKeySet(
            "synthetic", b"E" * 32, b"H" * 32,
        )}
        self.crypto = DocumentCrypto(keys, current_key_id="synthetic")
        self.probe = MemoryProbe()

    def pf(self, **overrides):
        args = dict(**PERSON, identity_id=IDENTITY_ID, party_id=PARTY_ID,
                    crypto=self.crypto, probe=self.probe)
        args.update(overrides)
        return prepare_pf_registration(**args)

    def pj(self, **overrides):
        args = dict(legal_name="Empresa Exemplo Ltda",
                    cnpj="12.ABC.345/01DE-35",
                    representative_name=PERSON["name"],
                    representative_cpf=PERSON["cpf"],
                    representative_email=PERSON["email"],
                    representative_phone=PERSON["phone"],
                    identity_id=IDENTITY_ID, party_id=PARTY_ID,
                    crypto=self.crypto, probe=self.probe)
        args.update(overrides)
        return prepare_pj_registration(**args)

    def test_pf_preliminary_links_only_global_identity(self):
        result = self.pf()
        self.assertEqual((result.identity.status, result.party.status),
                         ("PENDENTE", "PRELIMINAR"))
        self.assertEqual(result.party.pf_user_id, IDENTITY_ID)
        self.assertIsNone(result.party.representative_user_id)
        self.assertIsNone(result.party.tax_id_ciphertext)
        self.assertIsNone(result.party.tax_id_lookup_hmac)
        self.assertEqual(result.identity.email, "pessoa@example.com")
        self.assertEqual(self.probe.calls, ["cpf", "email"])

    def test_pj_numeric_and_alphanumeric_cnpj_and_representation_pending(self):
        for cnpj, canonical in (("12.ABC.345/01DE-35", "12ABC34501DE35"),
                                ("11.222.333/0001-81", "11222333000181")):
            with self.subTest(cnpj=canonical):
                self.probe.calls.clear()
                result = self.pj(cnpj=cnpj)
                self.assertEqual(result.party.party_type, "PJ")
                self.assertEqual(result.party.representative_user_id, IDENTITY_ID)
                self.assertIsNone(result.party.pf_user_id)
                self.assertEqual(result.party.status, "PRELIMINAR")
                self.assertFalse(hasattr(result.party, "representation_verified_at"))
                self.assertEqual(self.probe.calls, ["cpf", "email", "cnpj"])
                self.assertEqual(self.crypto.decrypt(
                    result.party.tax_id_ciphertext, kind="CNPJ",
                    entity="contracting_party", field="tax_id",
                    record_id=str(PARTY_ID)), canonical)

    def test_model_field_names_and_protected_bytes(self):
        for result in (self.pf(), self.pj()):
            self.assertLessEqual({f.name for f in fields(result.identity)},
                                 set(UserIdentity.__table__.c.keys()))
            self.assertLessEqual({f.name for f in fields(result.party)},
                                 set(ContractingParty.__table__.c.keys()))
            self.assertIsInstance(result.identity.cpf_ciphertext, bytes)
            self.assertEqual(len(result.identity.cpf_lookup_hmac), 32)
            self.assertNotIn(b"52998224725", result.identity.cpf_ciphertext)
            self.assertFalse(hasattr(result.identity, "cpf"))
            self.assertFalse(hasattr(result.party, "cnpj"))
            self.assertFalse(hasattr(result.identity, "auth_subject"))
            with self.assertRaises(FrozenInstanceError):
                result.party.status = "APTO"

    def test_cpf_zero_and_aad_bound_to_uuid(self):
        result = self.pf(cpf="042.236.650-14")
        context = dict(kind="CPF", entity="user_identity", field="cpf",
                       record_id=str(IDENTITY_ID))
        self.assertEqual(self.crypto.decrypt(result.identity.cpf_ciphertext,
                                             **context), "04223665014")
        for changed in (dict(record_id=str(OTHER_ID)),
                        dict(entity="contracting_party"), dict(field="tax_id")):
            with self.assertRaises(DocumentCryptoError):
                self.crypto.decrypt(result.identity.cpf_ciphertext,
                                    **(context | changed))

    def test_lookup_global_deterministic_and_domain_separated(self):
        first = self.pf()
        second = self.pf(identity_id=OTHER_ID)
        self.assertEqual(first.identity.cpf_lookup_hmac,
                         second.identity.cpf_lookup_hmac)
        self.assertNotEqual(first.identity.cpf_lookup_hmac,
                            self.crypto.lookup_hmac("11222333000181", kind="CNPJ"))

    def test_duplicate_cpf_and_email_fail_closed(self):
        first = self.pf()
        self.probe.cpfs.add(first.identity.cpf_lookup_hmac)
        with self.assertRaisesRegex(RegistrationPreparationError,
                                    "^IDENTITY_CONFLICT$"):
            self.pf()
        self.probe.cpfs.clear()
        self.probe.emails.add("pessoa@example.com")
        with self.assertRaisesRegex(RegistrationPreparationError,
                                    "^IDENTITY_CONFLICT$"):
            self.pf()

    def test_existing_representative_requires_verified_linkage(self):
        self.probe.cpfs.add(self.crypto.lookup_hmac("52998224725", kind="CPF"))
        with self.assertRaisesRegex(RegistrationPreparationError,
                                    "^IDENTITY_CONFLICT$"):
            self.pj()

    def test_duplicate_cnpj_fails_closed(self):
        self.probe.cnpjs.add(self.crypto.lookup_hmac("12ABC34501DE35",
                                                      kind="CNPJ"))
        with self.assertRaisesRegex(RegistrationPreparationError,
                                    "^PARTY_CONFLICT$"):
            self.pj()

    def test_invalid_fields_and_ids_rejected_before_crypto(self):
        for changed in (dict(cpf="529.982.247-26"),
                        dict(email="invalid"), dict(phone="00000000000"),
                        dict(name="\n")):
            with self.subTest(changed=list(changed)):
                with patch.object(self.crypto, "encrypt") as encrypt:
                    with self.assertRaisesRegex(RegistrationPreparationError,
                                                "^DRAFT_INVALID$"):
                        self.pf(**changed)
                    encrypt.assert_not_called()
        for bad_id in (None, str(IDENTITY_ID), UUID(int=0), PARTY_ID):
            with self.subTest(bad_id=type(bad_id).__name__):
                with self.assertRaisesRegex(RegistrationPreparationError,
                                            "^RECORD_ID_INVALID$"):
                    self.pf(identity_id=bad_id)

    def test_pj_invalid_cnpj_rejected(self):
        with self.assertRaisesRegex(RegistrationPreparationError,
                                    "^DRAFT_INVALID$"):
            self.pj(cnpj="12.ABC.345/01DE-36")

    def test_missing_or_uncertain_probe_fails_closed(self):
        with self.assertRaisesRegex(RegistrationPreparationError,
                                    "^CONFLICT_PROBE_UNAVAILABLE$"):
            self.pf(probe=None)
        with patch.object(self.probe, "cpf_exists", return_value=None):
            with self.assertRaisesRegex(RegistrationPreparationError,
                                        "^CONFLICT_CHECK_FAILED$"):
                self.pf()
        with patch.object(self.probe, "cpf_exists", side_effect=RuntimeError("PII")):
            with self.assertRaises(RegistrationPreparationError) as caught:
                self.pf()
            self.assertEqual(str(caught.exception), "CONFLICT_CHECK_FAILED")
            self.assertIsNone(caught.exception.__cause__)

    def test_probe_property_exception_is_redacted_before_encryption(self):
        def explode(_self):
            raise RuntimeError("DADO_SENSIVEL")

        for bad_name in ("cpf_exists", "email_exists", "cnpj_exists"):
            with self.subTest(method=bad_name):
                class ExplodingProbe:
                    def cpf_exists(self, _value): return False
                    def email_exists(self, _value): return False
                    def cnpj_exists(self, _value): return False

                setattr(ExplodingProbe, bad_name, property(explode))
                with patch.object(self.crypto, "encrypt") as encrypt:
                    with self.assertRaises(RegistrationPreparationError) as caught:
                        self.pf(probe=ExplodingProbe())
                    self.assertEqual(str(caught.exception),
                                     "CONFLICT_PROBE_UNAVAILABLE")
                    self.assertNotIn("DADO_SENSIVEL", repr(caught.exception))
                    encrypt.assert_not_called()

    def test_crypto_failure_does_not_leak_material(self):
        with patch.object(self.crypto, "encrypt", side_effect=RuntimeError("SECRET")):
            with self.assertRaises(RegistrationPreparationError) as caught:
                self.pf()
        self.assertEqual(str(caught.exception), "DOCUMENT_PROTECTION_FAILED")
        self.assertNotIn("SECRET", repr(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_outputs_and_errors_have_safe_repr(self):
        result = self.pj()
        for sensitive in ("52998224725", "12ABC34501DE35", "pessoa@example.com",
                          "Empresa Exemplo", "b'", "synthetic"):
            self.assertNotIn(sensitive, repr(result))
            self.assertNotIn(sensitive, repr(result.identity))
            self.assertNotIn(sensitive, repr(result.party))
        self.assertFalse(hasattr(result, "tenant_id"))
        self.assertFalse(hasattr(result.party, "role"))
        self.assertFalse(hasattr(result.party, "license"))

    def test_preliminary_status_cannot_be_replaced(self):
        result = self.pj()
        with self.assertRaises(TypeError):
            replace(result.identity, status="ATIVA")
        with self.assertRaises(TypeError):
            replace(result.party, status="APTO")

    def test_no_implicit_database_network_or_files(self):
        with patch("socket.socket", side_effect=AssertionError("network")), \
             patch("builtins.open", side_effect=AssertionError("file")):
            result = self.pj()
            self.assertEqual(result.party.status, "PRELIMINAR")


if __name__ == "__main__":
    unittest.main()
