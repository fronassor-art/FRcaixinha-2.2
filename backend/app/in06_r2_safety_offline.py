"""Negativas determinísticas IN06-R2 com referências sintéticas e sem efeitos.

Este contrato recebe apenas fatos candidatos de uma futura camada protegida.
Não consulta contas, autentica, verifica provas, decide titularidade, concede
papéis, recupera sessões ou persiste casos. Razões internas não são respostas
públicas; a camada de API futura precisará de controle antienumeração próprio.
"""

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4


class OfflineSafetyError(ValueError):
    """Erro estável sem dados pessoais ou referências fornecidas."""


class Disposition(str, Enum):
    DENY = "DENY"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True, slots=True, repr=False)
class OfflineAssessment:
    disposition: Disposition
    reason: str
    grants_access: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if (type(self.disposition) is not Disposition
                or type(self.reason) is not str
                or self.reason not in _REASONS):
            raise OfflineSafetyError("OFFLINE_ASSESSMENT_DENIED") from None

    def __repr__(self) -> str:
        return "OfflineAssessment(<redacted>)"


_REASONS = frozenset({
    "INSUFFICIENT_CIVIL_EVIDENCE", "CONTACT_OR_OWNERSHIP_RISK",
    "LEGAL_REPRESENTATION_UNVERIFIED",
    "LEGAL_REPRESENTATION_REVIEW_REQUIRED", "POSITIVE_POLICY_PENDING",
    "TENANT_MISMATCH", "REPRESENTATION_NOT_PROVEN", "SOURCE_UNVERIFIABLE",
    "MANDATE_INVALID", "ACT_POWER_NOT_PROVEN", "FINANCIAL_GATE_REQUIRED",
    "PJ_AUTHORITY_PENDING", "PJ_POSITIVE_POLICY_PENDING", "SELF_REVIEW", "REVIEW_CONFLICT",
    "REVIEW_AUTHORITY_PENDING", "REVIEW_POSITIVE_POLICY_PENDING",
    "REVIEW_EVIDENCE_DISPUTE",
    "RECOVERY_TOKEN_INVALID", "RECOVERY_CHANNEL_UNSAFE",
    "RECOVERY_METHOD_UNAPPROVED", "RECOVERY_AUTHORITY_PENDING",
    "RECOVERY_POSITIVE_POLICY_PENDING",
})


def _result(disposition: Disposition, reason: str) -> OfflineAssessment:
    return OfflineAssessment(disposition, reason)


def _valid_uuid(value: object) -> bool:
    if type(value) is not UUID:
        return False
    try:
        number = value.int
    except AttributeError:
        return False
    return type(number) is int and 0 < number < (1 << 128)


def _valid_bools(obj: object, fields: tuple[str, ...]) -> bool:
    return all(type(getattr(obj, name)) is bool for name in fields)


@dataclass(frozen=True, slots=True, repr=False)
class NeutralClaimReceipt:
    case_ref: UUID
    state: str = field(default="RECEIVED_UNVERIFIED_OFFLINE", init=False)

    def __post_init__(self) -> None:
        if not _valid_uuid(self.case_ref):
            raise OfflineSafetyError("NEUTRAL_INTAKE_DENIED") from None

    def __repr__(self) -> str:
        return "NeutralClaimReceipt(<redacted>)"


def receive_neutral_claim(
    *, party_type: str, allegation_kind: str | None = None,
    evidence_refs: tuple[UUID, ...] = (), **unsupported: object,
) -> NeutralClaimReceipt:
    """Recebe metadados candidatos; não procura conta nem atesta reclamante.

    O UUID retornado é uma referência efêmera, não um caso armazenado. A mesma
    resposta serve para alegações sobre pessoas existentes ou inexistentes.
    """
    if (unsupported or type(party_type) is not str
            or party_type not in {"PF", "PJ"}
            or type(allegation_kind) is not str
            or allegation_kind not in {
                "IDENTITY_MISUSE", "ACCOUNT_TAKEOVER", "CONTACT_COMPROMISE",
                "REPRESENTATION_DISPUTE", "OTHER",
            }
            or type(evidence_refs) is not tuple
            or len(evidence_refs) > 16
            or not all(_valid_uuid(value) for value in evidence_refs)
            or len(set(evidence_refs)) != len(evidence_refs)):
        raise OfflineSafetyError("NEUTRAL_INTAKE_DENIED") from None
    return NeutralClaimReceipt(uuid4())


