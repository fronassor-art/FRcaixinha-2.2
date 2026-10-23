"""Leitura transacional FUTURA de replay concluído, não integrada à API.

Usa o modelo F2P4 ainda NÃO aplicado. Nunca cria ou altera tabelas/linhas.
O chamador deverá fornecer digests derivadas de origem confiável, uma conexão
PostgreSQL dentro de transação EXPLÍCITA e permissão operacional aprovada.
Não arbitra o INSERT concorrente: isso requer um adaptador separado, UNIQUE
e estratégia de conflito/retentativa a ser revisada e autorizada.
"""
from sqlalchemy import func, select
from sqlalchemy.engine import Connection

from app.db.models import ContractingParty, RegistrationIdempotency
from app.g3c_transaction_guards_offline import (
    CompletedAttempt, PartyLink, TransactionGateError, verified_replay_ids,
)


class ReplayRepositoryUnavailable(RuntimeError):
    """Falha interna neutra: detalhes SQL não devem ser expostos à API."""


def completed_replay_statement(*, origin_digest: bytes, attempt_digest: bytes):
    """Consulta somente COMPLETED e bloqueia AMBAS as linhas durante o exame.

    A chave única (origin_digest, attempt_digest) da F2P4 futura impede que
    dois resultados distintos tenham a mesma chave na mesma transação.
    """
    registration = RegistrationIdempotency.__table__
    party = ContractingParty.__table__
    return (
        select(
            registration.c.origin_digest,
            registration.c.attempt_digest,
            registration.c.request_fingerprint,
            registration.c.identity_id,
            registration.c.party_id,
            registration.c.state,
            registration.c.created_at,
            registration.c.expires_at,
            party.c.id,
            party.c.party_type,
            party.c.pf_user_id,
            party.c.representative_user_id,
        )
        .select_from(registration.join(
            party, registration.c.party_id == party.c.id,
        ))
        .where(
            registration.c.origin_digest == origin_digest,
            registration.c.attempt_digest == attempt_digest,
            registration.c.state == "COMPLETED",
        )
        .with_for_update(of=(registration, party))
    )


def fetch_verified_completed_replay(
    connection: Connection, *,
    origin_digest: bytes, attempt_digest: bytes,
    request_fingerprint: bytes,
):
    """Read-only (sem INSERT/UPDATE) dentro de transação administrada fora.

    SELECT FOR UPDATE cria locks temporários e portanto NÃO é read-only para
    o PostgreSQL; só usar em DB expressamente autorizado quando F2P4 existir.
    Lê clock_timestamp() APÓS o lock para não reutilizar a hora anterior a
    uma possível espera longa por transação concorrente.
    """
    if (
        not isinstance(connection, Connection)
        or not connection.in_transaction()
        or not all(type(d) is bytes and len(d) == 32 for d in (
            origin_digest, attempt_digest, request_fingerprint,
        ))
    ):
        raise TransactionGateError("REPLAY_DENIED")

    statement = completed_replay_statement(
        origin_digest=origin_digest, attempt_digest=attempt_digest,
    )
    try:
        row = connection.execute(statement).one_or_none()
        if row is None:
            raise TransactionGateError("REPLAY_DENIED")
        server_now = connection.execute(select(func.clock_timestamp())).scalar_one()
        stored = CompletedAttempt(
            origin_digest=row[0], attempt_digest=row[1], fingerprint=row[2],
            identity_id=row[3], party_id=row[4], state=row[5],
            created_at=row[6], expires_at=row[7],
        )
        party = PartyLink(
            id=row[8], party_type=row[9], pf_user_id=row[10],
            representative_user_id=row[11],
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
