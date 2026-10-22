"""Proposta offline de sessão opaca, sem login, storage ou emissor público."""

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol
from uuid import UUID

from app.offline_credentials import PasswordCheck, SessionFacts, session_is_current


_DOMAIN = b"FRCAIXINHA/OPAQUE-SESSION/v1"
_LIFETIME = timedelta(minutes=15)


class OpaqueSessionError(ValueError):
    """Erro estável sem token, digest ou dados pessoais."""


class SessionEntropy(Protocol):
    def generate(self, length: int) -> bytes: ...


class SessionIdentifiers(Protocol):
    def new_uuid(self) -> UUID: ...


class SessionStore(Protocol):
    """Porta futura: consultar revogação atual a cada operação."""

    def find_by_verifier(self, verifier_sha256: bytes) -> "OpaqueSessionRecord | None": ...


@dataclass(frozen=True, slots=True, repr=False)
class OpaqueSessionRecord:
    id: UUID
    identity_id: UUID
    verifier_sha256: bytes
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None

    def __repr__(self) -> str:
        return "OpaqueSessionRecord(<redacted>)"


@dataclass(frozen=True, slots=True, repr=False)
class PreparedOpaqueSession:
    record: OpaqueSessionRecord
    delivery_token: bytes

    def __repr__(self) -> str:
        return "PreparedOpaqueSession(<redacted>)"


def _valid_uuid(value: object) -> bool:
    return isinstance(value, UUID) and value.int != 0


def _aware(value: object) -> bool:
    return (isinstance(value, datetime) and value.tzinfo is not None
            and value.utcoffset() is not None)


def _verifier(token: bytes) -> bytes:
    return hashlib.sha256(_DOMAIN + token).digest()


def prepare_opaque_session(
    *, identity_id: UUID, identity_status: str,
    email_verified_at: datetime | None, password_check: PasswordCheck,
    now: datetime, entropy: SessionEntropy,
    ids: SessionIdentifiers,
) -> PreparedOpaqueSession:
    """Prepara token efêmero só após elegibilidade informada pelo servidor."""
    if (not _valid_uuid(identity_id) or identity_status != "ATIVA"
            or not _aware(email_verified_at) or not _aware(now)
            or email_verified_at > now
            or not isinstance(password_check, PasswordCheck)
            or password_check.valid is not True):
        raise OpaqueSessionError("SESSION_PREPARATION_BLOCKED")
    try:
        session_id = ids.new_uuid()
        token = entropy.generate(32)
        if (not _valid_uuid(session_id) or session_id == identity_id
                or not isinstance(token, bytes) or len(token) != 32):
            raise ValueError
        record = OpaqueSessionRecord(
            session_id, identity_id, _verifier(token), now,
            now + _LIFETIME,
        )
        return PreparedOpaqueSession(record, token)
    except Exception:
        raise OpaqueSessionError("SESSION_PREPARATION_BLOCKED") from None


def resolve_opaque_session(
    *, token: bytes, now: datetime, store: SessionStore,
) -> SessionFacts | None:
    """Reconsulta o storage confiável a cada uso; jamais aceita claims cliente."""
    if not isinstance(token, bytes) or len(token) != 32 or not _aware(now):
        return None
    try:
        expected = _verifier(token)
        record = store.find_by_verifier(expected)
        if (not isinstance(record, OpaqueSessionRecord)
                or not _valid_uuid(record.id)
                or not _valid_uuid(record.identity_id)
                or not isinstance(record.verifier_sha256, bytes)
                or len(record.verifier_sha256) != 32
                or not hmac.compare_digest(record.verifier_sha256, expected)):
            return None
        facts = SessionFacts(record.identity_id, record.issued_at,
                             record.expires_at, record.revoked_at)
        return facts if session_is_current(
            facts, subject_id=record.identity_id, now=now,
        ) else None
    except Exception:
        return None
