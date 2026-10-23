"""Consulta transacional FUTURA de sessão opaca no PostgreSQL (não ativada).

Depende de F2P4 ainda não aplicada. NÃO abre login, cria token, revoga sessão
ou concede papel/tenant/ciclo. Deve ser chamada com verificador calculado no
servidor, sob transação EXPLÍCITA que abrange também a ação protegida.
SELECT FOR SHARE bloqueia UPDATE concorrente enquanto dura a transação;
não torna a autorização válida depois que a transação terminar.
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.engine import Connection

from app.db.models import IdentityCredential, IdentitySession, UserIdentity
from app.g3c_pg_transaction_guard import require_pg_transaction
from app.g3c_transaction_guards_offline import (
    SessionFacts, TransactionGateError, session_current_with_server_facts,
)


class SessionRepositoryUnavailable(RuntimeError):
    """Falha interna genérica, sem verificador, e-mail ou erro SQL."""


def current_session_statement(*, verifier_sha256: bytes):
    session = IdentitySession.__table__
    identity = UserIdentity.__table__
    credential = IdentityCredential.__table__
    return (
        select(
            session.c.identity_id,
            identity.c.id,
            identity.c.status,
            credential.c.status,
            identity.c.email_verified_at,
            credential.c.updated_at,
            session.c.issued_at,
            session.c.expires_at,
            session.c.revoked_at,
        )
        .select_from(
            session.join(
                identity, session.c.identity_id == identity.c.id,
            ).join(
                credential, credential.c.identity_id == identity.c.id,
            )
        )
        .where(session.c.verifier_sha256 == verifier_sha256)
        .with_for_update(
            read=True, of=(session, identity, credential),
        )
    )


def read_current_session_identity(
    connection: Connection, *, verifier_sha256: bytes,
) -> UUID | None:
    """Reconsulta 3 linhas do servidor sob lock, NÃO concede autorização.

    A operação protegida e a revalidação de RoleGrants/contexto devem ocorrer
    na MESMA transação para não abrir janela TOCTOU. O token do cliente não é
    recebido; apenas verificador SHA-256 produzido pelo servidor.
    """
    if type(verifier_sha256) is not bytes or len(verifier_sha256) != 32:
        raise TransactionGateError("SESSION_LOOKUP_DENIED")
    require_pg_transaction(connection, denial="SESSION_LOOKUP_DENIED")
    try:
        row = connection.execute(
            current_session_statement(verifier_sha256=verifier_sha256),
        ).one_or_none()
        if row is None:
            return None
        now = connection.execute(select(func.clock_timestamp())).scalar_one()
        facts = SessionFacts(
            session_identity_id=row[0],
            identity_id=row[1],
            identity_status=row[2],
            credential_status=row[3],
            email_verified_at=row[4],
            credential_updated_at=row[5],
            issued_at=row[6],
            expires_at=row[7],
            revoked_at=row[8],
        )
        return facts.identity_id if session_current_with_server_facts(
            facts, now=now,
        ) else None
    except Exception:
        raise SessionRepositoryUnavailable("SESSION_STORAGE_UNAVAILABLE") from None
