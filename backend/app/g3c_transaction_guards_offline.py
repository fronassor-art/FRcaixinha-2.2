"""Guardas offline para o futuro adaptador PostgreSQL de identidade G3-C.

AVISO: este módulo é puro, sem SQL, sem sincronização de concorrência e sem
autorização para F2P4/login/e-mail. Chamadas operacionais DEVEM carregar fatos
atuais sob isolamento e locks revistos numa única transação no servidor.
"""
import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from app.identity_draft import normalize_email


class TransactionGateError(ValueError):
    """Erro genérico; não revela CPF, e-mail, IDs ou hashes."""


@dataclass(frozen=True, slots=True, repr=False)
class CompletedAttempt:
    origin_digest: bytes
    attempt_digest: bytes
    fingerprint: bytes
    identity_id: UUID
    party_id: UUID
    state: str
    created_at: datetime
    expires_at: datetime


@dataclass(frozen=True, slots=True, repr=False)
class PartyLink:
    id: UUID
    party_type: str
    pf_user_id: UUID | None
    representative_user_id: UUID | None
    initial_registration_identity_id: UUID | None


@dataclass(frozen=True, slots=True, repr=False)
class EmailFacts:
    challenge_identity_id: UUID
    identity_id: UUID
    snapshot_email: str
    current_email: str
    identity_status: str
    purpose: str
    issued_at: datetime
    expires_at: datetime
    consumed_at: datetime | None = None
    revoked_at: datetime | None = None


@dataclass(frozen=True, slots=True, repr=False)
class SessionFacts:
    session_identity_id: UUID
    identity_id: UUID
    identity_status: str
    credential_status: str
    email_verified_at: datetime | None
    credential_updated_at: datetime
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None


def _uuid(value: object) -> bool:
    return isinstance(value, UUID) and value.int != 0


def _aware(value: object) -> bool:
    try:
        return isinstance(value, datetime) and value.tzinfo is not None and value.utcoffset() is not None
    except Exception:
        return False


def _digest(value: object) -> bool:
    return type(value) is bytes and len(value) == 32


def _window(start: object, end: object, now: object, maximum: timedelta) -> bool:
    try:
        return (_aware(start) and _aware(end) and _aware(now)
                and start <= now < end and timedelta(0) < end - start <= maximum)
    except Exception:
        return False


def verified_replay_ids(
    stored: CompletedAttempt, party: PartyLink, *,
    origin_digest: bytes, attempt_digest: bytes,
    request_fingerprint: bytes, now: datetime,
) -> tuple[UUID, UUID]:
    """Releitura de evidências COMPLETED, nunca autorização por lookup negativo.

    Fatos devem vir do mesmo snapshot PostgreSQL protegido por lock/isolamento
    do futuro adaptador. Não substitui UNIQUE, SQL transacional ou anti-abuso.
    """
    try:
        valid = (
            type(stored) is CompletedAttempt
            and type(party) is PartyLink
            and stored.state == "COMPLETED"
            and _uuid(stored.identity_id) and _uuid(stored.party_id)
            and stored.identity_id != stored.party_id
            and _uuid(party.id) and stored.party_id == party.id
            and _uuid(party.initial_registration_identity_id)
            and party.initial_registration_identity_id == stored.identity_id
            and all(_digest(x) for x in (
                stored.origin_digest, stored.attempt_digest, stored.fingerprint,
                origin_digest, attempt_digest, request_fingerprint))
            and hmac.compare_digest(stored.origin_digest, origin_digest)
            and hmac.compare_digest(stored.attempt_digest, attempt_digest)
            and hmac.compare_digest(stored.fingerprint, request_fingerprint)
            and _window(stored.created_at, stored.expires_at, now,
                        timedelta(minutes=15))
            and ((party.party_type == "PF"
                  and party.pf_user_id == stored.identity_id
                  and party.representative_user_id is None)
                 or (party.party_type == "PJ"
                     and _uuid(party.representative_user_id)
                     and party.pf_user_id is None))
        )
        if valid:
            return stored.identity_id, stored.party_id
    except Exception:
        pass
    raise TransactionGateError("REPLAY_DENIED")


def email_challenge_eligible(facts: EmailFacts, *, now: datetime) -> bool:
    """Pré-condições de consumo, não consome, não muda identidade e não envia e-mail.

    Token/digest precisam ser comprovados no adaptador e consumo deve ser UPDATE
    condicional, atômico, baseado no relógio do PostgreSQL.
    """
    try:
        return (
            type(facts) is EmailFacts
            and _uuid(facts.challenge_identity_id)
            and facts.challenge_identity_id == facts.identity_id
            and facts.identity_status == "PENDENTE"
            and facts.purpose == "INITIAL_EMAIL"
            and type(facts.snapshot_email) is str
            and type(facts.current_email) is str
            and bool(facts.snapshot_email)
            and facts.snapshot_email == facts.current_email
            and normalize_email(facts.snapshot_email) == facts.snapshot_email
            and facts.consumed_at is None and facts.revoked_at is None
            and _window(facts.issued_at, facts.expires_at, now,
                        timedelta(minutes=10))
        )
    except Exception:
        return False


def session_current_with_server_facts(
    facts: SessionFacts, *, now: datetime,
) -> bool:
    """Exige estado atual confiável; não emite token, RoleGrant ou autorização.

    O adaptador futuro deve reler sessão+identidade+credencial no servidor A
    CADA uso, com sincronização para mudanças concorrentes. Não aceitar fatos
    enviados pelo Flutter ou cache sem invalidação.
    """
    try:
        return (
            type(facts) is SessionFacts
            and _uuid(facts.session_identity_id)
            and facts.session_identity_id == facts.identity_id
            and facts.identity_status == "ATIVA"
            and facts.credential_status == "ACTIVE"
            and facts.revoked_at is None
            and _aware(facts.email_verified_at)
            and _aware(facts.credential_updated_at)
            and facts.email_verified_at <= facts.issued_at
            and facts.credential_updated_at <= facts.issued_at
            and _window(facts.issued_at, facts.expires_at, now,
                        timedelta(minutes=15))
        )
    except Exception:
        return False
