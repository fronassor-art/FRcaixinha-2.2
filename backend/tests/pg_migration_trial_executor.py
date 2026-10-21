"""Guarded C15/C16 trial runner; importing this module never opens a database.

This module is deliberately disabled. A later, separately reviewed change must
pin both approval constants to a disposable database and a checkpoint. Only
a private, short-lived trial connection is acquired after those gates pass.
This module does not create databases or read production credentials.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import file_digest
from pathlib import Path
import re
from threading import Lock
from types import CodeType, FunctionType, ModuleType

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from psycopg import Connection as PsycopgConnection
from psycopg.pq import TransactionStatus
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection as SQLAlchemyConnection, URL
from sqlalchemy.pool import NullPool


AUTHORITATIVE_DATABASE = "frcaixinha_2_2_dev"
TRIAL_DATABASE_PREFIX = "frcaixinha_2_2_c16_trial_"
TRIAL_ROLE_PREFIX = "frc22_trial_"
C15_REVISION = "c15r2_20261020"
C16_REVISION = "c16r5_20261020"
C15_TABLES = (
    "license_plans", "user_identities", "contracting_parties",
    "license_price_versions", "tenants", "cycles", "license_offers",
    "role_grants", "memberships", "term_acceptances",
    "license_payment_obligations", "quotas", "payments", "payment_attempts",
    "payment_reconciliation_events",
)
C16_TABLES = C15_TABLES + (
    "license_subscriptions", "license_entitlement_segments",
)

_REVISION_FILES = (
    (
        "c15r2_20261020_initial_schema.py",
        "d5b23fd54281242d6fc4837a860b3181a06ac57ece0ee4bfe32cedae04c4c420",
    ),
    (
        "c16r5_20261020_license_subscription_inactive.py",
        "f19dc054710e5a903de7ef26d35433b932e350f22932982531a65c7ce80620b2",
    ),
)
_REVISION_DIRECTORY = Path(__file__).resolve().parents[1] / "migrations" / "versions"
_REVISION_BINDING_LOCK = Lock()


@dataclass(frozen=True, slots=True)
class TrialTarget:
    host: str
    port: int
    database: str
    role: str


@dataclass(frozen=True, slots=True)
class TrialAuthorization:
    checkpoint: str
    target: TrialTarget


@dataclass(frozen=True, slots=True)
class TrialResult:
    upgrades: tuple[str, str]
    downgrades: tuple[str, str]
    rolled_back: bool


class TrialBlocked(RuntimeError):
    """No trial DDL may follow this failed gate."""


# No trial target or checkpoint has been approved for execution yet.
# They must be pinned by a separately authorized, reviewed code change.
APPROVED_TRIAL_TARGET: TrialTarget | None = None
APPROVED_TRIAL_CHECKPOINT: str | None = None


_IDENTITY_SQL = text(
    "SELECT current_database(), current_user, host(inet_server_addr()), "
    "inet_server_port(), current_setting('server_version_num')::integer, "
    "r.rolsuper, r.rolcreatedb, pg_is_in_recovery(), "
    "current_setting('transaction_read_only') "
    "FROM pg_catalog.pg_roles AS r WHERE r.rolname = current_user"
)
_RELATIONS_SQL = text(
    "SELECT n.nspname, c.relname, c.relkind "
    "FROM pg_catalog.pg_class AS c "
    "JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace "
    "WHERE n.nspname NOT IN ('pg_catalog', 'information_schema') "
    "AND n.nspname NOT LIKE 'pg_toast%' "
    "AND n.nspname NOT LIKE 'pg_temp_%' "
    "AND c.relkind IN ('r', 'p', 'v', 'm', 'S', 'f', 'i', 'I') "
    "ORDER BY n.nspname, c.relname"
)


def _validate_request(target: TrialTarget, authorization: TrialAuthorization) -> None:
    if not isinstance(target, TrialTarget):
        raise TrialBlocked("trial target is required")
    if target.database == AUTHORITATIVE_DATABASE:
        raise TrialBlocked("authoritative database is forbidden")
    if target.host != "127.0.0.1" or type(target.port) is not int or target.port != 5432:
        raise TrialBlocked("trial host or port is invalid")
    if type(target.database) is not str or not re.fullmatch(
        rf"{TRIAL_DATABASE_PREFIX}[a-z][a-z0-9_]{{0,31}}", target.database
    ):
        raise TrialBlocked("trial database name is invalid")
    if type(target.role) is not str or not re.fullmatch(
        rf"{TRIAL_ROLE_PREFIX}[a-z][a-z0-9_]{{0,31}}", target.role
    ):
        raise TrialBlocked("trial role name is invalid")
    if APPROVED_TRIAL_TARGET is None or target != APPROVED_TRIAL_TARGET:
        raise TrialBlocked("trial destination has no separate approval")
    if (
        APPROVED_TRIAL_CHECKPOINT is None
        or not isinstance(authorization, TrialAuthorization)
        or authorization.target != target
        or authorization.checkpoint != APPROVED_TRIAL_CHECKPOINT
    ):
        raise TrialBlocked("specific trial authorization is absent or mismatched")


def _sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def _frozen_revisions():
    for filename, expected_sha256 in _REVISION_FILES:
        try:
            actual_sha256 = _sha256_file(_REVISION_DIRECTORY / filename)
        except OSError as exc:
            raise TrialBlocked("frozen migration source is unavailable") from exc
        if actual_sha256 != expected_sha256:
            raise TrialBlocked("frozen migration source differs from checkpoint")

    from migrations.versions import c15r2_20261020_initial_schema as c15
    from migrations.versions import c16r5_20261020_license_subscription_inactive as c16

    if (
        c15.revision != C15_REVISION
        or c15.down_revision is not None
        or tuple(c15.TABLE_ORDER) != C15_TABLES
        or c16.revision != C16_REVISION
        or c16.down_revision != C15_REVISION
    ):
        raise TrialBlocked("migration chain differs from the frozen checkpoint")
    return c15, c16


def _validate_connection(connection) -> PsycopgConnection:
    if not isinstance(connection, SQLAlchemyConnection):
        raise TrialBlocked("an explicit SQLAlchemy connection is required")
    try:
        return _inspect_transactional_connection(connection)
    except TrialBlocked:
        raise
    except Exception:
        raise TrialBlocked("trial connection inspection failed") from None


def _inspect_transactional_connection(connection: SQLAlchemyConnection) -> PsycopgConnection:
    if (
        connection.dialect.name != "postgresql"
        or connection.dialect.driver != "psycopg"
    ):
        raise TrialBlocked("an explicit PostgreSQL psycopg connection is required")
    if connection.closed is not False or connection.invalidated is not False:
        raise TrialBlocked("trial connection is closed, invalidated, or unverified")
    if (
        not callable(getattr(connection, "execute", None))
        or not callable(getattr(connection, "begin", None))
        or not callable(getattr(connection, "in_transaction", None))
        or not callable(getattr(connection, "get_isolation_level", None))
        or not callable(getattr(connection, "get_execution_options", None))
    ):
        raise TrialBlocked("trial connection interface is incomplete")
    if connection.in_transaction() is not False:
        raise TrialBlocked("trial connection already has a transaction")
    options = connection.get_execution_options()
    if not isinstance(options, Mapping):
        raise TrialBlocked("trial execution options are unavailable")
    requested_isolation = options.get("isolation_level")
    if requested_isolation is not None and requested_isolation not in (
        "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"
    ):
        raise TrialBlocked("trial execution options require transactional DDL")
    driver = connection.connection.driver_connection
    if not isinstance(driver, PsycopgConnection):
        raise TrialBlocked("trial psycopg driver connection is unavailable")
    if driver.autocommit is not False:
        raise TrialBlocked("trial psycopg driver must have autocommit disabled")
    # SQLAlchemy's get_isolation_level() never reports DBAPI AUTOCOMMIT.
    # The driver check above is the decisive transactional gate.
    if connection.get_isolation_level() not in (
        "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"
    ):
        raise TrialBlocked("trial requires transactional PostgreSQL DDL")
    return driver


def _require_active_transaction(connection: SQLAlchemyConnection, driver: PsycopgConnection) -> None:
    try:
        if connection.closed is not False or connection.invalidated is not False:
            raise TrialBlocked("trial connection is no longer valid")
        if connection.in_transaction() is not True:
            raise TrialBlocked("SQLAlchemy transaction is not active")
        if connection.connection.driver_connection is not driver:
            raise TrialBlocked("trial driver connection changed")
        if driver.autocommit is not False:
            raise TrialBlocked("trial driver switched to autocommit")
        if driver.info.transaction_status is not TransactionStatus.INTRANS:
            raise TrialBlocked("trial PostgreSQL transaction is not active")
    except TrialBlocked:
        raise
    except Exception:
        raise TrialBlocked("trial transaction inspection failed") from None


def _validate_identity(row, target: TrialTarget) -> None:
    if row is None or len(row) != 9:
        raise TrialBlocked("PostgreSQL identity is unavailable")
    database, role, host, port, version, superuser, createdb, recovery, read_only = row
    if database == AUTHORITATIVE_DATABASE:
        raise TrialBlocked("authoritative database is forbidden")
    if (database, role, host, port) != (
        target.database, target.role, target.host, target.port
    ):
        raise TrialBlocked("PostgreSQL destination identity differs from approval")
    if superuser is not False or createdb is not False:
        raise TrialBlocked("superuser or CREATEDB role is forbidden")
    if type(version) is not int or not 180000 <= version < 190000:
        raise TrialBlocked("PostgreSQL version must be 18.x")
    if recovery is not False or read_only != "off":
        raise TrialBlocked("trial server must allow transactional DDL")


def _relations(connection) -> tuple[tuple[str, str, str], ...]:
    rows = connection.execute(_RELATIONS_SQL).all()
    try:
        relations = tuple(tuple(row) for row in rows)
    except (TypeError, ValueError) as exc:
        raise TrialBlocked("relation inventory is unavailable") from exc
    if any(
        len(row) != 3 or any(type(value) is not str for value in row)
        for row in relations
    ):
        raise TrialBlocked("relation inventory is malformed")
    return relations


def _require_tables(relations, expected: tuple[str, ...]) -> None:
    if not expected and relations:
        raise TrialBlocked("trial database is not empty")
    if expected and (
        {name for schema, name, kind in relations if schema == "public" and kind in ("r", "p")}
        != set(expected)
        or any(schema != "public" for schema, _, _ in relations)
    ):
        raise TrialBlocked("trial schema differs from the expected migration stage")


def _isolated_revision_function(revision: ModuleType, method: str, operations: Operations) -> FunctionType:
    """Bind `op` only in a fresh function namespace, never in a revision module."""
    expected_references = {
        (C15_REVISION, "upgrade"): {"op", "sa", "SCHEMA_DDL"},
        (C15_REVISION, "downgrade"): {"op", "sa", "TABLE_ORDER"},
        (C16_REVISION, "upgrade"): {"op", "sa", "postgresql"},
        (C16_REVISION, "downgrade"): {"op"},
    }
    if not isinstance(revision, ModuleType):
        raise TrialBlocked("frozen revision module is invalid")
    module_globals = vars(revision)
    expected = expected_references.get((module_globals.get("revision"), method))
    source = module_globals.get(method)
    if expected is None or not isinstance(source, FunctionType):
        raise TrialBlocked("frozen migration entry point is invalid")
    code = source.__code__
    if (
        source.__globals__ is not module_globals
        or source.__closure__ is not None
        or source.__defaults__ is not None
        or source.__kwdefaults__ is not None
        or code.co_freevars
        or code.co_cellvars
        or any(isinstance(constant, CodeType) for constant in code.co_consts)
        or code.co_argcount
        or code.co_posonlyargcount
        or code.co_kwonlyargcount
        or {name for name in code.co_names if name in module_globals} != expected
    ):
        raise TrialBlocked("frozen migration cannot be safely isolated")
    if "sa" in expected and module_globals["sa"] is not sqlalchemy:
        raise TrialBlocked("frozen SQLAlchemy reference differs from checkpoint")
    if "postgresql" in expected and module_globals["postgresql"] is not postgresql:
        raise TrialBlocked("frozen PostgreSQL reference differs from checkpoint")

    # Only the names used by the audited entry point are copied. No helper,
    # mutable revision-global, or original module namespace is shared.
    private_globals = {"__builtins__": {"reversed": reversed}, "op": operations}
    for name in expected - {"op"}:
        value = module_globals[name]
        if name in ("SCHEMA_DDL", "TABLE_ORDER") and not (
            type(value) is tuple and all(type(item) is str for item in value)
        ):
            raise TrialBlocked("frozen migration constants are invalid")
        private_globals[name] = value
    return FunctionType(code, private_globals, source.__name__)


def _invoke(revision, method: str, operations: Operations) -> None:
    _isolated_revision_function(revision, method, operations)()


def run_trial(*, target: TrialTarget, authorization: TrialAuthorization, trial_password: str) -> TrialResult:
    """Rehearse C15/C16 on one privately owned trial connection, then roll back.

    The disabled approval gate runs before a connection is acquired. A fresh
    NullPool engine is local to this call and never exposed to the caller.
    The caller provides a trial-only password explicitly; no environment or
    production credential is read by this module.
    """
    _validate_request(target, authorization)
    c15, c16 = _frozen_revisions()
    if type(trial_password) is not str or not trial_password:
        raise TrialBlocked("an explicit trial credential is required")

    url = URL.create(
        "postgresql+psycopg", username=target.role, password=trial_password,
        host=target.host, port=target.port, database=target.database,
    )
    engine = sqlalchemy.create_engine(url, poolclass=NullPool)
    try:
        with engine.connect() as connection:
            driver = _validate_connection(connection)
            transaction = connection.begin()
            try:
                _validate_identity(connection.execute(_IDENTITY_SQL).one_or_none(), target)
                _require_tables(_relations(connection), ())
                _require_active_transaction(connection, driver)

                context = MigrationContext.configure(connection=connection)
                operations = Operations(context)
                with _REVISION_BINDING_LOCK:
                    _require_active_transaction(connection, driver)
                    _invoke(c15, "upgrade", operations)
                    _require_tables(_relations(connection), C15_TABLES)
                    _require_active_transaction(connection, driver)
                    _invoke(c16, "upgrade", operations)
                    _require_tables(_relations(connection), C16_TABLES)
                    _require_active_transaction(connection, driver)
                    _invoke(c16, "downgrade", operations)
                    _require_tables(_relations(connection), C15_TABLES)
                    _require_active_transaction(connection, driver)
                    _invoke(c15, "downgrade", operations)
                    _require_tables(_relations(connection), ())
                return TrialResult(
                    upgrades=(C15_REVISION, C16_REVISION),
                    downgrades=(C16_REVISION, C15_REVISION),
                    rolled_back=True,
                )
            finally:
                transaction.rollback()
    finally:
        engine.dispose()
