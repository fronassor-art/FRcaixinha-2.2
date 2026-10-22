"""Desafio de e-mail offline; não envia mensagens nem persiste segredos.

O verificador futuro deve carregar o registro de fonte confiável e consumir
atomicamente uma única vez. Estes contratos não ativam a identidade.
"""

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol
from uuid import UUID

from app.identity_draft import normalize_email


_LIFETIME = timedelta(minutes=10)
_TOKEN_BYTES = 32
_DOMAIN = b"FRCAIXINHA/EMAIL-CONFIRM/v1"


class EmailChallengeError(ValueError):
    """Erro estável sem e-mail, token ou hash."""


class ChallengeEntropy(Protocol):
    """Fonte criptográfica injetada; o módulo não escolhe nem abre uma fonte."""

    def generate(self, length: int) -> bytes: ...


class ChallengeConsumption(Protocol):
    """Contrato futuro: consumo atômico condicional do registro confiável."""

    def consume_once(self, challenge_id: UUID, verifier: bytes) -> bool: ...


@dataclass(frozen=True, slots=True, repr=False)
class EmailChallengeRecord:
    id: UUID
    identity_id: UUID
    email: str
    issued_at: datetime
    expires_at: datetime
    verifier_sha256: bytes
    revoked_at: datetime | None = None

    def __repr__(self) -> str:
        return "EmailChallengeRecord(<redacted>)"


@dataclass(frozen=True, slots=True, repr=False)
class PreparedEmailChallenge:
    record: EmailChallengeRecord
    delivery_secret: bytes  # Entregar apenas por canal aprovado; nunca persistir.

    def __repr__(self) -> str:
        return "PreparedEmailChallenge(<redacted>)"


def _valid_uuid(value: object) -> bool:
    return isinstance(value, UUID) and value.int != 0


def _aware(value: object) -> bool:
    return (isinstance(value, datetime) and value.tzinfo is not None
            and value.utcoffset() is not None)


def _digest(challenge_id: UUID, identity_id: UUID, email: str,
            secret: bytes) -> bytes:
    email_bytes = email.encode("ascii")
    return hashlib.sha256(
        _DOMAIN + challenge_id.bytes + identity_id.bytes
        + len(email_bytes).to_bytes(2, "big") + email_bytes + secret
    ).digest()


def prepare_email_challenge(
    *, challenge_id: UUID, identity_id: UUID, email: object,
    now: datetime, entropy: ChallengeEntropy,
) -> PreparedEmailChallenge:
    """Prepara segredo efêmero de 256 bits e somente seu hash para storage."""
    normalized = normalize_email(email)
    if (not _valid_uuid(challenge_id) or not _valid_uuid(identity_id)
            or challenge_id == identity_id or normalized is None
            or not _aware(now)):
        raise EmailChallengeError("EMAIL_CHALLENGE_INVALID")
    try:
        secret = entropy.generate(_TOKEN_BYTES)
        if not isinstance(secret, bytes) or len(secret) != _TOKEN_BYTES:
            raise ValueError
        record = EmailChallengeRecord(
            id=challenge_id, identity_id=identity_id,
            email=normalized, issued_at=now, expires_at=now + _LIFETIME,
            verifier_sha256=_digest(challenge_id, identity_id,
                                    normalized, secret),
        )
        return PreparedEmailChallenge(record, secret)
    except Exception:
        raise EmailChallengeError("EMAIL_CHALLENGE_PREPARATION_FAILED") from None


def verify_and_consume_email_challenge(
    *, record: EmailChallengeRecord, candidate: bytes,
    identity_id: UUID, email: object, now: datetime,
    consumption: ChallengeConsumption,
) -> bool:
    """Resultado genérico; só o storage futuro pode garantir uso único real."""
    try:
        normalized = normalize_email(email)
        if (not isinstance(record, EmailChallengeRecord)
                or not _valid_uuid(record.id)
                or not _valid_uuid(identity_id)
                or record.identity_id != identity_id
                or record.email != normalized or normalized is None
                or not _aware(now) or not _aware(record.issued_at)
                or not _aware(record.expires_at)
                or record.revoked_at is not None
                or not record.issued_at <= now < record.expires_at
                or record.expires_at - record.issued_at > _LIFETIME
                or not isinstance(candidate, bytes)
                or len(candidate) != _TOKEN_BYTES
                or not isinstance(record.verifier_sha256, bytes)
                or len(record.verifier_sha256) != 32):
            return False
        expected = _digest(record.id, identity_id, normalized, candidate)
        if not hmac.compare_digest(expected, record.verifier_sha256):
            return False
        return consumption.consume_once(record.id,
                                        record.verifier_sha256) is True
    except Exception:
        return False
