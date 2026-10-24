"""IN-03: proposta de consumo PostgreSQL de desafio de email, DESABILITADA.

Este módulo não é usado pela API e exige a minuta F2P4 ainda NÃO aplicada.
Somente uma conexão SQLAlchemy em transação EXPLÍCITA, recebida do chamador,
pode executá-lo após aprovações e ensaios reais isolados. Não concede login,
RoleGrant, tenant, licença ou estado APTO de representação PJ.

Um verificador de 32 bytes foi emitido com hash de challenge_id, identidade,
contato então normalizado e segredo efêmero; não há coluna snapshot na minuta.
A checagem com o EMAIL ATUAL do banco invalida token para outro endereço,
mas mudanças A→B→A exigem revogação segura/epoch ainda não provados (IN05).
"""
import hmac
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.engine import Connection

from app.db.models import (
    EmailConfirmationChallenge, IdentityCredential, UserIdentity,
)
from app.email_confirmation_offline import _digest
from app.g3c_pg_transaction_guard import require_pg_transaction
from app.g3c_transaction_guards_offline import (
    EmailFacts, TransactionGateError, email_challenge_eligible,
)


class EmailConfirmationStorageUnavailable(RuntimeError):
    """Erro genérico de falha transacional, sem detalhes de banco ou token."""


class _EmailDenied(RuntimeError):
    """Sinal interno para reverter o SAVEPOINT antes de devolver False."""


def challenge_lookup_statement(*, challenge_id: UUID):
    """Localiza apenas um candidato; não autoriza consumo ou acesso."""
    challenge = EmailConfirmationChallenge.__table__
    return select(challenge.c.id, challenge.c.identity_id).where(
        challenge.c.id == challenge_id,
    )


def email_identity_lock_statement(*, identity_id: UUID):
    identity = UserIdentity.__table__
    return select(
        identity.c.id, identity.c.email, identity.c.status,
        identity.c.email_verified_at, identity.c.updated_at,
    ).where(identity.c.id == identity_id).with_for_update(of=identity)


def email_credential_lock_statement(*, identity_id: UUID):
    credential = IdentityCredential.__table__
    return select(
        credential.c.identity_id, credential.c.status,
    ).where(credential.c.identity_id == identity_id).with_for_update(
        of=credential,
    )


def challenge_lock_statement(*, challenge_id: UUID, identity_id: UUID):
    challenge = EmailConfirmationChallenge.__table__
    return select(
        challenge.c.id, challenge.c.identity_id,
        challenge.c.verifier_sha256, challenge.c.purpose,
        challenge.c.issued_at, challenge.c.expires_at,
        challenge.c.consumed_at, challenge.c.revoked_at,
    ).where(
        challenge.c.id == challenge_id,
        challenge.c.identity_id == identity_id,
    ).with_for_update(of=challenge)


def challenge_consume_statement(
    *, challenge_id: UUID, identity_id: UUID, verifier_sha256: bytes,
):
    challenge = EmailConfirmationChallenge.__table__
    return (
        update(challenge)
        .where(
            challenge.c.id == challenge_id,
            challenge.c.identity_id == identity_id,
            challenge.c.verifier_sha256 == verifier_sha256,
            challenge.c.purpose == "INITIAL_EMAIL",
            challenge.c.consumed_at.is_(None),
            challenge.c.revoked_at.is_(None),
            challenge.c.issued_at <= func.clock_timestamp(),
            challenge.c.expires_at > func.clock_timestamp(),
        )
        .values(consumed_at=func.clock_timestamp())
        .returning(challenge.c.id)
    )


def identity_verify_statement(*, identity_id: UUID, email: str):
    """Marca email confirmado, preservando PENDENTE e PENDING_EMAIL.

    A promoção para identidade ATIVA, credencial ACTIVE e PJ APTO depende de
    fluxos e decisões separados; não conceder acesso como efeito do desafio.
    """
    identity = UserIdentity.__table__
    return (
        update(identity)
        .where(
            identity.c.id == identity_id,
            identity.c.email == email,
            identity.c.status == "PENDENTE",
            identity.c.email_verified_at.is_(None),
        )
        .values(email_verified_at=func.clock_timestamp())
        .returning(identity.c.id)
    )


