"""Consulta transacional FUTURA de sessão opaca no PostgreSQL (não ativada).

Depende de F2P4 ainda não aplicada. NÃO abre login, cria token, revoga sessão
ou concede papel/tenant/ciclo. Deve ser chamada com verificador calculado no
servidor, sob transação EXPLÍCITA que abrange também a ação protegida.
Os locks I→C→S não tornam a autorização válida depois da transação.
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
    """Localiza um candidato sem lock; seus fatos não autorizam acesso."""
    session = IdentitySession.__table__
    return select(
        session.c.id, session.c.identity_id,
    ).where(session.c.verifier_sha256 == verifier_sha256)


def session_identity_lock_statement(*, identity_id: UUID):
    identity = UserIdentity.__table__
    return select(
        identity.c.id, identity.c.status, identity.c.email_verified_at,
    ).where(identity.c.id == identity_id).with_for_update(of=identity)


def session_credential_lock_statement(*, identity_id: UUID):
    credential = IdentityCredential.__table__
    return select(
        credential.c.identity_id, credential.c.status, credential.c.updated_at,
    ).where(credential.c.identity_id == identity_id).with_for_update(
        read=True, of=credential,
    )


def session_lock_statement(*, session_id: UUID, verifier_sha256: bytes):
    session = IdentitySession.__table__
    return select(
        session.c.id, session.c.identity_id, session.c.issued_at,
        session.c.expires_at, session.c.revoked_at,
    ).where(
        session.c.id == session_id,
        session.c.verifier_sha256 == verifier_sha256,
    ).with_for_update(read=True, of=session)


def read_current_session_identity(
    connection: Connection, *, verifier_sha256: bytes,
) -> UUID | None:
    """Reconsulta I→C→S sob lock; NÃO concede autorização.

    A ação protegida e a revalidação de RoleGrants/contexto devem ocorrer na
    MESMA transação externa. O adaptador não abre nem encerra essa transação.
    """
    if type(verifier_sha256) is not bytes or len(verifier_sha256) != 32:
        raise TransactionGateError("SESSION_LOOKUP_DENIED")
    require_pg_transaction(connection, denial="SESSION_LOOKUP_DENIED")
    try:
        found = connection.execute(current_session_statement(
            verifier_sha256=verifier_sha256,
        )).one_or_none()
        if found is None:
            return None
        session_id, identity_id = found
        if not all(
            isinstance(value, UUID) and value.int != 0
            for value in (session_id, identity_id)
        ):
            return None

        identity = connection.execute(session_identity_lock_statement(
            identity_id=identity_id,
        )).one_or_none()
        if identity is None or identity[0] != identity_id:
            return None

        credential = connection.execute(session_credential_lock_statement(
            identity_id=identity_id,
        )).one_or_none()
        if credential is None or credential[0] != identity_id:
            return None

        session = connection.execute(session_lock_statement(
            session_id=session_id, verifier_sha256=verifier_sha256,
        )).one_or_none()
        if (session is None or session[0] != session_id
                or session[1] != identity_id):
            return None

        now = connection.execute(select(func.clock_timestamp())).scalar_one()
        facts = SessionFacts(
            session_identity_id=session[1],
            identity_id=identity[0],
            identity_status=identity[1],
            credential_status=credential[1],
            email_verified_at=identity[2],
            credential_updated_at=credential[2],
            issued_at=session[2],
            expires_at=session[3],
            revoked_at=session[4],
        )
        return facts.identity_id if session_current_with_server_facts(
            facts, now=now,
        ) else None
    except Exception:
        raise SessionRepositoryUnavailable("SESSION_STORAGE_UNAVAILABLE") from None