@dataclass(frozen=True, slots=True, repr=False)
class PfClaimFacts:
    cpf_formal: bool = False
    email_confirmed: bool = False
    phone_possession: bool = False
    evidence_kinds: frozenset[str] = frozenset()
    contact_compromised: bool = False
    contact_recently_changed: bool = False
    ownership_conflict: bool = False
    legal_rep_required: bool = False
    special_case: str = "NONE"
    legal_rep_evidence_present: bool = False

    def __post_init__(self) -> None:
        if (not _valid_bools(self, _PF_BOOL_FIELDS)
                or type(self.special_case) is not str
                or self.special_case not in {
                    "NONE", "MINOR", "INCAPACITY", "DEATH",
                }
                or type(self.evidence_kinds) is not frozenset
                or not all(type(value) is str and value in _PF_EVIDENCE_KINDS
                           for value in self.evidence_kinds)):
            raise OfflineSafetyError("PF_FACTS_DENIED") from None

    def __repr__(self) -> str:
        return "PfClaimFacts(<redacted>)"


_PF_BOOL_FIELDS = tuple(
    name for name in PfClaimFacts.__dataclass_fields__
    if name not in {"evidence_kinds", "special_case"}
)
_PF_EVIDENCE_KINDS = frozenset({
    "CPF_FORMAL", "EMAIL_CONFIRMATION", "PHONE_POSSESSION", "SELFIE",
    "SCREENSHOT", "OTP", "CIVIL_DOCUMENT", "LEGAL_REPRESENTATION",
})


def assess_pf_claim(facts: PfClaimFacts) -> OfflineAssessment:
    """Nunca converte contato, CPF formal, selfie, print ou OTP em prova civil."""
    if type(facts) is not PfClaimFacts:
        raise OfflineSafetyError("PF_FACTS_DENIED") from None
    if (facts.contact_compromised or facts.contact_recently_changed
            or facts.ownership_conflict):
        return _result(Disposition.ESCALATE, "CONTACT_OR_OWNERSHIP_RISK")
    if facts.special_case != "NONE":
        return _result(Disposition.ESCALATE,
                       "LEGAL_REPRESENTATION_REVIEW_REQUIRED")
    if facts.legal_rep_required and not facts.legal_rep_evidence_present:
        return _result(Disposition.DENY, "LEGAL_REPRESENTATION_UNVERIFIED")
    if "CIVIL_DOCUMENT" not in facts.evidence_kinds:
        return _result(Disposition.DENY, "INSUFFICIENT_CIVIL_EVIDENCE")
    return _result(Disposition.ESCALATE, "POSITIVE_POLICY_PENDING")


@dataclass(frozen=True, slots=True, repr=False)
class PjActFacts:
    tenant_ref: UUID
    requested_tenant_ref: UUID
    cnpj_formal: bool = False
    qsa_record_present: bool = False
    representative_evidence_present: bool = False
    source_verifiable: bool = False
    act_power_evidence_present: bool = False
    mandate_expired: bool = False
    mandate_revoked: bool = False
    power_scope_matches: bool = False
    financial_act: bool = False
    authority_defined: bool = False

    def __post_init__(self) -> None:
        if (not _valid_uuid(self.tenant_ref)
                or not _valid_uuid(self.requested_tenant_ref)
                or not _valid_bools(self, _PJ_BOOL_FIELDS)):
            raise OfflineSafetyError("PJ_FACTS_DENIED") from None

    def __repr__(self) -> str:
        return "PjActFacts(<redacted>)"


_PJ_BOOL_FIELDS = tuple(
    name for name in PjActFacts.__dataclass_fields__
    if name not in {"tenant_ref", "requested_tenant_ref"}
)


def assess_pj_act(facts: PjActFacts) -> OfflineAssessment:
    """CNPJ/QSA são apenas pistas; não bastam para poderes por ato."""
    if type(facts) is not PjActFacts:
        raise OfflineSafetyError("PJ_FACTS_DENIED") from None
    if facts.tenant_ref != facts.requested_tenant_ref:
        return _result(Disposition.DENY, "TENANT_MISMATCH")
    if facts.mandate_expired or facts.mandate_revoked:
        return _result(Disposition.DENY, "MANDATE_INVALID")
    if not facts.representative_evidence_present:
        return _result(Disposition.DENY, "REPRESENTATION_NOT_PROVEN")
    if not facts.source_verifiable:
        return _result(Disposition.DENY, "SOURCE_UNVERIFIABLE")
    if not facts.act_power_evidence_present or not facts.power_scope_matches:
        return _result(Disposition.DENY, "ACT_POWER_NOT_PROVEN")
    if facts.financial_act:
        return _result(Disposition.ESCALATE, "FINANCIAL_GATE_REQUIRED")
    if not facts.authority_defined:
        return _result(Disposition.ESCALATE, "PJ_AUTHORITY_PENDING")
    return _result(Disposition.ESCALATE, "PJ_POSITIVE_POLICY_PENDING")


