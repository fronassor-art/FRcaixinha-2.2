"""Preparação local de dados PF/PJ para etapas futuras de cadastro.

Não cria usuários, não autentica, não registra aceite, não concede acesso,
não verifica titularidade e não lê/escreve no banco ou na rede.

Dados sensíveis persistidos exigirão cifra/HMAC e controles de identidade
implementados separadamente. A saída NÃO é um cadastro aprovado.
"""

from dataclasses import dataclass
import re
import unicodedata
from typing import Literal

from app.document_validation import normalize_cnpj, normalize_cpf

_EMAIL_LOCAL = re.compile(r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~.-]+", re.ASCII)
_EMAIL_DOMAIN_LABEL = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", re.ASCII
)
_PHONE_INPUT = re.compile(
    r"(?:[0-9]{10,11}|\([0-9]{2}\) [0-9]{4,5}-[0-9]{4}|"
    r"[0-9]{2} [0-9]{4,5}-[0-9]{4})",
    re.ASCII,
)
# Códigos nacionais brasileiros (Anatel); não confundir DDD válido com posse.
_VALID_DDDS = frozenset(
    (*range(11, 20), 21, 22, 24, 27, 28, 31, 32, 33, 34, 35, 37, 38,
     *range(41, 50), 51, 53, 54, 55, *range(61, 70),
     71, 73, 74, 75, 77, 79, *range(81, 90), *range(91, 100))
)


class IdentityDraftError(ValueError):
    """Código de erro estável, sem valores pessoais na mensagem."""


@dataclass(frozen=True, slots=True, repr=False)
class PersonDraft:
    name: str
    cpf: str
    email: str
    phone: str


@dataclass(frozen=True, slots=True, repr=False)
class ContractingPartyDraft:
    party_type: Literal["PF", "PJ"]
    legal_name: str
    person: PersonDraft
    cnpj: str | None


def _normalize_name(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    # Rejeita controles (inclusive quebra de linha), caracteres invisíveis
    # e caracteres de formatação antes de normalizar espaços.
    if any(unicodedata.category(char).startswith("C") for char in value):
        return None
    result = " ".join(unicodedata.normalize("NFC", value).split())
    words = result.split(" ")
    if not result or len(result) > 200:
        return None
    if not all(any(char.isalpha() for char in word) for word in words):
        return None
    return result


def normalize_email(value: object) -> str | None:
    """Sintaxe conservadora para endereço ASCII; não confirma propriedade."""
    if not isinstance(value, str) or len(value) > 254:
        return None
    if value.count("@") != 1:
        return None
    local, domain = value.split("@")
    if not 1 <= len(local) <= 64 or _EMAIL_LOCAL.fullmatch(local) is None:
        return None
    if local.startswith(".") or local.endswith(".") or ".." in local:
        return None
    if not domain or len(domain) > 253:
        return None
    labels = domain.split(".")
    if len(labels) < 2 or len(labels[-1]) < 2:
        return None
    if any(_EMAIL_DOMAIN_LABEL.fullmatch(part) is None for part in labels):
        return None
    return f"{local.lower()}@{domain.lower()}"


def normalize_phone(value: object) -> str | None:
    """DDD brasileiro + 8 dígitos fixos ou 9 móveis, sem código de país."""
    if not isinstance(value, str) or _PHONE_INPUT.fullmatch(value) is None:
        return None
    digits = value.translate(str.maketrans("", "", " ()-"))
    if int(digits[:2]) not in _VALID_DDDS:
        return None
    subscriber = digits[2:]
    if len(subscriber) == 9 and subscriber.startswith("9"):
        return digits
    if len(subscriber) == 8 and subscriber[0] in "2345":
        return digits
    return None


def prepare_person_draft(
    *, name: object, cpf: object, email: object, phone: object
) -> PersonDraft:
    """Verifica campos formais; não valida email/telefone por confirmação."""
    checked_name = _normalize_name(name)
    if checked_name is None:
        raise IdentityDraftError("NOME_INVALIDO")
    checked_cpf = normalize_cpf(cpf)
    if checked_cpf is None:
        raise IdentityDraftError("CPF_INVALIDO")
    checked_email = normalize_email(email)
    if checked_email is None:
        raise IdentityDraftError("EMAIL_INVALIDO")
    checked_phone = normalize_phone(phone)
    if checked_phone is None:
        raise IdentityDraftError("TELEFONE_INVALIDO")
    return PersonDraft(checked_name, checked_cpf, checked_email, checked_phone)


def prepare_pf_contractor_draft(
    *, name: object, cpf: object, email: object, phone: object
) -> ContractingPartyDraft:
    person = prepare_person_draft(name=name, cpf=cpf, email=email, phone=phone)
    # CPF deve residir em UserIdentity, não no tax_id da pessoa física.
    return ContractingPartyDraft("PF", person.name, person, None)


def prepare_pj_contractor_draft(
    *,
    legal_name: object,
    cnpj: object,
    representative_name: object,
    representative_cpf: object,
    representative_email: object,
    representative_phone: object,
) -> ContractingPartyDraft:
    """Prepara rascunho sem habilitar contratação PJ ou representação."""
    checked_name = _normalize_name(legal_name)
    if checked_name is None:
        raise IdentityDraftError("RAZAO_SOCIAL_INVALIDA")
    checked_cnpj = normalize_cnpj(cnpj)
    if checked_cnpj is None:
        raise IdentityDraftError("CNPJ_INVALIDO")
    person = prepare_person_draft(
        name=representative_name,
        cpf=representative_cpf,
        email=representative_email,
        phone=representative_phone,
    )
    # Uma PJ não está apta sem declaração e verificação de representação,
    # autenticação, aceite e demais requisitos contratuais.
    return ContractingPartyDraft("PJ", checked_name, person, checked_cnpj)
