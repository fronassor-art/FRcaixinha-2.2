"""Validação sintática e de dígitos verificadores de CPF/CNPJ.

Não consulta a Receita Federal, não comprova titularidade ou existência,
não persiste documentos, não realiza criptografia nem cria credenciais.

CNPJ alfanumérico: 12 caracteres ASCII [A-Z0-9] e 2 DVs numéricos.
Referência oficial (Serpro/RFB):
https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/documentos-tecnicos/cnpj/manual-dv-cnpj.pdf
"""

import re

_CPF_INPUT = re.compile(
    r"(?:[0-9]{11}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2})",
    re.ASCII,
)
_CNPJ_INPUT = re.compile(
    r"(?:[A-Za-z0-9]{12}[0-9]{2}|"
    r"[A-Za-z0-9]{2}\.[A-Za-z0-9]{3}\.[A-Za-z0-9]{3}/"
    r"[A-Za-z0-9]{4}-[0-9]{2})",
    re.ASCII,
)


def _parse(value: object, pattern: re.Pattern[str]) -> str | None:
    """Aceita exclusivamente formato compacto ou máscara completa usual."""
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        return None
    return value.replace(".", "").replace("/", "").replace("-", "").upper()


def _cpf_digit(numbers: str, weight: int) -> int:
    total = sum(int(char) * multiplier for char, multiplier in zip(
        numbers, range(weight, 1, -1)
    ))
    remainder = (total * 10) % 11
    return 0 if remainder == 10 else remainder


def normalize_cpf(value: object) -> str | None:
    """Retorna CPF válido (11 dígitos ASCII), ou None; nunca apenas formata."""
    cpf = _parse(value, _CPF_INPUT)
    if cpf is None or len(set(cpf)) == 1:
        return None
    first = _cpf_digit(cpf[:9], 10)
    second = _cpf_digit(cpf[:9] + str(first), 11)
    return cpf if cpf[-2:] == f"{first}{second}" else None


def _cnpj_digit(characters: str) -> int:
    """Módulo 11; valor ASCII - 48, pesos da direita 2..9 cíclicos."""
    total = sum(
        (ord(char) - 48) * (2 + index % 8)
        for index, char in enumerate(reversed(characters))
    )
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def normalize_cnpj(value: object) -> str | None:
    """Retorna CNPJ válido (12 alfanuméricos + 2 dígitos), ou None."""
    cnpj = _parse(value, _CNPJ_INPUT)
    if cnpj is None:
        return None
    base = cnpj[:12]
    # Impede placeholders numéricos repetitivos, sem vedar letras válidas.
    if base.isdigit() and len(set(base)) == 1:
        return None
    first = _cnpj_digit(base)
    second = _cnpj_digit(base + str(first))
    return cnpj if cnpj[-2:] == f"{first}{second}" else None


def is_valid_cpf(value: object) -> bool:
    """Verifica apenas sintaxe e dígitos verificadores do CPF."""
    return normalize_cpf(value) is not None


def is_valid_cnpj(value: object) -> bool:
    """Verifica apenas sintaxe e dígitos verificadores do CNPJ."""
    return normalize_cnpj(value) is not None
