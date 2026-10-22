"""Prepara cadastro PF/PJ protegido, sem persistência ou ativação.

O resultado não é inserível diretamente: a origem confiável de auth_subject,
a prova de contato e a transação de unicidade dependem de aprovação futura.
"""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.crypto_documents import DocumentCrypto
from app.identity_document_protection import (
    prepare_pj_contracting_party_cnpj,
    prepare_user_identity_cpf,
)
from app.identity_draft import (
    prepare_pf_contractor_draft,
    prepare_pj_contractor_draft,
)


class RegistrationPreparationError(ValueError):
    """Código estável, sem documento, contato ou material criptográfico."""


class ConflictProbe(Protocol):
    """Porta de leitura injetada; não substitui UNIQUE/transação futura."""

    def cpf_exists(self, lookup_hmac: bytes) -> bool: ...
    def email_exists(self, normalized_email: str) -> bool: ...
    def cnpj_exists(self, lookup_hmac: bytes) -> bool: ...


@dataclass(frozen=True, slots=True, repr=False)
class PreparedIdentity:
    id: UUID
    name: str
    cpf_ciphertext: bytes
    cpf_lookup_hmac: bytes
    email: str
    phone: str
    status: str = "PENDENTE"

    def __repr__(self) -> str:
        return "PreparedIdentity(<redacted>)"


@dataclass(frozen=True, slots=True, repr=False)
class PreparedParty:
    id: UUID
    party_type: str
    legal_name: str
    pf_user_id: UUID | None
    representative_user_id: UUID | None
    tax_id_ciphertext: bytes | None
    tax_id_lookup_hmac: bytes | None
    status: str = "PRELIMINAR"

    def __repr__(self) -> str:
        return "PreparedParty(<redacted>)"


@dataclass(frozen=True, slots=True, repr=False)
class PreparedRegistration:
    identity: PreparedIdentity
    party: PreparedParty

    def __repr__(self) -> str:
        return "PreparedRegistration(<redacted>)"


def _context(identity_id: UUID, party_id: UUID, crypto: DocumentCrypto,
             probe: ConflictProbe) -> None:
    if (not isinstance(identity_id, UUID) or identity_id.int == 0
            or not isinstance(party_id, UUID) or party_id.int == 0
            or identity_id == party_id):
        raise RegistrationPreparationError("RECORD_ID_INVALID")
    if not isinstance(crypto, DocumentCrypto):
        raise RegistrationPreparationError("CRYPTO_UNAVAILABLE")
    if probe is None or not all(callable(getattr(probe, name, None)) for name in
                                   ("cpf_exists", "email_exists", "cnpj_exists")):
        raise RegistrationPreparationError("CONFLICT_PROBE_UNAVAILABLE")


def _exists(probe: ConflictProbe, method: str, value: bytes | str) -> bool:
    try:
        found = getattr(probe, method)(value)
    except Exception:
        raise RegistrationPreparationError("CONFLICT_CHECK_FAILED") from None
    if type(found) is not bool:
        raise RegistrationPreparationError("CONFLICT_CHECK_FAILED")
    return found


def _prepare(draft, *, identity_id: UUID, party_id: UUID,
             crypto: DocumentCrypto, probe: ConflictProbe) -> PreparedRegistration:
    _context(identity_id, party_id, crypto, probe)
    try:
        cpf = prepare_user_identity_cpf(
            cpf=draft.person.cpf, record_id=identity_id, crypto=crypto,
        )
        cnpj = (prepare_pj_contracting_party_cnpj(
            cnpj=draft.cnpj, record_id=party_id, crypto=crypto,
        ) if draft.party_type == "PJ" else None)
    except Exception:
        raise RegistrationPreparationError("DOCUMENT_PROTECTION_FAILED") from None

    # Observação offline; a unicidade real exige UNIQUE e uma única transação.
    if _exists(probe, "cpf_exists", cpf.cpf_lookup_hmac):
        raise RegistrationPreparationError("IDENTITY_CONFLICT")
    if _exists(probe, "email_exists", draft.person.email):
        raise RegistrationPreparationError("IDENTITY_CONFLICT")
    if cnpj is not None and _exists(probe, "cnpj_exists", cnpj.tax_id_lookup_hmac):
        raise RegistrationPreparationError("PARTY_CONFLICT")

    identity = PreparedIdentity(
        id=identity_id, name=draft.person.name,
        cpf_ciphertext=cpf.cpf_ciphertext,
        cpf_lookup_hmac=cpf.cpf_lookup_hmac,
        email=draft.person.email, phone=draft.person.phone,
    )
    party = PreparedParty(
        id=party_id, party_type=draft.party_type, legal_name=draft.legal_name,
        pf_user_id=identity_id if draft.party_type == "PF" else None,
        representative_user_id=identity_id if draft.party_type == "PJ" else None,
        tax_id_ciphertext=cnpj.tax_id_ciphertext if cnpj else None,
        tax_id_lookup_hmac=cnpj.tax_id_lookup_hmac if cnpj else None,
    )
    return PreparedRegistration(identity, party)


def prepare_pf_registration(*, name: object, cpf: object, email: object,
                            phone: object, identity_id: UUID, party_id: UUID,
                            crypto: DocumentCrypto,
                            probe: ConflictProbe) -> PreparedRegistration:
    """Prepara PF nova. Identidade já existente exige vínculo verificado futuro."""
    _context(identity_id, party_id, crypto, probe)
    try:
        draft = prepare_pf_contractor_draft(
            name=name, cpf=cpf, email=email, phone=phone,
        )
    except Exception:
        raise RegistrationPreparationError("DRAFT_INVALID") from None
    return _prepare(draft, identity_id=identity_id, party_id=party_id,
                    crypto=crypto, probe=probe)


def prepare_pj_registration(*, legal_name: object, cnpj: object,
                            representative_name: object,
                            representative_cpf: object,
                            representative_email: object,
                            representative_phone: object,
                            identity_id: UUID, party_id: UUID,
                            crypto: DocumentCrypto,
                            probe: ConflictProbe) -> PreparedRegistration:
    """Prepara PJ preliminar; não atesta poderes do representante."""
    _context(identity_id, party_id, crypto, probe)
    try:
        draft = prepare_pj_contractor_draft(
            legal_name=legal_name, cnpj=cnpj,
            representative_name=representative_name,
            representative_cpf=representative_cpf,
            representative_email=representative_email,
            representative_phone=representative_phone,
        )
    except Exception:
        raise RegistrationPreparationError("DRAFT_INVALID") from None
    return _prepare(draft, identity_id=identity_id, party_id=party_id,
                    crypto=crypto, probe=probe)
