"""Leitura transacional FUTURA de replay concluído, não integrada à API.

Usa o modelo F2P4 ainda NÃO aplicado. Nunca cria ou altera tabelas/linhas.
O chamador deverá fornecer digests derivadas de origem confiável, uma conexão
PostgreSQL dentro de transação EXPLÍCITA e permissão operacional aprovada.
Não arbitra o INSERT concorrente: isso requer um adaptador separado, UNIQUE
e estratégia de conflito/retentativa a ser revisada e autorizada.
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.engine import Connection

from app.db.models import ContractingParty, RegistrationIdempotency, UserIdentity
from app.g3c_pg_transaction_guard import require_pg_transaction
from app.g3c_transaction_guards_offline import (
    CompletedAttempt, PartyLink, TransactionGateError, verified_replay_ids,
)


class ReplayRepositoryUnavailable(RuntimeError):
    """Falha interna neutra: detalhes SQL não devem ser expostos à API."""


def completed_replay_statement(*, origin_digest: bytes, attempt_digest: bytes):
    """Bloqueia R antes de I e P; nunca delega a ordem a um JOIN."""
    registration = RegistrationIdempotency.__table__
    return (
        select(
            registration.c.id,
            registration.c.origin_digest,
            registration.c.attempt_digest,
            registration.c.request_fingerprint,
            registration.c.identity_id,
            registration.c.party_id,
            registration.c.state,
            registration.c.created_at,
            registration.c.expires_at,
        )
        .where(
            registration.c.origin_digest == origin_digest,
            registration.c.attempt_digest == attempt_digest,
            registration.c.state == "COMPLETED",
        )
        .with_for_update(of=registration)
    )


def replay_identity_lock_statement(*, identity_id: UUID):
    identity = UserIdentity.__table__
    return select(identity.c.id).where(
        identity.c.id == identity_id,
    ).with_for_update(of=identity)


def replay_party_lock_statement(*, party_id: UUID):
    party = ContractingParty.__table__
    return select(
        party.c.id, party.c.party_type, party.c.pf_user_id,
        party.c.representative_user_id,
    ).where(party.c.id == party_id).with_for_update(of=party)


def replay_recheck_statement(*, reservation_id: UUID):
    registration = RegistrationIdempotency.__table__
    return select(
        registration.c.id, registration.c.origin_digest,
        registration.c.attempt_digest, registration.c.request_fingerprint,
        registration.c.identity_id, registration.c.party_id,
        registration.c.state, registration.c.created_at,
        registration.c.expires_at,
    ).where(registration.c.id == reservation_id)


def fetch_verified_completed_replay(
    connection: Connection, *,
    origin_digest: bytes, attempt_digest: bytes,
    request_fingerprint: bytes,
):
    """Lê R→I→P sob transação do chamador, sem conceder acesso operacional.

    FOR UPDATE não é permitido em transação PostgreSQL READ ONLY. O relógio
    do servidor é lido após todas as esperas por lock.
    """
    if not all(type(d) is bytes and len(d) == 32 for d in (
            origin_digest, attempt_digest, request_fingerprint,
        )):
        raise TransactionGateError("REPLAY_DENIED")
    require_pg_transaction(connection, denial="REPLAY_DENIED")

    try:
        reserved = connection.execute(completed_replay_statement(
            origin_digest=origin_digest, attempt_digest=attempt_digest,
        )).one_or_none()
        if reserved is None or not all(
            isinstance(value, UUID) and value.int != 0
            for value in (reserved[0], reserved[4], reserved[5])
        ):
            raise TransactionGateError("REPLAY_DENIED")

        identity = connection.execute(replay_identity_lock_statement(
            identity_id=reserved[4],
        )).scalar_one_or_none()
        if identity != reserved[4]:
            raise TransactionGateError("REPLAY_DENIED")

        party_row = connection.execute(replay_party_lock_statement(
            party_id=reserved[5],
        )).one_or_none()
        if party_row is None or party_row[0] != reserved[5]:
            raise TransactionGateError("REPLAY_DENIED")

        row = connection.execute(replay_recheck_statement(
            reservation_id=reserved[0],
        )).one_or_none()
        if row is None or tuple(row) != tuple(reserved):
            raise TransactionGateError("REPLAY_DENIED")

        server_now = connection.execute(select(func.clock_timestamp())).scalar_one()
        stored = CompletedAttempt(
            origin_digest=row[1], attempt_digest=row[2], fingerprint=row[3],
            identity_id=row[4], party_id=row[5], state=row[6],
            created_at=row[7], expires_at=row[8],
        )
        party = PartyLink(
            id=party_row[0], party_type=party_row[1], pf_user_id=party_row[2],
            representative_user_id=party_row[3],
        )
        return verified_replay_ids(
            stored, party, origin_digest=origin_digest,
            attempt_digest=attempt_digest,
            request_fingerprint=request_fingerprint, now=server_now,
        )
    except TransactionGateError:
        raise
    except Exception:
        raise ReplayRepositoryUnavailable("REPLAY_STORAGE_UNAVAILABLE") from None
