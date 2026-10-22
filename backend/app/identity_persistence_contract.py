"""Contrato de escrita preliminar futura; este módulo não contém adaptador SQL.

Uma implementação operacional precisará de transação única, UNIQUE,
idempotência com comparação do pedido e revisão/autorização independentes.
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.identity_registration_offline import (
    PreparedIdentity, PreparedParty, PreparedRegistration,
)
from app.offline_credentials import session_is_current
from app.trusted_auth_subject import ResolvedAuthSubject, issuer_is_valid


class PersistenceContractError(ValueError):
    """Erro genérico sem documento, contato ou chave de idempotência."""


@dataclass(frozen=True, slots=True, repr=False)
class PreliminaryWriteIntent:
    registration: PreparedRegistration
    auth_subject: str
    idempotency_digest: bytes

    def __repr__(self) -> str:
        return "PreliminaryWriteIntent(<redacted>)"


@dataclass(frozen=True, slots=True)
class PreliminaryCommitResult:
    identity_id: UUID
    party_id: UUID
    created: bool


class PreliminaryRegistrationStore(Protocol):
    """Futura porta transacional; nenhuma implementação acompanha o pacote."""

    def commit_once(self, intent: PreliminaryWriteIntent) -> PreliminaryCommitResult: ...


def prepare_preliminary_write_intent(
    *, registration: PreparedRegistration, auth: ResolvedAuthSubject,
    idempotency_key: bytes, now: datetime,
) -> PreliminaryWriteIntent:
    """Vincula pedido ao sujeito autenticado, sem chamar a porta de escrita."""
    if (not isinstance(registration, PreparedRegistration)
            or not isinstance(auth, ResolvedAuthSubject)
            or not isinstance(auth.subject_id, UUID)
            or auth.subject_id.int == 0
            or not issuer_is_valid(auth.issuer)
            or auth.value != f"{auth.issuer}:{auth.subject_id}"
            or not session_is_current(auth.session,
                                      subject_id=auth.subject_id, now=now)
            or not isinstance(idempotency_key, bytes)
            or not 16 <= len(idempotency_key) <= 128):
        raise PersistenceContractError("WRITE_INTENT_INVALID")
    identity, party = registration.identity, registration.party
    if (not isinstance(identity, PreparedIdentity)
            or not isinstance(party, PreparedParty)
            or not isinstance(identity.id, UUID) or identity.id.int == 0
            or not isinstance(party.id, UUID) or party.id.int == 0
            or identity.id == party.id or identity.status != "PENDENTE"
            or party.status != "PRELIMINAR"
            or not isinstance(identity.cpf_ciphertext, bytes)
            or not identity.cpf_ciphertext
            or not isinstance(identity.cpf_lookup_hmac, bytes)
            or len(identity.cpf_lookup_hmac) != 32
            or (party.party_type == "PF" and (
                party.pf_user_id != identity.id
                or party.representative_user_id is not None
                or party.tax_id_ciphertext is not None
                or party.tax_id_lookup_hmac is not None))
            or (party.party_type == "PJ" and (
                party.pf_user_id is not None
                or party.representative_user_id != identity.id
                or not isinstance(party.tax_id_ciphertext, bytes)
                or not party.tax_id_ciphertext
                or not isinstance(party.tax_id_lookup_hmac, bytes)
                or len(party.tax_id_lookup_hmac) != 32))
            or party.party_type not in {"PF", "PJ"}):
        raise PersistenceContractError("WRITE_INTENT_INVALID")
    subject = auth.value.encode("ascii")
    digest = hashlib.sha256(
        b"FRCAIXINHA/REGISTRATION-IDEMPOTENCY/v1"
        + len(subject).to_bytes(2, "big") + subject + idempotency_key
    ).digest()
    return PreliminaryWriteIntent(registration, auth.value, digest)
