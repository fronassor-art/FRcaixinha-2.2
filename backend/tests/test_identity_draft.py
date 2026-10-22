"""Testes isolados: nenhuma conexão, serviço pago, DB ou dado do usuário."""

import unittest
from dataclasses import FrozenInstanceError

from app.identity_draft import (
    IdentityDraftError,
    normalize_email,
    normalize_phone,
    prepare_person_draft,
    prepare_pf_contractor_draft,
    prepare_pj_contractor_draft,
)


PERSON = {
    "name": "  José   da Silva ",
    "cpf": "529.982.247-25",
    "email": "TESTE+tag@Example.COM",
    "phone": "(91) 91234-5678",
}


class EmailDraftTests(unittest.TestCase):
    def test_normalizes_conservative_ascii_email(self) -> None:
        self.assertEqual(
            normalize_email("Usuario+TAG@Sub.Example.COM"),
            "usuario+tag@sub.example.com",
        )
        self.assertEqual(
            normalize_email("a_b.c-d@example.com.br"),
            "a_b.c-d@example.com.br",
        )

    def test_rejects_invalid_local_and_domain(self) -> None:
        for value in (
            "", "abc", "@dominio.com", "user@", "a..b@example.com",
            ".a@example.com", "a.@example.com", "a@localhost",
            "a@-example.com", "a@example-.com", "a@example..com",
            "a@example.c", "a@@example.com", "a b@example.com",
            "a@example.com\n", " a@example.com", "á@example.com",
            "a@exámple.com", "a@examp_le.com",
        ):
            with self.subTest(value=value):
                self.assertIsNone(normalize_email(value))

    def test_rejects_oversized_email(self) -> None:
        self.assertIsNone(normalize_email("a" * 65 + "@example.com"))
        self.assertIsNone(normalize_email("a@" + "b" * 64 + ".com"))
        self.assertIsNone(normalize_email("a@" + "x." * 126 + "com"))
        self.assertIsNone(normalize_email("a" * 60 + "@" + "x" * 63 +
                                         "." + "x" * 63 + "." + "x" * 63 +
                                         ".com"))

    def test_email_rejects_non_string(self) -> None:
        for value in (None, b"a@example.com", 123, False, {}, []):
            with self.subTest(kind=type(value).__name__):
                self.assertIsNone(normalize_email(value))


class PhoneDraftTests(unittest.TestCase):
    def test_valid_cell_and_fixed_with_ddd(self) -> None:
        self.assertEqual(normalize_phone("(91) 91234-5678"), "91912345678")
        self.assertEqual(normalize_phone("91 91234-5678"), "91912345678")
        self.assertEqual(normalize_phone("91912345678"), "91912345678")
        self.assertEqual(normalize_phone("(11) 3333-4444"), "1133334444")
        self.assertEqual(normalize_phone("6133334444"), "6133334444")

    def test_rejects_invalid_ddd_and_length(self) -> None:
        for value in (
            "00912345678", "23912345678", "36912345678",
            "9191234567", "919123456789", "(91) 9123-456",
            "919123456", "9991234567",
        ):
            with self.subTest(value=value):
                self.assertIsNone(normalize_phone(value))

    def test_rejects_invalid_national_number_and_non_ascii(self) -> None:
        for value in (
            "91812345678", "91112345678", "9161234567",
            "9191234567", "91 912345678", "+5591912345678",
            "(91)91234-5678", "(91) 91234 5678", "91 91234-5678 ",
            "９１９１２３４５６７８", "91 91234-567٨", "91 91234-5678\n",
        ):
            with self.subTest(value=value):
                self.assertIsNone(normalize_phone(value))

    def test_phone_rejects_non_string(self) -> None:
        for value in (None, 91912345678, b"91912345678", True, [], {}):
            with self.subTest(kind=type(value).__name__):
                self.assertIsNone(normalize_phone(value))


