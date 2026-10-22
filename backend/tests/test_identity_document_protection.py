"""Testes offline com documentos ilustrativos e chaves sintéticas."""

import unittest
from dataclasses import FrozenInstanceError, fields
from unittest.mock import patch
from uuid import UUID

from app.crypto_documents import DocumentCrypto, DocumentCryptoError, DocumentKeySet
from app.db.models import ContractingParty, UserIdentity
from app.identity_document_protection import (
    ContractingPartyPjDocumentFields,
    IdentityDocumentProtectionError,
    UserIdentityDocumentFields,
    prepare_pj_contracting_party_cnpj,
    prepare_user_identity_cpf,
)


USER_ID = UUID("00000000-0000-4000-8000-000000000001")
OTHER_ID = UUID("00000000-0000-4000-8000-000000000002")
PARTY_ID = UUID("00000000-0000-4000-8000-000000000003")


class IdentityDocumentProtectionTests(unittest.TestCase):
    def setUp(self) -> None:
        # Material exclusivamente sintético: nenhuma chave operacional.
        keys = {"test-key": DocumentKeySet(
            "test-key", b"E" * 32, b"H" * 32,
        )}
        self.crypto = DocumentCrypto(keys, current_key_id="test-key")

    def test_cpf_masked_and_canonical_prepare_identical_lookup(self) -> None:
        masked = prepare_user_identity_cpf(
            cpf="529.982.247-25", record_id=USER_ID, crypto=self.crypto,
        )
        canonical = prepare_user_identity_cpf(
            cpf="52998224725", record_id=USER_ID, crypto=self.crypto,
        )
        self.assertEqual(masked.cpf_lookup_hmac, canonical.cpf_lookup_hmac)
        self.assertEqual(len(masked.cpf_lookup_hmac), 32)
        self.assertEqual(
            self.crypto.decrypt(
                masked.cpf_ciphertext, kind="CPF", entity="user_identity",
                field="cpf", record_id=str(USER_ID),
            ),
            "52998224725",
        )

    def test_cpf_with_leading_zero_is_preserved(self) -> None:
        prepared = prepare_user_identity_cpf(
            cpf="042.236.650-14", record_id=USER_ID, crypto=self.crypto,
        )
        self.assertEqual(
            self.crypto.decrypt(
                prepared.cpf_ciphertext, kind="CPF", entity="user_identity",
                field="cpf", record_id=str(USER_ID),
            ),
            "04223665014",
        )

    def test_numeric_and_alphanumeric_pj_cnpj(self) -> None:
        cases = (
            ("11.222.333/0001-81", "11222333000181"),
            ("12.abc.345/01de-35", "12ABC34501DE35"),
        )
        for supplied, expected in cases:
            with self.subTest(document=expected):
                prepared = prepare_pj_contracting_party_cnpj(
                    cnpj=supplied, record_id=PARTY_ID, crypto=self.crypto,
                )
                self.assertEqual(
                    self.crypto.decrypt(
                        prepared.tax_id_ciphertext, kind="CNPJ",
                        entity="contracting_party", field="tax_id",
                        record_id=str(PARTY_ID),
                    ),
                    expected,
                )
                self.assertEqual(
                    prepared.tax_id_lookup_hmac,
                    self.crypto.lookup_hmac(expected, kind="CNPJ"),
                )

    def test_field_names_and_types_match_existing_models(self) -> None:
        user_fields = {field.name for field in fields(UserIdentityDocumentFields)}
        party_fields = {field.name for field in fields(ContractingPartyPjDocumentFields)}
        self.assertEqual(user_fields, {"cpf_ciphertext", "cpf_lookup_hmac"})
        self.assertEqual(party_fields, {"tax_id_ciphertext", "tax_id_lookup_hmac"})
        self.assertLessEqual(user_fields, set(UserIdentity.__table__.c.keys()))
        self.assertLessEqual(party_fields, set(ContractingParty.__table__.c.keys()))
        user = prepare_user_identity_cpf(
            cpf="52998224725", record_id=USER_ID, crypto=self.crypto,
        )
        party = prepare_pj_contracting_party_cnpj(
            cnpj="11222333000181", record_id=PARTY_ID, crypto=self.crypto,
        )
        for result in (user, party):
            for field in fields(result):
                value = getattr(result, field.name)
                self.assertIsInstance(value, bytes)
                self.assertTrue(value)
            with self.assertRaises(FrozenInstanceError):
                setattr(result, fields(result)[0].name, b"replacement")

    def test_only_ciphertext_and_hmac_leave_the_adapter(self) -> None:
        for supplied, prepare, key in (
            ("529.982.247-25", prepare_user_identity_cpf, "cpf"),
            ("11.222.333/0001-81", prepare_pj_contracting_party_cnpj, "cnpj"),
        ):
            record_id = USER_ID if key == "cpf" else PARTY_ID
            result = prepare(**{
                key: supplied, "record_id": record_id, "crypto": self.crypto,
            })
            for field in fields(result):
                value = getattr(result, field.name)
                self.assertNotIn(supplied.encode("ascii"), value)
                self.assertNotIn(supplied.translate(
                    str.maketrans("", "", "./-")).encode("ascii"), value)
            self.assertNotIn(supplied, repr(result))
            self.assertNotIn("b'", repr(result))

    def test_decryption_requires_correct_uuid_entity_and_field(self) -> None:
        result = prepare_user_identity_cpf(
            cpf="52998224725", record_id=USER_ID, crypto=self.crypto,
        )
        context = {"kind": "CPF", "entity": "user_identity", "field": "cpf",
                   "record_id": str(USER_ID)}
        for changed in (
            {"record_id": str(OTHER_ID)},
            {"entity": "contracting_party"},
            {"field": "tax_id"},
        ):
            with self.subTest(changed=changed):
                with self.assertRaisesRegex(
                    DocumentCryptoError, "DOCUMENT_AUTHENTICATION_FAILED"
                ):
                    self.crypto.decrypt(
                        result.cpf_ciphertext, **{**context, **changed},
                    )

    def test_record_id_must_be_supplied_uuid_before_encryption(self) -> None:
        for record_id in (None, str(USER_ID), UUID(int=0), 1):
            with self.subTest(kind=type(record_id).__name__):
                with patch.object(self.crypto, "encrypt") as encrypt:
                    with self.assertRaisesRegex(
                        IdentityDocumentProtectionError, "RECORD_ID_INVALID"
                    ):
                        prepare_user_identity_cpf(
                            cpf="52998224725", record_id=record_id,
                            crypto=self.crypto,
                        )
                    encrypt.assert_not_called()

    def test_invalid_documents_fail_before_encryption_without_pii(self) -> None:
        cases = (
            (prepare_user_identity_cpf, "cpf", "529.982.247-26", "CPF_INVALIDO"),
            (prepare_pj_contracting_party_cnpj, "cnpj", "11.222.333/0001-82", "CNPJ_INVALIDO"),
            (prepare_pj_contracting_party_cnpj, "cnpj", "529.982.247-25", "CNPJ_INVALIDO"),
        )
        for prepare, keyword, supplied, code in cases:
            with self.subTest(code=code, supplied=supplied):
                with patch.object(self.crypto, "encrypt") as encrypt:
                    with patch.object(self.crypto, "lookup_hmac") as lookup:
                        with self.assertRaises(IdentityDocumentProtectionError) as caught:
                            prepare(**{
                                keyword: supplied, "record_id": USER_ID,
                                "crypto": self.crypto,
                            })
                        self.assertEqual(str(caught.exception), code)
                        self.assertNotIn(supplied, repr(caught.exception))
                        encrypt.assert_not_called()
                        lookup.assert_not_called()

    def test_global_hmac_does_not_use_record_id_or_tenant(self) -> None:
        first = prepare_user_identity_cpf(
            cpf="52998224725", record_id=USER_ID, crypto=self.crypto,
        )
        second = prepare_user_identity_cpf(
            cpf="52998224725", record_id=OTHER_ID, crypto=self.crypto,
        )
        party = prepare_pj_contracting_party_cnpj(
            cnpj="11222333000181", record_id=PARTY_ID,
            crypto=self.crypto,
        )
        self.assertEqual(first.cpf_lookup_hmac, second.cpf_lookup_hmac)
        self.assertNotEqual(first.cpf_lookup_hmac, party.tax_id_lookup_hmac)
        self.assertEqual(
            first.cpf_lookup_hmac,
            self.crypto.lookup_hmac("52998224725", kind="CPF"),
        )
        self.assertEqual(
            party.tax_id_lookup_hmac,
            self.crypto.lookup_hmac("11222333000181", kind="CNPJ"),
        )

    def test_rejects_missing_document_crypto_without_exposing_material(self) -> None:
        with self.assertRaisesRegex(
            IdentityDocumentProtectionError, "DOCUMENT_CRYPTO_INVALID"
        ):
            prepare_user_identity_cpf(
                cpf="52998224725", record_id=USER_ID, crypto=None,
            )
        result = prepare_user_identity_cpf(
            cpf="52998224725", record_id=USER_ID, crypto=self.crypto,
        )
        self.assertNotIn("52998224725", repr(result))
        self.assertNotIn("EEEE", repr(result))
        self.assertNotIn("HHHH", repr(result))

    def test_preparation_does_not_use_file_network_or_database(self) -> None:
        with patch("builtins.open") as open_file:
            with patch("socket.socket") as socket:
                with patch("psycopg.connect") as connect:
                    with patch("sqlalchemy.create_engine") as engine:
                        prepare_user_identity_cpf(
                            cpf="52998224725", record_id=USER_ID,
                            crypto=self.crypto,
                        )
                        prepare_pj_contracting_party_cnpj(
                            cnpj="11222333000181", record_id=PARTY_ID,
                            crypto=self.crypto,
                        )
        open_file.assert_not_called()
        socket.assert_not_called()
        connect.assert_not_called()
        engine.assert_not_called()


if __name__ == "__main__":
    unittest.main()
