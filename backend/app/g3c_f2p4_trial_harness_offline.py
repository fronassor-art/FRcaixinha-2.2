"""C16-R12.221 — manifesto/auditoria de cenários F2P4 EXCLUSIVAMENTE OFFLINE.

Este módulo não produz SQL, não conecta ao PostgreSQL e não executa Alembic.
Nenhuma evidência aqui certifica uma migration ou concorrência física.
O executor real permanece BLOQUEADO até outras G2 e implementação auditada.
"""

from dataclasses import dataclass, fields
from enum import Enum


class HarnessBlocked(RuntimeError):
    """Negação padronizada sem SQL, identidades ou segredos."""


class Stage(str, Enum):
    VERIFY_SEPARATE_G2 = "VERIFY_SEPARATE_G2"
    VERIFY_RECOVERABLE_BACKUP = "VERIFY_RECOVERABLE_BACKUP"
    INVENTORY_PUBLIC_READ_ONLY = "INVENTORY_PUBLIC_READ_ONLY"
    REVIEW_ISOLATED_ALEMBIC = "REVIEW_ISOLATED_ALEMBIC"
    COMMIT_TRIAL_SCHEMA = "COMMIT_TRIAL_SCHEMA"
    VERIFY_LOCAL_FKS_AND_VERSION = "VERIFY_LOCAL_FKS_AND_VERSION"
    PREPARE_SYNTHETIC_FIXTURES = "PREPARE_SYNTHETIC_FIXTURES"
    COMMIT_SYNTHETIC_FIXTURES = "COMMIT_SYNTHETIC_FIXTURES"
    OPEN_CONNECTION_A = "OPEN_CONNECTION_A"
    OPEN_CONNECTION_B = "OPEN_CONNECTION_B"
    VERIFY_DISTINCT_BACKEND_PIDS = "VERIFY_DISTINCT_BACKEND_PIDS"
    TEST_UNIQUE_IDEMPOTENCY = "TEST_UNIQUE_IDEMPOTENCY"
    TEST_DIFFERENT_FINGERPRINT = "TEST_DIFFERENT_FINGERPRINT"
    TEST_SAVEPOINT_AND_ROLLBACK = "TEST_SAVEPOINT_AND_ROLLBACK"
    TEST_LOCK_ORDER_AND_TIMEOUT = "TEST_LOCK_ORDER_AND_TIMEOUT"
    STOP_BEFORE_IN05 = "STOP_BEFORE_IN05"
    CLOSE_A_AND_B = "CLOSE_A_AND_B"
    CLEANUP_TRIAL_OBJECTS = "CLEANUP_TRIAL_OBJECTS"
    VERIFY_PUBLIC_UNCHANGED = "VERIFY_PUBLIC_UNCHANGED"


SCHEMA = "frc22_c16_trial_c16r12"
# Fonte de verdade imutavel por conteudo; nao usar o alias publico TABLES
# como oraculo de validacao (o nome pode ser reassociado em runtime).
_CANONICAL_TABLES = (
    "user_identities",
    "contracting_parties",
    "identity_credentials",
    "email_confirmation_challenges",
    "registration_idempotency",
    "identity_sessions",
)
TABLES = _CANONICAL_TABLES
# A tupla de identidades Enum fica capturada antes de eventual reassociacao
# de STAGES; nao depende do alias publico durante a validacao.
_CANONICAL_STAGES = tuple(Stage)
STAGES = _CANONICAL_STAGES


@dataclass(frozen=True, slots=True)
class ForeignKeyBoundary:
    source_schema: str
    source_table: str
    source_columns: tuple[str, ...]
    target_schema: str
    target_table: str
    target_columns: tuple[str, ...]


def _fk(source: str, source_cols: tuple[str, ...], target: str,
        target_cols: tuple[str, ...]) -> ForeignKeyBoundary:
    return ForeignKeyBoundary(SCHEMA, source, source_cols, SCHEMA, target, target_cols)


# Matriz de FK necessária ao subconjunto G3-C; NÃO representa por si
# só o DDL equivalente completo de colunas, checks, índices e UNIQUE.
# Referência CANÔNICA composta apenas de tuples/strings nativas imutáveis.
# Nunca validar contra ForeignKeyBoundary global: frozen=True ainda permite
# object.__setattr__ em instâncias expostas por um processo Python.
_CANONICAL_FK_SPECS = (
    ("contracting_parties", ("pf_user_id",), "user_identities", ("id",)),
    ("contracting_parties", ("representative_user_id",), "user_identities", ("id",)),
    ("contracting_parties", ("initial_registration_identity_id",),
     "user_identities", ("id",)),
    ("identity_credentials", ("identity_id",), "user_identities", ("id",)),
    ("email_confirmation_challenges", ("identity_id",),
     "user_identities", ("id",)),
    ("registration_idempotency", ("identity_id",), "user_identities", ("id",)),
    ("registration_idempotency", ("party_id",), "contracting_parties", ("id",)),
    ("registration_idempotency", ("party_id", "identity_id"),
     "contracting_parties", ("id", "initial_registration_identity_id")),
    ("identity_sessions", ("identity_id",), "user_identities", ("id",)),
)

_CANONICAL_FK_VALUES = tuple(
    (SCHEMA, source, source_columns, SCHEMA, target, target_columns)
    for source, source_columns, target, target_columns in _CANONICAL_FK_SPECS
)
REQUIRED_FKS = tuple(_fk(*spec) for spec in _CANONICAL_FK_SPECS)
_FK_FIELD_NAMES = (
    "source_schema", "source_table", "source_columns",
    "target_schema", "target_table", "target_columns",
)



