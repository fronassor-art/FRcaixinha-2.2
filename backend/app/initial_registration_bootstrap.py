"""Preparação offline da primeira inscrição, sem sessão ou escrita.

O chamador futuro deve fornecer IDs e escopo de origem produzidos pelo servidor.
A porta de conflito é consultiva; a unicidade depende de transação PostgreSQL.
"""

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol
from uuid import UUID

from app.crypto_documents import DocumentCrypto
from app.email_confirmation_offline import (
    ChallengeEntropy, EmailChallengeRecord, prepare_email_challenge,
)
from app.identity_registration_offline import (
    ConflictProbe, PreparedRegistration, prepare_pf_registration,
    prepare_pj_registration,
)
from app.offline_credentials import PasswordDigest, prepare_password_digest


_DOMAIN = b"FRCAIXINHA/INITIAL-REGISTRATION/v1/"
_ATTEMPT_LIFETIME = timedelta(minutes=15)


class InitialRegistrationError(ValueError):
    """Erro estável, sem documento, senha, e-mail ou detalhe interno."""


class BootstrapIdentifiers(Protocol):
    """Fonte injetada pelo servidor; nunca aceite IDs de campos do cliente."""

    def new_uuid(self) -> UUID: ...


@dataclass(frozen=True, slots=True, repr=False)
class InitialRegistrationIntent:
    registration: PreparedRegistration
    auth_subject: str
    password_digest: PasswordDigest
    credential_state: str
    challenge: EmailChallengeRecord
    origin_digest: bytes
    attempt_digest: bytes
    request_fingerprint: bytes
    attempt_expires_at: datetime

    def __repr__(self) -> str:
        return "InitialRegistrationIntent(<redacted>)"


@dataclass(frozen=True, slots=True, repr=False)
class PreparedInitialRegistration:
    intent: InitialRegistrationIntent
    delivery_secret: bytes  # Efêmero; apenas canal futuro aprovado.

    def __repr__(self) -> str:
        return "PreparedInitialRegistration(<redacted>)"


def _frame(value: bytes) -> bytes:
    return len(value).to_bytes(4, "big") + value


def _valid_uuid(value: object) -> bool:
    return isinstance(value, UUID) and value.int != 0


def _digest(key: bytes, label: bytes, *parts: bytes) -> bytes:
    return hmac.digest(key, _DOMAIN + label + b"".join(_frame(p) for p in parts),
                       "sha256")


def prepare_initial_registration(
    *, party_type: str, name: object, cpf: object, email: object,
    phone: object, password: str, legal_name: object = None,
    cnpj: object = None, ids: BootstrapIdentifiers,
    crypto: DocumentCrypto, probe: ConflictProbe,
    challenge_entropy: ChallengeEntropy, origin_scope: bytes,
    attempt_key: bytes, fingerprint_key: bytes, now: datetime,
) -> PreparedInitialRegistration:
    """Produz apenas campos para uma transação futura; não autentica ninguém."""
    if (party_type not in ("PF", "PJ")
            or not isinstance(now, datetime) or now.tzinfo is None
            or now.utcoffset() is None
            or not isinstance(origin_scope, bytes) or len(origin_scope) != 32
            or not isinstance(attempt_key, bytes)
            or not 16 <= len(attempt_key) <= 128
            or not isinstance(fingerprint_key, bytes)
            or len(fingerprint_key) != 32):
        raise InitialRegistrationError("INITIAL_REGISTRATION_INVALID")
    if party_type == "PF" and (legal_name is not None or cnpj is not None):
        raise InitialRegistrationError("INITIAL_REGISTRATION_INVALID")
    try:
        identity_id, party_id, challenge_id = (
            ids.new_uuid(), ids.new_uuid(), ids.new_uuid()
        )
        if (not all(_valid_uuid(value) for value in
                    (identity_id, party_id, challenge_id))
                or len({identity_id, party_id, challenge_id}) != 3):
            raise ValueError
        if party_type == "PF":
            registration = prepare_pf_registration(
                name=name, cpf=cpf, email=email, phone=phone,
                identity_id=identity_id, party_id=party_id,
                crypto=crypto, probe=probe,
            )
        else:
            registration = prepare_pj_registration(
                legal_name=legal_name, cnpj=cnpj,
                representative_name=name, representative_cpf=cpf,
                representative_email=email, representative_phone=phone,
                identity_id=identity_id, party_id=party_id,
                crypto=crypto, probe=probe,
            )
        password_digest = prepare_password_digest(password)
        challenge = prepare_email_challenge(
            challenge_id=challenge_id, identity_id=identity_id,
            email=registration.identity.email, now=now,
            entropy=challenge_entropy,
        )
        identity, party = registration.identity, registration.party
        fields = (
            party_type.encode("ascii"), identity.name.encode("utf-8"),
            identity.cpf_lookup_hmac, identity.email.encode("ascii"),
            identity.phone.encode("ascii"), party.legal_name.encode("utf-8"),
            party.tax_id_lookup_hmac or b"", password.encode("utf-8"),
        )
        intent = InitialRegistrationIntent(
            registration=registration,
            auth_subject=f"local:{identity_id}",
            password_digest=password_digest,
            credential_state="PENDING_EMAIL",
            challenge=challenge.record,
            origin_digest=_digest(fingerprint_key, b"ORIGIN", origin_scope),
            attempt_digest=_digest(fingerprint_key, b"ATTEMPT",
                                   origin_scope, attempt_key),
            request_fingerprint=_digest(fingerprint_key, b"REQUEST", *fields),
            attempt_expires_at=now + _ATTEMPT_LIFETIME,
        )
        return PreparedInitialRegistration(intent, challenge.delivery_secret)
    except Exception:
        raise InitialRegistrationError("INITIAL_REGISTRATION_INVALID") from None


def equivalent_initial_attempt(
    previous: InitialRegistrationIntent, candidate: InitialRegistrationIntent,
) -> bool:
    """Classifica repetição; o storage futuro deve consultar antes do probe."""
    if (not isinstance(previous, InitialRegistrationIntent)
            or not isinstance(candidate, InitialRegistrationIntent)):
        raise InitialRegistrationError("INITIAL_REGISTRATION_INVALID")
    if not hmac.compare_digest(previous.attempt_digest, candidate.attempt_digest):
        return False
    if (not hmac.compare_digest(previous.origin_digest, candidate.origin_digest)
            or not hmac.compare_digest(previous.request_fingerprint,
                                       candidate.request_fingerprint)):
        raise InitialRegistrationError("INITIAL_ATTEMPT_CONFLICT")
    return True
