"""Testes sem rede, PostgreSQL, cadastro real ou dados de usuários."""

import unittest

from app.document_validation import (
    is_valid_cnpj,
    is_valid_cpf,
    normalize_cnpj,
    normalize_cpf,
)


class CPFValidationTests(unittest.TestCase):
    def test_valid_unformatted_and_formatted(self) -> None:
        # Vetores públicos ilustrativos, não obtidos do banco do projeto.
        self.assertEqual(normalize_cpf("52998224725"), "52998224725")
        self.assertEqual(normalize_cpf("529.982.247-25"), "52998224725")
        self.assertEqual(normalize_cpf("12345678909"), "12345678909")
        self.assertTrue(is_valid_cpf("529.982.247-25"))

    def test_invalid_check_digits_and_repetitions(self) -> None:
        for number in (
            "52998224726", "529.982.247-20", "12345678900",
            "00000000000", "11111111111", "99999999999",
        ):
            with self.subTest(number=number):
                self.assertIsNone(normalize_cpf(number))
                self.assertFalse(is_valid_cpf(number))

    def test_invalid_format_unicode_and_redaction(self) -> None:
        for number in (
            "", "5299822472", "529982247255",
            "529 982 247 25", "529.982.247/25",
            " 52998224725", "52998224725\n",
            "529.***.247-25", "５２９９８２２４７２５",
            "5299822472٥", "52998224725;DROP",
        ):
            with self.subTest(number=number):
                self.assertFalse(is_valid_cpf(number))

    def test_non_string_inputs_are_rejected(self) -> None:
        for value in (None, 52998224725, b"52998224725", True, [], {}):
            with self.subTest(kind=type(value).__name__):
                self.assertIsNone(normalize_cpf(value))
                self.assertFalse(is_valid_cpf(value))


class CNPJValidationTests(unittest.TestCase):
    def test_numeric_cnpj_retains_legacy_algorithm(self) -> None:
        self.assertEqual(normalize_cnpj("11222333000181"), "11222333000181")
        self.assertEqual(normalize_cnpj("11.222.333/0001-81"), "11222333000181")
        self.assertEqual(normalize_cnpj("12.345.678/0001-95"), "12345678000195")
        self.assertTrue(is_valid_cnpj("11.222.333/0001-81"))

    def test_official_serpro_alphanumeric_example(self) -> None:
        # Manual do DV CNPJ alfanumérico (Serpro/RFB): 12.ABC.345/01DE-35
        self.assertEqual(
            normalize_cnpj("12.ABC.345/01DE-35"),
            "12ABC34501DE35",
        )
        self.assertEqual(
            normalize_cnpj("12.abc.345/01de-35"),
            "12ABC34501DE35",
        )
        self.assertEqual(normalize_cnpj("12abc34501de35"), "12ABC34501DE35")
        self.assertTrue(is_valid_cnpj("12.ABC.345/01DE-35"))

    def test_invalid_check_digits(self) -> None:
        for number in (
            "11.222.333/0001-82", "11222333000180",
            "12.ABC.345/01DE-36", "12ABC34501DE34",
            "00000000000000", "11111111111111",
        ):
            with self.subTest(number=number):
                self.assertIsNone(normalize_cnpj(number))
                self.assertFalse(is_valid_cnpj(number))

    def test_invalid_masks_unicode_and_alphabetic_check_digits(self) -> None:
        for number in (
            "", "12ABC34501DE3", "12ABC34501DE355",
            "12.ABC.345/01DE-X5", "12.ABC.345/01DE-3A",
            "12.ABC.345/01DE35", "12ABC345/01DE-35",
            "12.ABC.345/01DE-35\n", " 12ABC34501DE35",
            "12.ÁBC.345/01DE-35", "１２.ABC.345/01DE-35",
            "12.ABC.345/01DE-3５", "12.***.345/01DE-35",
            "12ABC34501DE35#", "12ABC34501DE35;",
        ):
            with self.subTest(number=number):
                self.assertIsNone(normalize_cnpj(number))
                self.assertFalse(is_valid_cnpj(number))

    def test_non_string_inputs_are_rejected(self) -> None:
        for value in (None, 11222333000181, b"12ABC34501DE35", False, [], {}):
            with self.subTest(kind=type(value).__name__):
                self.assertIsNone(normalize_cnpj(value))
                self.assertFalse(is_valid_cnpj(value))

    def test_valid_syntactic_document_is_not_identity_proof(self) -> None:
        # Resultado não deve ativar conta, conceder papel, enviar Pix ou autenticar.
        # Este módulo apenas retorna representação canônica ou None.
        self.assertIsInstance(normalize_cnpj("12ABC34501DE35"), str)
        self.assertIsInstance(is_valid_cpf("52998224725"), bool)


if __name__ == "__main__":
    unittest.main()