def confirm_initial_email_within_transaction(
    connection: Connection, *,
    challenge_id: UUID, identity_id: UUID, candidate: bytes,
) -> bool:
    """Consome H após I→C→H no SAVEPOINT; o chamador possui a transação externa.

    Uma negação reverte o SAVEPOINT e libera os locks nele adquiridos. Sucesso
    libera apenas o SAVEPOINT; não confirma a transação externa nem emite token.
    """
    if (
        not isinstance(challenge_id, UUID) or challenge_id.int == 0
        or not isinstance(identity_id, UUID) or identity_id.int == 0
        or challenge_id == identity_id
        or type(candidate) is not bytes or len(candidate) != 32
    ):
        raise TransactionGateError("EMAIL_CONFIRMATION_DENIED")
    require_pg_transaction(connection, denial="EMAIL_CONFIRMATION_DENIED")

    try:
        with connection.begin_nested():
            found = connection.execute(challenge_lookup_statement(
                challenge_id=challenge_id,
            )).one_or_none()
            if found is None or found[0] != challenge_id or found[1] != identity_id:
                raise _EmailDenied

            identity = connection.execute(email_identity_lock_statement(
                identity_id=identity_id,
            )).one_or_none()
            if identity is None or identity[0] != identity_id:
                raise _EmailDenied

            credential = connection.execute(email_credential_lock_statement(
                identity_id=identity_id,
            )).one_or_none()
            if credential is None or credential[0] != identity_id:
                raise _EmailDenied

            challenge = connection.execute(challenge_lock_statement(
                challenge_id=challenge_id, identity_id=identity_id,
            )).one_or_none()
            if (challenge is None or challenge[0] != challenge_id
                    or challenge[1] != identity_id):
                raise _EmailDenied

            now = connection.execute(select(func.clock_timestamp())).scalar_one()
            if identity[3] is not None or credential[1] != "PENDING_EMAIL":
                raise _EmailDenied
            facts = EmailFacts(
                challenge_identity_id=challenge[1],
                identity_id=identity[0],
                snapshot_email=identity[1],
                current_email=identity[1],
                identity_status=identity[2],
                purpose=challenge[3],
                issued_at=challenge[4],
                expires_at=challenge[5],
                consumed_at=challenge[6],
                revoked_at=challenge[7],
            )
            if not email_challenge_eligible(facts, now=now):
                raise _EmailDenied
            changed_at = identity[4]
            if (not isinstance(changed_at, datetime)
                    or changed_at.tzinfo is None
                    or changed_at.utcoffset() is None
                    or changed_at > challenge[4]):
                raise _EmailDenied
            expected = _digest(challenge[0], identity[0], identity[1], candidate)
            if not (
                type(challenge[2]) is bytes and len(challenge[2]) == 32
                and hmac.compare_digest(expected, challenge[2])
            ):
                raise _EmailDenied

            consumed = connection.execute(challenge_consume_statement(
                challenge_id=challenge_id, identity_id=identity_id,
                verifier_sha256=challenge[2],
            )).scalar_one_or_none()
            if consumed != challenge_id:
                raise _EmailDenied
            verified = connection.execute(identity_verify_statement(
                identity_id=identity_id, email=identity[1],
            )).scalar_one_or_none()
            if verified != identity_id:
                raise EmailConfirmationStorageUnavailable(
                    "EMAIL_CONFIRMATION_STORAGE_UNAVAILABLE"
                )
            return True
    except _EmailDenied:
        return False
    except Exception:
        raise EmailConfirmationStorageUnavailable(
            "EMAIL_CONFIRMATION_STORAGE_UNAVAILABLE"
        ) from None