@dataclass(frozen=True, slots=True)
class OfflineHarnessManifest:
    database: str = "frcaixinha_2_2_dev"
    role: str = "frc22_trial_c16r12"
    schema: str = SCHEMA
    authoritative_revision: str = "f2p4_20261022"
    repository_commit: str = "12a1e3f25197b98442c225a5c1ef86044c2dd22f"
    backup_sha256: str = (
        "a10fb867ef77d2a13994cb3e2c253003ced814b28f35026a42c58e78fee17337"
    )
    trial_version_schema: str = SCHEMA
    trial_version_table: str = "alembic_version_trial"
    tables: tuple[str, ...] = TABLES
    foreign_keys: tuple[ForeignKeyBoundary, ...] = REQUIRED_FKS
    stages: tuple[Stage, ...] = STAGES
    in05_triggers_enabled: bool = False


EXPECTED_MANIFEST = OfflineHarnessManifest()

# Os valores de fronteira são independentes de EXPECTED_MANIFEST (mutável por
# object.__setattr__). Cada entrada contém apenas str nativa, sem __eq__ externo.
_CANONICAL_SCALARS = (
    ("database", "frcaixinha_2_2_dev"),
    ("role", "frc22_trial_c16r12"),
    ("schema", "frc22_c16_trial_c16r12"),
    ("authoritative_revision", "f2p4_20261022"),
    ("repository_commit", "12a1e3f25197b98442c225a5c1ef86044c2dd22f"),
    ("backup_sha256", "a10fb867ef77d2a13994cb3e2c253003ced814b28f35026a42c58e78fee17337"),
    ("trial_version_schema", "frc22_c16_trial_c16r12"),
    ("trial_version_table", "alembic_version_trial"),
)
_CANONICAL_FIELD_NAMES = tuple(name for name, _ in _CANONICAL_SCALARS) + (
    "tables", "foreign_keys", "stages", "in05_triggers_enabled",
)



@dataclass(frozen=True, slots=True)
class OfflineHarnessReport:
    manifest: OfflineHarnessManifest
    status: str
    database_connected: bool
    migration_executed: bool
    two_connections_verified: bool
    schema_created: bool
    in05_tested: bool
    cleanup_performed: bool
    future_g2_required: bool


def _deny() -> None:
    raise HarnessBlocked("F2P4_221_OFFLINE_SCOPE_DENIED")


def _strings_exact(candidate: object, reference: tuple[str, ...]) -> None:
    if type(candidate) is not tuple or len(candidate) != len(reference):
        _deny()
    for value, expected in zip(candidate, reference):
        if type(value) is not str or value != expected:
            _deny()


def _foreign_keys_exact(candidate: object) -> None:
    if type(candidate) is not tuple or len(candidate) != len(_CANONICAL_FK_VALUES):
        _deny()
    for fk, required_values in zip(candidate, _CANONICAL_FK_VALUES):
        if type(fk) is not ForeignKeyBoundary:
            _deny()
        for field_name, expected in zip(_FK_FIELD_NAMES, required_values):
            try:
                actual = getattr(fk, field_name)
            except AttributeError:
                _deny()
            if type(expected) is str:
                if type(actual) is not str or actual != expected:
                    _deny()
            else:
                _strings_exact(actual, expected)


def _stages_exact(candidate: object) -> None:
    if type(candidate) is not tuple or len(candidate) != len(_CANONICAL_STAGES):
        _deny()
    for stage, expected in zip(candidate, _CANONICAL_STAGES):
        if type(stage) is not Stage or stage is not expected:
            _deny()


def validate_manifest(manifest: OfflineHarnessManifest) -> None:
    """Nega valores adulterados sem confiar nas instâncias globais expostas."""
    if type(manifest) is not OfflineHarnessManifest:
        _deny()
    # Falha segura se a classe ganhar novos campos não contemplados aqui.
    if tuple(field.name for field in fields(OfflineHarnessManifest)) != _CANONICAL_FIELD_NAMES:
        _deny()
    for field_name, expected in _CANONICAL_SCALARS:
        try:
            actual = getattr(manifest, field_name)
        except AttributeError:
            _deny()
        if type(actual) is not str or actual != expected:
            _deny()
    try:
        tables = manifest.tables
        foreign_keys = manifest.foreign_keys
        stages = manifest.stages
        in05 = manifest.in05_triggers_enabled
    except AttributeError:
        _deny()
    _strings_exact(tables, _CANONICAL_TABLES)
    _foreign_keys_exact(foreign_keys)
    _stages_exact(stages)
    if type(in05) is not bool or in05 is not False:
        _deny()



def build_offline_harness(
    manifest: OfflineHarnessManifest = EXPECTED_MANIFEST,
) -> OfflineHarnessReport:
    """Examina apenas objetos Python; não valida nem executa SQL."""
    validate_manifest(manifest)
    return OfflineHarnessReport(
        manifest=manifest,
        status="OFFLINE_MANIFEST_ONLY",
        database_connected=False,
        migration_executed=False,
        two_connections_verified=False,
        schema_created=False,
        in05_tested=False,
        cleanup_performed=False,
        future_g2_required=True,
    )


def run_physical_trial(*_args: object, **_kwargs: object) -> None:
    """Proibido, mesmo se argumentos simularem uma aprovação G2."""
    raise HarnessBlocked("F2P4_221_PHYSICAL_TRIAL_NOT_AUTHORIZED")