@dataclass(frozen=True, slots=True, repr=False)
class ReviewFacts:
    case_ref: UUID
    claimant_ref: UUID
    reviewer_ref: UUID
    reviewer_interested: bool = False
    authority_defined: bool = False
    competing_claims: bool = False
    evidence_contradictory: bool = False
    appeal_required: bool = False
    appeal_available: bool = False

    def __post_init__(self) -> None:
        if (not all(_valid_uuid(value) for value in (
                self.case_ref, self.claimant_ref, self.reviewer_ref))
                or self.case_ref == self.claimant_ref
                or self.case_ref == self.reviewer_ref
                or not _valid_bools(self, _REVIEW_BOOL_FIELDS)):
            raise OfflineSafetyError("REVIEW_FACTS_DENIED") from None

    def __repr__(self) -> str:
        return "ReviewFacts(<redacted>)"


_REVIEW_BOOL_FIELDS = tuple(
    name for name in ReviewFacts.__dataclass_fields__
    if name not in {"case_ref", "claimant_ref", "reviewer_ref"}
)


def assess_review(facts: ReviewFacts) -> OfflineAssessment:
    """Avalia impedimentos; nenhum candidato ganha poder de decidir."""
    if type(facts) is not ReviewFacts:
        raise OfflineSafetyError("REVIEW_FACTS_DENIED") from None
    if facts.claimant_ref == facts.reviewer_ref:
        return _result(Disposition.DENY, "SELF_REVIEW")
    if facts.reviewer_interested:
        return _result(Disposition.DENY, "REVIEW_CONFLICT")
    if (facts.competing_claims or facts.evidence_contradictory
            or (facts.appeal_required and not facts.appeal_available)):
        return _result(Disposition.ESCALATE, "REVIEW_EVIDENCE_DISPUTE")
    if not facts.authority_defined:
        return _result(Disposition.ESCALATE, "REVIEW_AUTHORITY_PENDING")
    return _result(Disposition.ESCALATE, "REVIEW_POSITIVE_POLICY_PENDING")


@dataclass(frozen=True, slots=True, repr=False)
class RecoveryFacts:
    token_present: bool = False
    token_expired: bool = False
    token_consumed: bool = False
    token_replayed: bool = False
    only_channel_compromised: bool = False
    channel_recently_changed: bool = False
    independent_method_approved: bool = False
    exceptional_authority_defined: bool = False

    def __post_init__(self) -> None:
        if not _valid_bools(self, _RECOVERY_FIELDS):
            raise OfflineSafetyError("RECOVERY_FACTS_DENIED") from None

    def __repr__(self) -> str:
        return "RecoveryFacts(<redacted>)"


_RECOVERY_FIELDS = tuple(RecoveryFacts.__dataclass_fields__)


def assess_recovery(facts: RecoveryFacts) -> OfflineAssessment:
    """Consome estado candidato, nunca o token, a sessão ou o banco."""
    if type(facts) is not RecoveryFacts:
        raise OfflineSafetyError("RECOVERY_FACTS_DENIED") from None
    if (not facts.token_present or facts.token_expired
            or facts.token_consumed or facts.token_replayed):
        return _result(Disposition.DENY, "RECOVERY_TOKEN_INVALID")
    if facts.only_channel_compromised or facts.channel_recently_changed:
        return _result(Disposition.DENY, "RECOVERY_CHANNEL_UNSAFE")
    if not facts.independent_method_approved:
        return _result(Disposition.DENY, "RECOVERY_METHOD_UNAPPROVED")
    if not facts.exceptional_authority_defined:
        return _result(Disposition.ESCALATE, "RECOVERY_AUTHORITY_PENDING")
    return _result(Disposition.ESCALATE, "RECOVERY_POSITIVE_POLICY_PENDING")
