"""IN-02 — proposta de escrita única PF/PJ com replay seguro, NÃO ATIVADA.

Dependências futuras: F2P4, transações PostgreSQL reais, HMAC originado no
servidor e prova de titularidade PF/PJ/representação aprovadas. Nenhuma API
chama este módulo. Nunca abrir conexão, instalar schema ou confirmar a
transação do chamador aqui.

O único retorno público são IDs já verificados; o segredo de e-mail NÃO
é devolvido em replay, nem pode ser entregue antes do COMMIT externo.
Esta proposta não implementa expurgo/reapropriação de RESERVED expirado.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import func, insert, select, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Connection

from app.db.models import (
    ContractingParty, EmailConfirmationChallenge, IdentityCredential,
    RegistrationIdempotency, UserIdentity,
)
from app.g3c_completed_replay_pg import fetch_verified_completed_replay
from app.g3c_transaction_guards_offline import TransactionGateError
from app.identity_draft import normalize_email
from app.initial_registration_bootstrap import InitialRegistrationIntent
from app.offline_credentials import PasswordDigest


class InitialRegistrationStorageUnavailable(RuntimeError):
    """Erro genérico sem CPF, CNPJ, e-mail, senha ou SQL interno."""


@dataclass(frozen=True, slots=True, repr=False)
class InitialRegistrationWriteResult:
    identity_id: UUID
    party_id: UUID
    created: bool

    def __repr__(self) -> str:
        return "InitialRegistrationWriteResult(<redacted>)"


def _uuid(value: object) -> bool:
    return isinstance(value, UUID) and value.int != 0


def _digest(value: object) -> bool:
    return type(value) is bytes and len(value) == 32


def _valid_intent(intent: object) -> bool:
    """Validação de forma: NÃO substitui origem e assinatura confiáveis."""
    try:
        if type(intent) is not InitialRegistrationIntent:
            return False
        registration = intent.registration
        identity, party, challenge = (
            registration.identity, registration.party, intent.challenge
        )
        return (
            _uuid(identity.id) and _uuid(party.id) and _uuid(challenge.id)
            and len({identity.id, party.id, challenge.id}) == 3
            and intent.auth_subject == f"local:{identity.id}"
            and identity.status == "PENDENTE"
            and party.status == "PRELIMINAR"
            and intent.credential_state == "PENDING_EMAIL"
            and normalize_email(identity.email) == identity.email
            and type(identity.phone) is str and len(identity.phone) == 11
            and type(identity.cpf_ciphertext) is bytes
            and bool(identity.cpf_ciphertext)
            and _digest(identity.cpf_lookup_hmac)
            and (
                (party.party_type == "PF"
                 and party.pf_user_id == identity.id
                 and party.representative_user_id is None
                 and party.tax_id_ciphertext is None
                 and party.tax_id_lookup_hmac is None)
                or
                (party.party_type == "PJ"
                 and party.pf_user_id is None
                 and party.representative_user_id == identity.id
                 and type(party.tax_id_ciphertext) is bytes
                 and bool(party.tax_id_ciphertext)
                 and _digest(party.tax_id_lookup_hmac))
            )
            and all(_digest(v) for v in (
                intent.origin_digest, intent.attempt_digest,
                intent.request_fingerprint, challenge.verifier_sha256))
            and challenge.identity_id == identity.id
            and challenge.email == identity.email
            and isinstance(challenge.issued_at, datetime)
            and challenge.issued_at.tzinfo is not None
            and challenge.issued_at.utcoffset() is not None
            and isinstance(challenge.expires_at, datetime)
            and challenge.expires_at.tzinfo is not None
            and challenge.expires_at.utcoffset() is not None
            and timedelta(0) < (
                challenge.expires_at - challenge.issued_at
            ) <= timedelta(minutes=10)
            and isinstance(intent.password_digest, PasswordDigest)
            and type(intent.password_digest.encoded) is str
            and 1 <= len(intent.password_digest.encoded) <= 160
            and intent.password_digest.encoded.startswith("scrypt$v1$")
        )
    except Exception:
        return False


def reserve_attempt_statement(intent: InitialRegistrationIntent, *, reservation_id: UUID):
    """UNIQUE (origin_digest, attempt_digest) arbitra escritores concorrentes."""
    table = RegistrationIdempotency.__table__
    stamp = func.statement_timestamp()
    return (
        pg_insert(table)
        .values(
            id=reservation_id,
            origin_digest=intent.origin_digest,
            attempt_digest=intent.attempt_digest,
            request_fingerprint=intent.request_fingerprint,
            state="RESERVED",
            created_at=stamp,
            expires_at=stamp + text("INTERVAL '15 minutes'"),
        )
        .on_conflict_do_nothing(
            constraint="uq_registration_idempotency_origin_attempt"
        )
        .returning(table.c.id)
    )


def complete_attempt_statement(
    intent: InitialRegistrationIntent, *, reservation_id: UUID,
):
    table = RegistrationIdempotency.__table__
    return (
        update(table)
        .where(
            table.c.id == reservation_id,
            table.c.origin_digest == intent.origin_digest,
            table.c.attempt_digest == intent.attempt_digest,
            table.c.request_fingerprint == intent.request_fingerprint,
            table.c.state == "RESERVED",
            table.c.expires_at > func.clock_timestamp(),
        )
        .values(
            state="COMPLETED",
            identity_id=intent.registration.identity.id,
            party_id=intent.registration.party.id,
        )
        .returning(table.c.id)
    )


def _write_identity_party_credential_challenge(
    connection: Connection, intent: InitialRegistrationIntent,
):
    """Todos os INSERTS ocorrem no SAVEPOINT pertencente ao chamador."""
    identity = intent.registration.identity
    party = intent.registration.party
    challenge = intent.challenge

    connection.execute(insert(UserIdentity.__table__).values(
        id=identity.id,
        name=identity.name,
        cpf_ciphertext=identity.cpf_ciphertext,
        cpf_lookup_hmac=identity.cpf_lookup_hmac,
        email=identity.email,
        phone=identity.phone,
        auth_subject=intent.auth_subject,
        status="PENDENTE",
    ))
    connection.execute(insert(ContractingParty.__table__).values(
        id=party.id,
        party_type=party.party_type,
        legal_name=party.legal_name,
        pf_user_id=party.pf_user_id,
        representative_user_id=party.representative_user_id,
        tax_id_ciphertext=party.tax_id_ciphertext,
        tax_id_lookup_hmac=party.tax_id_lookup_hmac,
        status="PRELIMINAR",
    ))
    connection.execute(insert(IdentityCredential.__table__).values(
        id=uuid4(),
        identity_id=identity.id,
        password_digest=intent.password_digest.encoded,
        status="PENDING_EMAIL",
    ))
    # Emissão física usa relógio PostgreSQL, NÃO o relógio da preparação.
    # statement_timestamp é constante nesta instrução: TTL exatos 10 minutos.
    stamp = func.statement_timestamp()
    connection.execute(insert(EmailConfirmationChallenge.__table__).values(
        id=challenge.id,
        identity_id=identity.id,
        verifier_sha256=challenge.verifier_sha256,
        purpose="INITIAL_EMAIL",
        issued_at=stamp,
        expires_at=stamp + text("INTERVAL '10 minutes'"),
    ))


def write_initial_registration_within_transaction(
    connection: Connection, *, intent: InitialRegistrationIntent,
) -> InitialRegistrationWriteResult:
    """Escrita ou replay com SAVEPOINT, sem COMMIT/ROLLBACK do chamador.

    Proposta para testes IN-02: não usar num ambiente real até auditoria
    independente, política antifraude e concorrência PostgreSQL autorizadas.
    O chamador PRECISA manter a transação externa até decidir COMMIT; o token
    de confirmação não é devolvido nem encaminhado por esta função.
    """
    if (
        not isinstance(connection, Connection)
        or not connection.in_transaction()
        or not _valid_intent(intent)
    ):
        raise TransactionGateError("REGISTRATION_WRITE_DENIED")

    try:
        with connection.begin_nested():
            reservation_id = uuid4()
            claimed = connection.execute(reserve_attempt_statement(
                intent, reservation_id=reservation_id,
            )).scalar_one_or_none()

            if claimed is None:
                # Não permitir que um RESERVED anterior seja apropriado.
                identity_id, party_id = fetch_verified_completed_replay(
                    connection,
                    origin_digest=intent.origin_digest,
                    attempt_digest=intent.attempt_digest,
                    request_fingerprint=intent.request_fingerprint,
                )
                return InitialRegistrationWriteResult(
                    identity_id, party_id, False,
                )

            if claimed != reservation_id:
                raise TransactionGateError("REGISTRATION_WRITE_DENIED")
            _write_identity_party_credential_challenge(connection, intent)
            completed = connection.execute(complete_attempt_statement(
                intent, reservation_id=reservation_id,
            )).scalar_one_or_none()
            if completed != reservation_id:
                # Condição expirada/conflito → reversão de TODOS os INSERTS.
                raise TransactionGateError("REGISTRATION_WRITE_DENIED")
            return InitialRegistrationWriteResult(
                intent.registration.identity.id,
                intent.registration.party.id, True,
            )
    except TransactionGateError:
        raise
    except Exception:
        raise InitialRegistrationStorageUnavailable(
            "REGISTRATION_STORAGE_UNAVAILABLE"
        ) from None