class PersonDraftTests(unittest.TestCase):
    def test_prepares_person_without_state_or_permissions(self) -> None:
        person = prepare_person_draft(**PERSON)
        self.assertEqual(person.name, "José da Silva")
        self.assertEqual(person.cpf, "52998224725")
        self.assertEqual(person.email, "teste+tag@example.com")
        self.assertEqual(person.phone, "91912345678")
        self.assertFalse(hasattr(person, "status"))
        self.assertFalse(hasattr(person, "email_verified_at"))
        self.assertFalse(hasattr(person, "role"))

    def test_canonical_unicode_and_name_length(self) -> None:
        person = prepare_person_draft(**{**PERSON, "name": "Jose\u0301 Silva"})
        self.assertEqual(person.name, "José Silva")
        with self.assertRaisesRegex(IdentityDraftError, "^NOME_INVALIDO$"):
            prepare_person_draft(**{**PERSON, "name": "A" * 201 + " B"})

    def test_single_word_name_not_arbitrarily_forbidden(self) -> None:
        # Exigência de nome completo não autoriza presumir regra de dois termos.
        draft = prepare_person_draft(**{**PERSON, "name": "Maria"})
        self.assertEqual(draft.name, "Maria")

    def test_invalid_names_fail_closed(self) -> None:
        for value in (
            "", "   ", "Maria\nSilva", "Maria\tSilva",
            "Maria\u200b Silva", "12 34", "Maria 123", None, 123,
        ):
            with self.subTest(kind=type(value).__name__, value=value):
                with self.assertRaisesRegex(IdentityDraftError, "^NOME_INVALIDO$"):
                    prepare_person_draft(**{**PERSON, "name": value})

    def test_invalid_person_fields_are_rejected_in_order(self) -> None:
        bad_values = {
            "cpf": ("52998224726", "CPF_INVALIDO"),
            "email": ("a@-example.com", "EMAIL_INVALIDO"),
            "phone": ("00912345678", "TELEFONE_INVALIDO"),
        }
        for field, (invalid, error) in bad_values.items():
            with self.subTest(field=field):
                with self.assertRaisesRegex(IdentityDraftError, "^" + error + "$"):
                    prepare_person_draft(**{**PERSON, field: invalid})

    def test_no_pii_in_repr_or_errors(self) -> None:
        person = prepare_person_draft(**PERSON)
        public_repr = repr(person) + str(person)
        for sensitive in ("52998224725", "91912345678",
                          "teste+tag@example.com", "José da Silva"):
            self.assertNotIn(sensitive, public_repr)
        try:
            prepare_person_draft(**{**PERSON, "cpf": "52998224726"})
        except IdentityDraftError as exc:
            self.assertEqual(str(exc), "CPF_INVALIDO")
            self.assertNotIn("52998224726", str(exc))
        else:
            self.fail("CPF inválido aceito")

    def test_prepared_draft_is_immutable(self) -> None:
        person = prepare_person_draft(**PERSON)
        with self.assertRaises(FrozenInstanceError):
            person.cpf = "00000000000"


class ContractingPartyDraftTests(unittest.TestCase):
    def test_pf_uses_identity_cpf_and_has_no_cnpj(self) -> None:
        draft = prepare_pf_contractor_draft(**PERSON)
        self.assertEqual(draft.party_type, "PF")
        self.assertEqual(draft.legal_name, "José da Silva")
        self.assertEqual(draft.person.cpf, "52998224725")
        self.assertIsNone(draft.cnpj)
        self.assertFalse(hasattr(draft, "status"))
        self.assertFalse(hasattr(draft, "license_active"))

    def test_pj_keeps_representative_separate(self) -> None:
        draft = prepare_pj_contractor_draft(
            legal_name="  Comércio  Modelo Ltda  ",
            cnpj="12.ABC.345/01DE-35",
            representative_name=PERSON["name"],
            representative_cpf=PERSON["cpf"],
            representative_email=PERSON["email"],
            representative_phone=PERSON["phone"],
        )
        self.assertEqual(draft.party_type, "PJ")
        self.assertEqual(draft.legal_name, "Comércio Modelo Ltda")
        self.assertEqual(draft.cnpj, "12ABC34501DE35")
        self.assertEqual(draft.person.cpf, "52998224725")
        self.assertNotEqual(draft.cnpj, draft.person.cpf)
        self.assertFalse(hasattr(draft, "representation_verified_at"))
        self.assertFalse(hasattr(draft, "status"))

    def test_pj_accepts_numeric_cnpj_without_silent_activation(self) -> None:
        draft = prepare_pj_contractor_draft(
            legal_name="Empresa Modelo",
            cnpj="11.222.333/0001-81",
            representative_name=PERSON["name"],
            representative_cpf=PERSON["cpf"],
            representative_email=PERSON["email"],
            representative_phone=PERSON["phone"],
        )
        self.assertEqual(draft.cnpj, "11222333000181")
        self.assertFalse(hasattr(draft, "tenant_id"))

    def test_pj_rejects_invalid_cnpj_and_representative(self) -> None:
        base = dict(
            legal_name="Comércio Modelo Ltda",
            cnpj="12.ABC.345/01DE-35",
            representative_name=PERSON["name"],
            representative_cpf=PERSON["cpf"],
            representative_email=PERSON["email"],
            representative_phone=PERSON["phone"],
        )
        for key, invalid, code in (
            ("legal_name", "", "RAZAO_SOCIAL_INVALIDA"),
            ("cnpj", "12.ABC.345/01DE-36", "CNPJ_INVALIDO"),
            ("representative_cpf", "00000000000", "CPF_INVALIDO"),
            ("representative_email", "sem-arroba", "EMAIL_INVALIDO"),
            ("representative_phone", "00123456789", "TELEFONE_INVALIDO"),
        ):
            with self.subTest(field=key):
                with self.assertRaisesRegex(IdentityDraftError, "^" + code + "$"):
                    prepare_pj_contractor_draft(**{**base, key: invalid})

    def test_contractor_repr_never_exposes_pii(self) -> None:
        draft = prepare_pf_contractor_draft(**PERSON)
        self.assertNotIn("52998224725", repr(draft))
        self.assertNotIn("José", repr(draft))
        self.assertNotIn("91912345678", repr(draft))
        with self.assertRaises(FrozenInstanceError):
            draft.party_type = "PJ"


if __name__ == "__main__":
    unittest.main()
