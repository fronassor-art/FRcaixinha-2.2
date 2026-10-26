"""Prepara uma contestação IN-06 offline, sem decidir ou persistir o caso.

Os UUIDs são apenas referências opacas. A existência, origem e suficiência da
prova, a identidade do requerente e a autoridade revisora não são verificadas
aqui. Nenhum resultado deste módulo concede acesso ou altera titularidade.
"""

from dataclasses import dataclass, field
from typing import Literal
from uuid import UUID


class ClaimPreparationError(ValueError):
    """Erro estável, sem identificadores, documentos ou contatos."""


@dataclass(frozen=True, slots=True, repr=False)
class ClaimReviewIntent:
    claim_id: UUID
    claimant_ref: UUID
    reserved_identity_id: UUID
    party_type: Literal["PF", "PJ"]
    party_id: UUID | None
    evidence_refs: tuple[UUID, ...]
    state: str = field(default="PREPARED_OFFLINE_UNREVIEWED", init=False)

    def __post_init__(self) -> None:
        _validate_claim_fields(self)

    def __repr__(self) -> str:
        return "ClaimReviewIntent(<redacted>)"


def _valid_uuid(value: object) -> bool:
    if type(value) is not UUID:
        return False
    try:
        uuid_int = value.int
    except AttributeError:
        return False
    return type(uuid_int) is int and 0 < uuid_int < (1 << 128)


def _validate_claim_fields(intent: ClaimReviewIntent) -> None:
    ids = (intent.claim_id, intent.claimant_ref, intent.reserved_identity_id)
    party_type = intent.party_type
    party_id = intent.party_id
    evidence_refs = intent.evidence_refs
    if (type(party_type) is not str
            or party_type not in {"PF", "PJ"}
            or not all(_valid_uuid(value) for value in ids)
            or len(set(ids)) != len(ids)
            or (party_id is not None and not _valid_uuid(party_id))
            or (party_type == "PJ" and party_id is None)
            or (party_id is not None and party_id in ids)
            or type(evidence_refs) is not tuple
            or not 1 <= len(evidence_refs) <= 32
            or not all(_valid_uuid(value) for value in evidence_refs)):
        raise ClaimPreparationError("CLAIM_PREPARATION_DENIED") from None

    used = set(ids)
    if party_id is not None:
        used.add(party_id)
    if (len(set(evidence_refs)) != len(evidence_refs)
            or any(value in used for value in evidence_refs)):
        raise ClaimPreparationError("CLAIM_PREPARATION_DENIED") from None


def prepare_claim_review(
    *, claim_id: UUID, claimant_ref: UUID, reserved_identity_id: UUID,
    party_type: Literal["PF", "PJ"], party_id: UUID | None,
    evidence_refs: tuple[UUID, ...], **unsupported: object,
) -> ClaimReviewIntent:
    """Valida forma para triagem futura; nunca confirma titular ou representante.

    ``claimant_ref`` identifica apenas a solicitação, não uma sessão ou pessoa
    autenticada. ``evidence_refs`` aponta para registros protegidos futuros;
    sua presença não atesta autenticidade nem suficiência jurídica.
    """
    if unsupported:
        raise ClaimPreparationError("CLAIM_PREPARATION_DENIED") from None
    return ClaimReviewIntent(
        claim_id, claimant_ref, reserved_identity_id,
        party_type, party_id, evidence_refs,
    )
