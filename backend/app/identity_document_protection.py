"""Prepara campos de documento protegidos, sem persistir identidade ou PJ.

O chamador fornece o UUID definitivo do registro e o DocumentCrypto já
configurado. Nenhuma chave, identidade ou conexão é criada neste módulo.
"""

from dataclasses import dataclass
from uuid import UUID

from app.crypto_documents import DocumentCrypto
from app.document_validation import normalize_cnpj, normalize_cpf


class IdentityDocumentProtectionError(ValueError):
    """Código de erro estável, sem refletir entrada ou material protegido."""


@dataclass(frozen=True, slots=True, repr=False)
class UserIdentityDocumentFields:
    cpf_ciphertext: bytes
    cpf_lookup_hmac: bytes

    def __repr__(self) -> str:
        return "UserIdentityDocumentFields(<redacted>)"


@dataclass(frozen=True, slots=True, repr=False)
class ContractingPartyPjDocumentFields:
    tax_id_ciphertext: bytes
    tax_id_lookup_hmac: bytes

    def __repr__(self) -> str:
        return "ContractingPartyPjDocumentFields(<redacted>)"


def _checked_context(record_id: UUID, crypto: DocumentCrypto) -> str:
    if not isinstance(record_id, UUID) or record_id.int == 0:
        raise IdentityDocumentProtectionError("RECORD_ID_INVALID")
    if not isinstance(crypto, DocumentCrypto):
        raise IdentityDocumentProtectionError("DOCUMENT_CRYPTO_INVALID")
    return str(record_id)


def prepare_user_identity_cpf(
    *, cpf: object, record_id: UUID, crypto: DocumentCrypto
) -> UserIdentityDocumentFields:
    """Prepara somente cpf_ciphertext e cpf_lookup_hmac de UserIdentity."""
    stable_id = _checked_context(record_id, crypto)
    canonical = normalize_cpf(cpf)
    if canonical is None:
        raise IdentityDocumentProtectionError("CPF_INVALIDO")
    return UserIdentityDocumentFields(
        cpf_ciphertext=crypto.encrypt(
            canonical, kind="CPF", entity="user_identity", field="cpf",
            record_id=stable_id,
        ),
        cpf_lookup_hmac=crypto.lookup_hmac(canonical, kind="CPF"),
    )


def prepare_pj_contracting_party_cnpj(
    *, cnpj: object, record_id: UUID, crypto: DocumentCrypto
) -> ContractingPartyPjDocumentFields:
    """Prepara somente tax_id_ciphertext e tax_id_lookup_hmac de PJ."""
    stable_id = _checked_context(record_id, crypto)
    canonical = normalize_cnpj(cnpj)
    if canonical is None:
        raise IdentityDocumentProtectionError("CNPJ_INVALIDO")
    return ContractingPartyPjDocumentFields(
        tax_id_ciphertext=crypto.encrypt(
            canonical, kind="CNPJ", entity="contracting_party",
            field="tax_id", record_id=stable_id,
        ),
        tax_id_lookup_hmac=crypto.lookup_hmac(canonical, kind="CNPJ"),
    )
