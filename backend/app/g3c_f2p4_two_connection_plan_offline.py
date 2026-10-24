"""C16-R12.210 — executor de PLANO offline de ensaio F2P4, não operacional.

NÃO conecta ao PostgreSQL, NÃO aplica Alembic, NÃO cria schema,
NÃO inicia threads nem registra aprovação G2 para o teste físico.
O relatório é uma revisão de passos; nunca é evidência de concorrência real.
"""

from dataclasses import dataclass
from enum import Enum


class OfflineTrialBlocked(RuntimeError):
    """Negação fixa, sem SQL, segredo ou identificadores pessoais."""


class TrialStage(str, Enum):
    APPROVAL = "APPROVAL"
    VERIFY_BACKUP = "VERIFY_BACKUP"
    PREFLIGHT_READ_ONLY = "PREFLIGHT_READ_ONLY"
    ALEMBIC_PREPARE_TRIAL_SCHEMA = "ALEMBIC_PREPARE_TRIAL_SCHEMA"
    COMMIT_SHARED_SCHEMA = "COMMIT_SHARED_SCHEMA"
    VERIFY_ISOLATION = "VERIFY_ISOLATION"
    PREPARE_SYNTHETIC_FIXTURES = "PREPARE_SYNTHETIC_FIXTURES"
    COMMIT_SHARED_FIXTURES = "COMMIT_SHARED_FIXTURES"
    VERIFY_TWO_DISTINCT_SESSIONS = "VERIFY_TWO_DISTINCT_SESSIONS"
    TEST_UNIQUE_IDEMPOTENCY = "TEST_UNIQUE_IDEMPOTENCY"
    TEST_FINGERPRINT_CONFLICT = "TEST_FINGERPRINT_CONFLICT"
    TEST_SAVEPOINT_AND_ROLLBACK = "TEST_SAVEPOINT_AND_ROLLBACK"
    TEST_LOCK_ORDER_AND_TIMEOUT = "TEST_LOCK_ORDER_AND_TIMEOUT"
    STOP_BEFORE_IN05_REVOCATION = "STOP_BEFORE_IN05_REVOCATION"
    CLOSE_ALL_SESSIONS = "CLOSE_ALL_SESSIONS"
    ALEMBIC_CLEANUP_TRIAL_SCHEMA = "ALEMBIC_CLEANUP_TRIAL_SCHEMA"
    FINAL_READ_ONLY_INTEGRITY = "FINAL_READ_ONLY_INTEGRITY"


@dataclass(frozen=True, slots=True)
class TrialScope:
    database: str = "frcaixinha_2_2_dev"
    role: str = "frc22_trial_c16r12"
    schema: str = "frc22_c16_trial_c16r12"
    alembic_version: str = "f2p4_20261022"
    repository_commit: str = "1685d987e60ade2a7b2373614bd18fa52064b9f8"
    backup_sha256: str = (
        "a10fb867ef77d2a13994cb3e2c253003ced814b28f35026a42c58e78fee17337"
    )


EXPECTED_SCOPE = TrialScope()

# Passos a revisar ANTES de desenvolver um executor físico. As fases com COMMIT
# não são simuladas como writes: registram a exigência de visibilidade entre A/B.
PLAN_STAGES = tuple(TrialStage)


@dataclass(frozen=True, slots=True)
class OfflinePlanReport:
    scope: TrialScope
    stages: tuple[TrialStage, ...]
    status: str
    connected_to_database: bool
    ddl_executed: bool
    physical_concurrency_verified: bool
    in05_revocation_verified: bool
    future_g2_required: bool


def validate_scope(scope: TrialScope) -> None:
    """Exige seis strings nativas exatas; não invoca igualdade do chamador."""
    if type(scope) is not TrialScope:
        raise OfflineTrialBlocked("F2P4_OFFLINE_SCOPE_DENIED")
    for field in (
        "database", "role", "schema", "alembic_version",
        "repository_commit", "backup_sha256",
    ):
        value = getattr(scope, field)
        if type(value) is not str or value != getattr(EXPECTED_SCOPE, field):
            raise OfflineTrialBlocked("F2P4_OFFLINE_SCOPE_DENIED")


def build_offline_plan(scope: TrialScope = EXPECTED_SCOPE) -> OfflinePlanReport:
    """Constrói roteiro IMUTÁVEL sem IO, SQL, Alembic ou conexão."""
    validate_scope(scope)
    return OfflinePlanReport(
        scope=scope,
        stages=PLAN_STAGES,
        status="OFFLINE_PLAN_ONLY",
        connected_to_database=False,
        ddl_executed=False,
        physical_concurrency_verified=False,
        in05_revocation_verified=False,
        future_g2_required=True,
    )


def run_physical_trial(*_args: object, **_kwargs: object) -> None:
    """Entrypoint real propositalmente inexistente até nova G2 e revisão."""
    raise OfflineTrialBlocked("F2P4_PHYSICAL_TRIAL_NOT_AUTHORIZED")
