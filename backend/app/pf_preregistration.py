"""Serviço transitório de pré-cadastro PF para demonstração offline.

O armazenamento é injetado e pertence à instância da aplicação. Não há estado
global, banco, rede, autenticação, aprovação civil ou concessão de acesso.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from enum import Enum
from hashlib import sha256
import hmac
import secrets
from threading import RLock
from time import monotonic
from typing import Final
from uuid import UUID, uuid4

from app.identity_draft import PersonDraft, prepare_person_draft


class PreRegistrationError(ValueError):
    """Erro estável, sem CPF, e-mail, telefone ou referências na mensagem."""


class PreRegistrationState(str, Enum):
    PRELIMINARY = "PRELIMINARY"
    CONTACT_CONFIRMED = "CONTACT_CONFIRMED"


@dataclass(frozen=True, slots=True, repr=False)
class PreRegistrationReceipt:
    request_ref: UUID
    state: PreRegistrationState
    idempotent_replay: bool = False
    contact_confirmation_required: bool = True
    identity_verified: bool = field(default=False, init=False)
    access_granted: bool = field(default=False, init=False)
    persisted: bool = field(default=False, init=False)
    _confirmation_token: str = field(default="", repr=False)

    def __repr__(self) -> str:
        return "PreRegistrationReceipt(<redacted>)"


@dataclass(frozen=True, slots=True, repr=False)
class _Record:
    request_ref: UUID
    fingerprint: bytes
    idempotency_lookup: bytes
    cpf_lookup: bytes
    email_lookup: bytes
    confirmation_token_digest: str
    token_expires_at: float
    state: PreRegistrationState = PreRegistrationState.PRELIMINARY
    failed_confirmation_attempts: int = 0
    token_revoked: bool = False
    audit_events: tuple[str, ...] = ("SUBMITTED",)

    def __repr__(self) -> str:
        return "_Record(<redacted>)"


class TransientPreRegistrationStore:
    """Repositório efêmero injetado, com índices protegidos e registro atômico."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._lookup_key = secrets.token_bytes(32)
        self._by_key: dict[bytes, _Record] = {}
        self._by_cpf: dict[bytes, UUID] = {}
        self._by_email: dict[bytes, UUID] = {}
        self._by_ref: dict[UUID, _Record] = {}

    def lookup_digest(self, purpose: str, value: str) -> bytes:
        """HMAC efêmero com domínio separado; não conserva o identificador claro."""
        material = b"FRCAIXINHA/PF-DEMO/v1/" + purpose.encode("ascii")
        return hmac.new(
            self._lookup_key, material + b"\0" + value.encode("utf-8"), sha256,
        ).digest()

    def register(self, record: _Record) -> tuple[_Record, bool]:
        """Verifica idempotência e unicidade de CPF/e-mail na mesma seção crítica."""
        with self._lock:
            previous = self._by_key.get(record.idempotency_lookup)
            if previous is not None:
                if not hmac.compare_digest(previous.fingerprint, record.fingerprint):
                    raise PreRegistrationError("IDEMPOTENCY_CONFLICT")
                return previous, True
            if record.cpf_lookup in self._by_cpf or record.email_lookup in self._by_email:
                raise PreRegistrationError("DUPLICATE_PRE_REGISTRATION")
            self._by_key[record.idempotency_lookup] = record
            self._by_cpf[record.cpf_lookup] = record.request_ref
            self._by_email[record.email_lookup] = record.request_ref
            self._by_ref[record.request_ref] = record
            return record, False

    def locked(self):
        return self._lock

    def by_ref(self, request_ref: UUID) -> _Record | None:
        with self._lock:
            return self._by_ref.get(request_ref)

    def replace(self, record: _Record) -> None:
        with self._lock:
            self._by_ref[record.request_ref] = record
            self._by_key[record.idempotency_lookup] = record



_MAX_IDEMPOTENCY_KEY: Final = 128
_SIMULATED_TOKEN_LIFETIME_SECONDS: Final = 600  # F2P4: teto de 10 min para desafio.
_MAX_SIMULATED_CONFIRM_FAILURES: Final = 5  # Contenção apenas demonstrativa.


def _fingerprint(person: PersonDraft, store: TransientPreRegistrationStore) -> bytes:
    # Inclui o nome: mesma chave com qualquer campo normalizado diferente conflita.
    material = "\x1f".join((person.name, person.cpf, person.email, person.phone))
    return store.lookup_digest("payload", material)


