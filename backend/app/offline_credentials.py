"""Password and session primitives only; no login, token or persistence API.

All session facts must come from a future trusted session store. This module
does not generate operational credentials or grant permissions.
"""

import base64
import binascii
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import hmac
from secrets import token_bytes
from uuid import UUID


_N = 1 << 14
_R = 8
_P = 1
_MAX_PASSWORD_BYTES = 1024
_SALT_BYTES = 16
_HASH_BYTES = 32
_DUMMY_SALT = b"FRCAIXINHA-DUMMY"  # Public; used only to equalize unknown-user work.
_MAX_SESSION_AGE = timedelta(minutes=15)


class CredentialError(ValueError):
    """Stable error code; never includes a password or stored digest."""


@dataclass(frozen=True, slots=True, repr=False)
class PasswordDigest:
    encoded: str

    def __repr__(self) -> str:
        return "PasswordDigest(<redacted>)"


@dataclass(frozen=True, slots=True)
class PasswordCheck:
    valid: bool
    needs_rehash: bool


def _password_bytes(password: object) -> bytes | None:
    if not isinstance(password, str):
        return None
    try:
        encoded = password.encode("utf-8")
    except UnicodeError:
        return None
    if not 12 <= len(encoded) <= _MAX_PASSWORD_BYTES or "\x00" in password:
        return None
    return encoded


def _scrypt(password: bytes, salt: bytes) -> bytes:
    return hashlib.scrypt(password, salt=salt, n=_N, r=_R, p=_P,
                          dklen=_HASH_BYTES, maxmem=64 * 1024 * 1024)


def prepare_password_digest(password: str) -> PasswordDigest:
    """Produce a versioned offline digest from a caller-supplied password."""
    password_bytes = _password_bytes(password)
    if password_bytes is None:
        raise CredentialError("PASSWORD_POLICY_INVALID")
    salt = token_bytes(_SALT_BYTES)
    digest = _scrypt(password_bytes, salt)
    encoded = "$".join((
        "scrypt", "v1", str(_N), str(_R), str(_P),
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    ))
    return PasswordDigest(encoded)


def _decode_digest(stored: object) -> tuple[bytes, bytes] | None:
    if (not isinstance(stored, PasswordDigest) or not isinstance(stored.encoded, str)
            or len(stored.encoded) > 160):
        return None
    try:
        algorithm, version, n, r, p, salt_text, hash_text = stored.encoded.split("$")
        if (algorithm, version, n, r, p) != ("scrypt", "v1", str(_N), str(_R), str(_P)):
            return None
        salt = base64.b64decode(salt_text, validate=True)
        digest = base64.b64decode(hash_text, validate=True)
        if len(salt) != _SALT_BYTES or len(digest) != _HASH_BYTES:
            return None
        return salt, digest
    except (ValueError, UnicodeError, TypeError, binascii.Error):
        return None


def verify_password(password: object, stored: PasswordDigest | None) -> PasswordCheck:
    """Use equivalent KDF work for unknown users and malformed stored digests."""
    supplied = _password_bytes(password)
    decoded = _decode_digest(stored)
    salt, expected = decoded if decoded is not None else (_DUMMY_SALT, b"\x00" * _HASH_BYTES)
    candidate = _scrypt(supplied if supplied is not None else b"invalid-input", salt)
    valid = supplied is not None and decoded is not None and hmac.compare_digest(candidate, expected)
    return PasswordCheck(bool(valid), False)


@dataclass(frozen=True, slots=True)
class SessionFacts:
    """Facts from a future trusted store, not a token supplied by the client."""

    subject_id: UUID
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None


def session_is_current(
    facts: SessionFacts, *, subject_id: UUID, now: datetime,
) -> bool:
    """Bounded eligibility check; authentication and revocation are external."""
    if (not isinstance(facts, SessionFacts) or not isinstance(subject_id, UUID)
            or subject_id.int == 0 or facts.subject_id != subject_id
            or not isinstance(now, datetime) or now.tzinfo is None
            or now.utcoffset() is None):
        return False
    timestamps = (facts.issued_at, facts.expires_at, facts.revoked_at)
    if any(value is not None and (not isinstance(value, datetime)
           or value.tzinfo is None or value.utcoffset() is None) for value in timestamps):
        return False
    if (facts.expires_at <= facts.issued_at
            or facts.expires_at - facts.issued_at > _MAX_SESSION_AGE
            or not facts.issued_at <= now < facts.expires_at):
        return False
    return facts.revoked_at is None or now < facts.revoked_at
