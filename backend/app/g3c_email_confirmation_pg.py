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
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.engine import Connection

from app.db.models import (
    EmailConfirmationChallenge, IdentityCredential, UserIdentity,
)
from app.email_confirmation_offline import _digest
from app.g3c_transaction_guards_offline import (
    EmailFacts, TransactionGateError, email_challenge_eligible,
)


class EmailConfirmationStorageUnavailable(RuntimeError):
    """Erro genérico de falha transacional, sem detalhes de banco ou token."""


def challenge_lock_statement(*, challenge_id: UUID, identity_id: UUID):
    challenge = EmailConfirmationChallenge.__table__
    identity = UserIdentity.__table__
    credential = IdentityCredential.__table__
    return (
        select(
            challenge.c.id,
            challenge.c.identity_id,
            challenge.c.verifier_sha256,
            challenge.c.purpose,
            challenge.c.issued_at,
            challenge.c.expires_at,
            challenge.c.consumed_at,
            challenge.c.revoked_at,
            identity.c.id,
            identity.c.email,
            identity.c.status,
            identity.c.email_verified_at,
            credential.c.status,
        )
        .select_from(
            challenge.join(
                identity, challenge.c.identity_id == identity.c.id,
            ).join(
                credential, credential.c.identity_id == identity.c.id,
            )
        )
        .where(
            challenge.c.id == challenge_id,
            challenge.c.identity_id == identity_id,
        )
        .with_for_update(of=(challenge, identity, credential))
    )


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
    """Consome desafio e verifica contato num SAVEPOINT ou desfaz as duas ações.

    O chamador controla a transação EXTERNA e deve tratá-la como parte do fluxo
    maior de cadastro (inclusive COMMIT/ROLLBACK). A função não abre conexões,
    não confirma transação externa e não solicita nem emite tokens.
    """
    if (
        not isinstance(connection, Connection)
        or not connection.in_transaction()
        or not isinstance(challenge_id, UUID) or challenge_id.int == 0
        or not isinstance(identity_id, UUID) or identity_id.int == 0
        or challenge_id == identity_id
        or type(candidate) is not bytes or len(candidate) != 32
    ):
        raise TransactionGateError("EMAIL_CONFIRMATION_DENIED")

    try:
        # O savepoint impede persistir consumo parcial se a escrita de contato
        # falhar e a transação do chamador continuar.
        with connection.begin_nested():
            row = connection.execute(challenge_lock_statement(
                challenge_id=challenge_id, identity_id=identity_id,
            )).one_or_none()
            if row is None:
                return False
            now = connection.execute(select(func.clock_timestamp())).scalar_one()
            if row[11] is not None or row[12] != "PENDING_EMAIL":
                return False
            facts = EmailFacts(
                challenge_identity_id=row[1],
                identity_id=row[8],
                snapshot_email=row[9],
                current_email=row[9],
                identity_status=row[10],
                purpose=row[3],
                issued_at=row[4],
                expires_at=row[5],
                consumed_at=row[6],
                revoked_at=row[7],
            )
            if not email_challenge_eligible(facts, now=now):
                return False
            # A emissão criptograficamente vinculou o segredo ao e-mail de
            # origem. Aqui usamos o estado atual da fonte do servidor.
            expected = _digest(row[0], row[8], row[9], candidate)
            if not (
                type(row[2]) is bytes and len(row[2]) == 32
                and hmac.compare_digest(expected, row[2])
            ):
                return False

            consumed = connection.execute(challenge_consume_statement(
                challenge_id=challenge_id, identity_id=identity_id,
                verifier_sha256=row[2],
            )).scalar_one_or_none()
            if consumed != challenge_id:
                return False
            verified = connection.execute(identity_verify_statement(
                identity_id=identity_id, email=row[9],
            )).scalar_one_or_none()
            if verified != identity_id:
                # Não devolver False após consumir: FORÇAR rollback ao savepoint.
                raise EmailConfirmationStorageUnavailable(
                    "EMAIL_CONFIRMATION_STORAGE_UNAVAILABLE"
                )
            return True
    except Exception:
        raise EmailConfirmationStorageUnavailable(
            "EMAIL_CONFIRMATION_STORAGE_UNAVAILABLE"
        ) from None