def _digest(token: str) -> str:
    return sha256(token.encode("ascii")).hexdigest()


class PfPreRegistrationService:
    """Prepara solicitações PF sem afirmar identidade ou criar acesso."""

    def __init__(self, store: TransientPreRegistrationStore) -> None:
        self._store = store

    def submit(
        self, *, name: object, cpf: object, email: object, phone: object,
        idempotency_key: object,
    ) -> PreRegistrationReceipt:
        if idempotency_key is None:
            raise PreRegistrationError("IDEMPOTENCY_KEY_MISSING")
        if (type(idempotency_key) is not str
                or not 1 <= len(idempotency_key) <= _MAX_IDEMPOTENCY_KEY
                or any(ord(char) < 0x21 or ord(char) > 0x7E for char in idempotency_key)):
            raise PreRegistrationError("IDEMPOTENCY_KEY_INVALID")
        person = prepare_person_draft(name=name, cpf=cpf, email=email, phone=phone)
        try:
            token = secrets.token_urlsafe(24)
            record = _Record(
                request_ref=uuid4(),
                fingerprint=_fingerprint(person, self._store),
                idempotency_lookup=self._store.lookup_digest("idempotency", idempotency_key),
                cpf_lookup=self._store.lookup_digest("cpf", person.cpf),
                email_lookup=self._store.lookup_digest("email", person.email),
                confirmation_token_digest=_digest(token),
                token_expires_at=monotonic() + _SIMULATED_TOKEN_LIFETIME_SECONDS,
            )
            stored, replay = self._store.register(record)
        except PreRegistrationError:
            raise
        except Exception:
            raise PreRegistrationError("PRE_REGISTRATION_UNAVAILABLE") from None
        return self._receipt(stored, token="" if replay else token, idempotent_replay=replay)

    def confirm_contact(self, *, request_ref: object, token: object) -> PreRegistrationReceipt:
        if (type(request_ref) is not UUID or type(token) is not str
                or not 1 <= len(token) <= 256 or not token.isascii()):
            raise PreRegistrationError("CONTACT_CONFIRMATION_INVALID")
        try:
            with self._store.locked():
                record = self._store.by_ref(request_ref)
                if record is None or record.state is not PreRegistrationState.PRELIMINARY:
                    raise PreRegistrationError("CONTACT_CONFIRMATION_INVALID")
                if record.token_revoked or monotonic() >= record.token_expires_at:
                    if not record.token_revoked:
                        self._store.replace(dataclass_replace(
                            record, token_revoked=True, confirmation_token_digest="",
                            audit_events=record.audit_events + ("CONTACT_CONFIRMATION_EXPIRED",),
                        ))
                    raise PreRegistrationError("CONTACT_CONFIRMATION_INVALID")
                if not secrets.compare_digest(record.confirmation_token_digest, _digest(token)):
                    failed = record.failed_confirmation_attempts + 1
                    locked = failed >= _MAX_SIMULATED_CONFIRM_FAILURES
                    self._store.replace(dataclass_replace(
                        record, failed_confirmation_attempts=failed,
                        token_revoked=locked,
                        confirmation_token_digest="" if locked else record.confirmation_token_digest,
                        audit_events=record.audit_events + (
                            "CONTACT_CONFIRMATION_LOCKED" if locked
                            else "CONTACT_CONFIRMATION_REJECTED",
                        ),
                    ))
                    raise PreRegistrationError("CONTACT_CONFIRMATION_INVALID")
                confirmed = dataclass_replace(
                    record, state=PreRegistrationState.CONTACT_CONFIRMED,
                    confirmation_token_digest="",
                    audit_events=record.audit_events + ("CONTACT_CONFIRMED_SIMULATED",),
                )
                self._store.replace(confirmed)
                return self._receipt(confirmed)
        except PreRegistrationError:
            raise
        except Exception:
            raise PreRegistrationError("PRE_REGISTRATION_UNAVAILABLE") from None

    @staticmethod
    def _receipt(record: _Record, *, token: str = "", idempotent_replay: bool = False) -> PreRegistrationReceipt:
        return PreRegistrationReceipt(
            request_ref=record.request_ref, state=record.state,
            idempotent_replay=idempotent_replay,
            contact_confirmation_required=record.state is PreRegistrationState.PRELIMINARY,
            _confirmation_token=token,
        )
