"""Adaptador PF preliminar proposto, isolado de rotas e conexões reais.

O chamador fornece uma transação PostgreSQL explícita, verificador confiável,
chaves custodiadas e registro já preparado. Esta função nunca abre conexão,
confirma a transação externa, cria credencial ou ativa identidade/acesso.
"""

from dataclasses import dataclass
from datetime import datetime
import hmac
from uuid import UUID, uuid4

from sqlalchemy import func, insert, select, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Connection

from app.crypto_documents import DocumentCrypto
from app.db.models import ContractingParty, RegistrationIdempotency, UserIdentity
from app.g3c_completed_replay_pg import fetch_verified_completed_replay
from app.g3c_pg_transaction_guard import require_pg_transaction
from app.g3c_transaction_guards_offline import TransactionGateError
from app.identity_draft import prepare_person_draft
from app.identity_persistence_contract import (
    PreliminaryCommitResult, prepare_preliminary_write_intent,
)
from app.identity_registration_offline import PreparedRegistration
from app.trusted_auth_subject import AuthAssertionVerifier, resolve_auth_subject


class PfPreliminaryStorageUnavailable(RuntimeError):
    """Erro neutro; não revela SQL, CPF, e-mail ou existência de terceiros."""


@dataclass(frozen=True, slots=True, repr=False)
class PfPreliminaryDigests:
    origin: bytes
    attempt: bytes
    fingerprint: bytes

    def __repr__(self) -> str:
        return "PfPreliminaryDigests(<redacted>)"


def _digest(key: bytes, purpose: bytes, *values: bytes) -> bytes:
    framed = b"".join(len(value).to_bytes(4, "big") + value for value in values)
    return hmac.digest(key, b"FRCAIXINHA/PF-PRELIMINARY/v1/" + purpose + framed,
                       "sha256")


def _prepare_digests(
    *, registration: PreparedRegistration, assertion: bytes,
    verifier: AuthAssertionVerifier, expected_issuer: str,
    idempotency_key: bytes, crypto: DocumentCrypto, digest_key: bytes,
    now: datetime,
) -> tuple[PfPreliminaryDigests, str, datetime]:
    """Revalida a origem e o documento protegido antes de qualquer INSERT."""
    if (not isinstance(crypto, DocumentCrypto)
            or type(digest_key) is not bytes or len(digest_key) < 32):
        raise TransactionGateError("PF_WRITE_DENIED")
    try:
        auth = resolve_auth_subject(
            assertion=assertion, verifier=verifier,
            expected_issuer=expected_issuer, now=now,
        )
        intent = prepare_preliminary_write_intent(
            registration=registration, auth=auth,
            idempotency_key=idempotency_key, now=now,
        )
        identity, party = registration.identity, registration.party
        if (party.party_type != "PF" or auth.subject_id != identity.id
                or type(party.legal_name) is not str
                or party.legal_name != identity.name):
            raise ValueError
        cpf = crypto.decrypt(
            identity.cpf_ciphertext, kind="CPF", entity="user_identity",
            field="cpf", record_id=str(identity.id),
        )
        person = prepare_person_draft(
            name=identity.name, cpf=cpf,
            email=identity.email, phone=identity.phone,
        )
        if (person.name != identity.name or person.email != identity.email
                or person.phone != identity.phone
                or not hmac.compare_digest(
                    crypto.lookup_hmac(cpf, kind="CPF"),
                    identity.cpf_lookup_hmac,
                )):
            raise ValueError
        subject = auth.value.encode("ascii")
        digests = PfPreliminaryDigests(
            origin=_digest(digest_key, b"origin", subject),
            attempt=_digest(digest_key, b"attempt", intent.idempotency_digest),
            fingerprint=_digest(
                digest_key, b"fingerprint", identity.name.encode("utf-8"),
                identity.cpf_lookup_hmac, identity.email.encode("ascii"),
                identity.phone.encode("ascii"), party.legal_name.encode("utf-8"),
            ),
        )
        return digests, auth.value, auth.session.expires_at
    except Exception:
        raise TransactionGateError("PF_WRITE_DENIED") from None


def reserve_pf_statement(digests: PfPreliminaryDigests, *, reservation_id: UUID):
    table = RegistrationIdempotency.__table__
    stamp = func.statement_timestamp()
    return (
        pg_insert(table).values(
            id=reservation_id, origin_digest=digests.origin,
            attempt_digest=digests.attempt,
            request_fingerprint=digests.fingerprint, state="RESERVED",
            created_at=stamp,
            expires_at=stamp + text("INTERVAL '15 minutes'"),
        ).on_conflict_do_nothing(
            constraint="uq_registration_idempotency_origin_attempt",
        ).returning(table.c.id)
    )


def complete_pf_statement(
    digests: PfPreliminaryDigests, *, reservation_id: UUID,
    identity_id: UUID, party_id: UUID, session_expires_at: datetime,
):
    table = RegistrationIdempotency.__table__
    return (
        update(table).where(
            table.c.id == reservation_id,
            table.c.origin_digest == digests.origin,
            table.c.attempt_digest == digests.attempt,
            table.c.request_fingerprint == digests.fingerprint,
            table.c.state == "RESERVED",
            table.c.expires_at > func.clock_timestamp(),
            func.clock_timestamp() < session_expires_at,
        ).values(
            state="COMPLETED", identity_id=identity_id, party_id=party_id,
        ).returning(table.c.id)
    )


def write_pf_preliminary_within_transaction(
    connection: Connection, *, registration: PreparedRegistration,
    assertion: bytes, verifier: AuthAssertionVerifier, expected_issuer: str,
    idempotency_key: bytes, crypto: DocumentCrypto, digest_key: bytes,
) -> PreliminaryCommitResult:
    """Escreve PF PENDENTE/PRELIMINAR em SAVEPOINT; COMMIT é do chamador.

    Proposta offline: não ligar a rota anônima nem usar no banco autoritativo
    antes de gates de autenticação, chaves, IN06/IN08 e ensaio físico.
    """
    require_pg_transaction(connection, denial="PF_WRITE_DENIED")
    try:
        now = connection.execute(select(func.clock_timestamp())).scalar_one()
        digests, auth_subject, session_expires_at = _prepare_digests(
            registration=registration, assertion=assertion,
            verifier=verifier, expected_issuer=expected_issuer,
            idempotency_key=idempotency_key, crypto=crypto,
            digest_key=digest_key, now=now,
        )
        identity, party = registration.identity, registration.party
        with connection.begin_nested():
            reservation_id = uuid4()
            claimed = connection.execute(reserve_pf_statement(
                digests, reservation_id=reservation_id,
            )).scalar_one_or_none()
            if claimed is None:
                identity_id, party_id = fetch_verified_completed_replay(
                    connection, origin_digest=digests.origin,
                    attempt_digest=digests.attempt,
                    request_fingerprint=digests.fingerprint,
                )
                if identity_id != identity.id:
                    raise TransactionGateError("PF_WRITE_DENIED")
                stored_subject = connection.execute(
                    select(UserIdentity.__table__.c.auth_subject).where(
                        UserIdentity.__table__.c.id == identity_id,
                    ).with_for_update(of=UserIdentity.__table__)
                ).scalar_one_or_none()
                if stored_subject != auth_subject:
                    raise TransactionGateError("PF_WRITE_DENIED")
                replay_now = connection.execute(
                    select(func.clock_timestamp())
                ).scalar_one()
                if replay_now >= session_expires_at:
                    raise TransactionGateError("PF_WRITE_DENIED")
                return PreliminaryCommitResult(identity_id, party_id, False)
            if claimed != reservation_id:
                raise TransactionGateError("PF_WRITE_DENIED")
            connection.execute(insert(UserIdentity.__table__).values(
                id=identity.id, name=identity.name,
                cpf_ciphertext=identity.cpf_ciphertext,
                cpf_lookup_hmac=identity.cpf_lookup_hmac,
                email=identity.email, phone=identity.phone,
                auth_subject=auth_subject, status="PENDENTE",
            ))
            connection.execute(insert(ContractingParty.__table__).values(
                id=party.id, party_type="PF", legal_name=party.legal_name,
                pf_user_id=identity.id,
                initial_registration_identity_id=identity.id,
                status="PRELIMINAR",
            ))
            completed = connection.execute(complete_pf_statement(
                digests, reservation_id=reservation_id,
                identity_id=identity.id, party_id=party.id,
                session_expires_at=session_expires_at,
            )).scalar_one_or_none()
            if completed != reservation_id:
                raise TransactionGateError("PF_WRITE_DENIED")
            return PreliminaryCommitResult(identity.id, party.id, True)
    except TransactionGateError:
        raise
    except Exception:
        raise PfPreliminaryStorageUnavailable("PF_STORAGE_UNAVAILABLE") from None
