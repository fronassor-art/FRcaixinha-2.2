"""Offline gates for the disabled C15/C16 PostgreSQL trial executor.

All connections and Alembic operations here are mocks. These tests do not
prove that PostgreSQL enforces the schema or that a real restore succeeds.
"""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import importlib
from pathlib import Path
from threading import Barrier
from types import FunctionType, ModuleType
import unittest
from unittest.mock import MagicMock, Mock, patch, PropertyMock

from psycopg import Connection as PsycopgConnection
from psycopg.pq import TransactionStatus
from sqlalchemy.engine import Connection as SQLAlchemyConnection
from sqlalchemy.pool import NullPool

import pg_migration_trial_executor as trial


_UNSET = object()


class FakeResult:
    def __init__(self, *, one=None, rows=()):
        self.one = one
        self.rows = rows

    def one_or_none(self):
        return self.one

    def all(self):
        return self.rows


class MigrationTrialExecutorOfflineTests(unittest.TestCase):
    def setUp(self):
        self.target = trial.TrialTarget(
            host="127.0.0.1", port=5432,
            database="frcaixinha_2_2_c16_trial_unit",
            role="frc22_trial_unit",
        )
        self.authorization = trial.TrialAuthorization(
            checkpoint="C16-R11.8-OFFLINE-UNIT", target=self.target
        )

    @contextmanager
    def approved_for_mock_only(self):
        with (
            patch.object(trial, "APPROVED_TRIAL_TARGET", self.target),
            patch.object(
                trial, "APPROVED_TRIAL_CHECKPOINT", self.authorization.checkpoint
            ),
        ):
            yield

    def identity(self, **changes):
        values = {
            "database": self.target.database,
            "role": self.target.role,
            "host": self.target.host,
            "port": self.target.port,
            "version": 180002,
            "superuser": False,
            "createdb": False,
            "recovery": False,
            "read_only": "off",
        }
        values.update(changes)
        return tuple(values.values())

    @staticmethod
    def table_rows(names):
        return tuple(("public", name, "r") for name in names)

    def connection(self, *, identity=None, inventories=None):
        if identity is None:
            identity = self.identity()
        if inventories is None:
            inventories = (
                (),
                self.table_rows(trial.C15_TABLES),
                self.table_rows(trial.C16_TABLES),
                self.table_rows(trial.C15_TABLES),
                (),
            )
        inventory = iter(inventories)
        connection = Mock(spec=SQLAlchemyConnection)
        connection.dialect = Mock()
        connection.dialect.name = "postgresql"
        connection.dialect.driver = "psycopg"
        connection.closed = False
        connection.invalidated = False
        connection.in_transaction.side_effect = lambda: connection.begin.called
        connection.get_execution_options.return_value = {}
        connection.get_isolation_level.return_value = "READ COMMITTED"
        driver = Mock(spec=PsycopgConnection)
        driver.autocommit = False
        driver.info.transaction_status = TransactionStatus.INTRANS
        connection.connection = Mock()
        connection.connection.driver_connection = driver

        def execute(statement):
            if statement is trial._IDENTITY_SQL:
                return FakeResult(one=identity)
            if statement is trial._RELATIONS_SQL:
                return FakeResult(rows=next(inventory))
            self.fail("executor issued SQL outside the two fixed read-only queries")

        connection.execute.side_effect = execute
        return connection

    @staticmethod
    def recording_operations():
        operations = Mock()
        events = []
        for name in (
            "execute", "create_unique_constraint", "create_table", "create_index",
            "drop_index", "drop_table", "drop_constraint",
        ):
            getattr(operations, name).side_effect = (
                lambda *args, _name=name, **kwargs:
                events.append((_name, args, kwargs))
            )
        return operations, events

    @contextmanager
    def private_engine_for_mock_only(self, connection):
        engine = MagicMock()
        engine.connect.return_value.__enter__.return_value = connection
        with patch("sqlalchemy.create_engine", return_value=engine) as create_engine:
            yield create_engine, engine

    def run_with_mock_operations(self, connection, operations):
        with (
            self.approved_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (create_engine, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock())
            as configure,
            patch.object(trial, "Operations", return_value=operations),
        ):
            result = trial.run_trial(
                target=self.target, authorization=self.authorization,
                trial_password="offline-unit-only",
            )
        return result, configure, create_engine, engine

    def assert_no_ddl_after_rejection(
        self, connection, *, target=_UNSET, authorization=_UNSET
    ):
        if target is _UNSET:
            target = self.target
        if authorization is _UNSET:
            authorization = self.authorization
        with (
            self.private_engine_for_mock_only(connection) as (create_engine, engine),
            patch.object(trial.MigrationContext, "configure") as configure,
            patch.object(trial, "Operations") as operations,
        ):
            with self.assertRaises(trial.TrialBlocked):
                trial.run_trial(
                    target=target, authorization=authorization,
                    trial_password="offline-unit-only",
                )
        configure.assert_not_called()
        operations.assert_not_called()
        if create_engine.called:
            engine.dispose.assert_called_once()

    def test_import_has_no_connection_or_execution_side_effect(self):
        with (
            patch("sqlalchemy.create_engine") as create_engine,
            patch("psycopg.connect") as connect,
        ):
            importlib.reload(trial)
        create_engine.assert_not_called()
        connect.assert_not_called()
        self.assertIsNone(trial.APPROVED_TRIAL_TARGET)
        self.assertIsNone(trial.APPROVED_TRIAL_CHECKPOINT)

    def test_frozen_sources_and_revision_chain(self):
        base = Path(trial.__file__).resolve().parents[1] / "migrations" / "versions"
        for filename, expected in trial._REVISION_FILES:
            with self.subTest(filename=filename):
                self.assertEqual(trial._sha256_file(base / filename), expected)
        c15, c16 = trial._frozen_revisions()
        self.assertEqual((c15.revision, c16.revision), (
            "c15r2_20261020", "c16r5_20261020"
        ))
        self.assertIsNone(c15.down_revision)
        self.assertEqual(c16.down_revision, c15.revision)
        self.assertEqual(len(trial.C15_TABLES), 15)
        self.assertEqual(len(trial.C16_TABLES), 17)

    def test_default_gate_refuses_even_valid_synthetic_destination(self):
        connection = self.connection()
        self.assert_no_ddl_after_rejection(connection)
        connection.begin.assert_not_called()
        connection.execute.assert_not_called()

    def test_authoritative_database_is_rejected_even_if_policy_is_misconfigured(self):
        forbidden = trial.TrialTarget(
            "127.0.0.1", 5432, trial.AUTHORITATIVE_DATABASE, "frc22_owner"
        )
        authorization = trial.TrialAuthorization("incorrect-approval", forbidden)
        connection = self.connection()
        with (
            patch.object(trial, "APPROVED_TRIAL_TARGET", forbidden),
            patch.object(trial, "APPROVED_TRIAL_CHECKPOINT", "incorrect-approval"),
        ):
            self.assert_no_ddl_after_rejection(
                connection, target=forbidden, authorization=authorization
            )
        connection.begin.assert_not_called()
        connection.execute.assert_not_called()

    def test_unknown_missing_and_malformed_destinations_fail_before_sql(self):
        invalid = (
            None,
            trial.TrialTarget("0.0.0.0", 5432, self.target.database, self.target.role),
            trial.TrialTarget("127.0.0.1", 5433, self.target.database, self.target.role),
            trial.TrialTarget("127.0.0.1", 5432, "", self.target.role),
            trial.TrialTarget("127.0.0.1", 5432, "other_database", self.target.role),
            trial.TrialTarget("127.0.0.1", 5432, self.target.database, "frc22_owner"),
            trial.TrialTarget(
                "127.0.0.1", 5432, "frcaixinha_2_2_c16_trial_other",
                self.target.role,
            ),
        )
        with self.approved_for_mock_only():
            for destination in invalid:
                with self.subTest(destination=destination):
                    connection = self.connection()
                    authorization = trial.TrialAuthorization(
                        self.authorization.checkpoint, destination
                    )
                    self.assert_no_ddl_after_rejection(
                        connection, target=destination, authorization=authorization
                    )
                    connection.begin.assert_not_called()
                    connection.execute.assert_not_called()

    def test_specific_authorization_is_required(self):
        with self.approved_for_mock_only():
            for authorization in (
                None,
                trial.TrialAuthorization("wrong-checkpoint", self.target),
                trial.TrialAuthorization(
                    self.authorization.checkpoint,
                    trial.TrialTarget(
                        "127.0.0.1", 5432,
                        "frcaixinha_2_2_c16_trial_other", self.target.role,
                    ),
                ),
            ):
                with self.subTest(authorization=authorization):
                    connection = self.connection()
                    with (
                        patch("sqlalchemy.create_engine") as create_engine,
                        patch.object(trial.MigrationContext, "configure") as configure,
                        patch.object(trial, "Operations") as operations,
                    ):
                        with self.assertRaises(trial.TrialBlocked):
                            trial.run_trial(
                                target=self.target, authorization=authorization,
                                trial_password="offline-unit-only",
                            )
                    create_engine.assert_not_called()
                    configure.assert_not_called()
                    operations.assert_not_called()
                    connection.begin.assert_not_called()
                    connection.execute.assert_not_called()

    def test_connection_must_be_explicit_postgresql_and_transactional(self):
        with self.approved_for_mock_only():
            for modification in (
                lambda c: setattr(c.dialect, "name", "sqlite"),
                lambda c: setattr(c.dialect, "driver", "psycopg2"),
                lambda c: setattr(c, "closed", True),
                lambda c: setattr(c, "invalidated", True),
                lambda c: setattr(c.in_transaction, "side_effect", lambda: True),
                lambda c: setattr(c.get_isolation_level, "return_value", "READ UNCOMMITTED"),
            ):
                with self.subTest(modification=modification):
                    connection = self.connection()
                    modification(connection)
                    self.assert_no_ddl_after_rejection(connection)
                    connection.begin.assert_not_called()
                    connection.execute.assert_not_called()
            self.assert_no_ddl_after_rejection(None)

    def test_ac01_driver_autocommit_blocks_even_with_read_committed(self):
        connection = self.connection()
        connection.get_isolation_level.return_value = "READ COMMITTED"
        connection.connection.driver_connection.autocommit = True
        with self.approved_for_mock_only():
            self.assert_no_ddl_after_rejection(connection)
        connection.begin.assert_not_called()
        connection.execute.assert_not_called()

    def test_ac02_unavailable_or_ambiguous_driver_autocommit_blocks(self):
        for modification in (
            lambda c: setattr(c.connection, "driver_connection", None),
            lambda c: setattr(c.connection, "driver_connection", object()),
            lambda c: setattr(c.connection.driver_connection, "autocommit", None),
            lambda c: setattr(c.connection.driver_connection, "autocommit", 0),
            lambda c: delattr(c.connection, "driver_connection"),
        ):
            with self.subTest(modification=modification):
                connection = self.connection()
                modification(connection)
                with self.approved_for_mock_only():
                    self.assert_no_ddl_after_rejection(connection)
                connection.begin.assert_not_called()
                connection.execute.assert_not_called()

        connection = self.connection()
        driver = connection.connection.driver_connection
        with (
            self.approved_for_mock_only(),
            patch.object(type(driver), "autocommit", new_callable=PropertyMock,
                         create=True) as autocommit,
        ):
            autocommit.side_effect = RuntimeError("driver inspection failed")
            self.assert_no_ddl_after_rejection(connection)
        connection.begin.assert_not_called()
        connection.execute.assert_not_called()

    def test_ac03_explicit_autocommit_execution_option_blocks(self):
        connection = self.connection()
        connection.get_execution_options.return_value = {
            "isolation_level": "AUTOCOMMIT"
        }
        with self.approved_for_mock_only():
            self.assert_no_ddl_after_rejection(connection)
        connection.begin.assert_not_called()
        connection.execute.assert_not_called()

    def test_ac04_verified_psycopg_transactional_flow_rolls_back(self):
        connection = self.connection()
        driver = connection.connection.driver_connection
        self.assertIsInstance(connection, SQLAlchemyConnection)
        self.assertIsInstance(driver, PsycopgConnection)
        self.assertIs(driver.autocommit, False)
        self.assertEqual(connection.get_isolation_level(), "READ COMMITTED")
        operations, events = self.recording_operations()
        result, configure, create_engine, engine = self.run_with_mock_operations(connection, operations)
        self.assertTrue(events)
        self.assertTrue(result.rolled_back)
        configure.assert_called_once_with(connection=connection)
        connection.begin.return_value.rollback.assert_called_once()
        connection.begin.return_value.commit.assert_not_called()

    def test_ac05_autocommit_changed_before_initial_query_blocks_ddl(self):
        connection = self.connection()
        initial_execute = connection.execute.side_effect
        driver = connection.connection.driver_connection

        def change_before_identity(statement):
            if statement is trial._IDENTITY_SQL:
                driver.autocommit = True
                driver.info.transaction_status = TransactionStatus.IDLE
            return initial_execute(statement)

        connection.execute.side_effect = change_before_identity
        with self.approved_for_mock_only():
            self.assert_no_ddl_after_rejection(connection)
        connection.begin.return_value.rollback.assert_called_once()
        self.assertEqual(connection.execute.call_count, 2)

    def test_ac06_nontransactional_or_unknown_driver_status_blocks(self):
        for status in (
            TransactionStatus.IDLE, TransactionStatus.INERROR,
            TransactionStatus.ACTIVE, TransactionStatus.UNKNOWN, None,
        ):
            with self.subTest(status=status):
                connection = self.connection()
                connection.connection.driver_connection.info.transaction_status = status
                with self.approved_for_mock_only():
                    self.assert_no_ddl_after_rejection(connection)
                connection.begin.return_value.rollback.assert_called_once()

        class BrokenInfo:
            @property
            def transaction_status(self):
                raise RuntimeError("transaction status inspection failed")

        connection = self.connection()
        connection.connection.driver_connection.info = BrokenInfo()
        with self.approved_for_mock_only():
            self.assert_no_ddl_after_rejection(connection)
        connection.begin.return_value.rollback.assert_called_once()

    def test_ac06b_transaction_lost_during_context_setup_blocks_ddl(self):
        connection = self.connection()
        driver = connection.connection.driver_connection
        operations, events = self.recording_operations()

        def alter_status_after_initial_check(_context):
            driver.info.transaction_status = TransactionStatus.IDLE
            return operations

        with (
            self.approved_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (_, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock()),
            patch.object(trial, "Operations", side_effect=alter_status_after_initial_check),
        ):
            with self.assertRaises(trial.TrialBlocked):
                trial.run_trial(
                    target=self.target, authorization=self.authorization,
                    trial_password="offline-unit-only",
                )
        self.assertEqual(events, [])
        connection.begin.return_value.rollback.assert_called_once()
        engine.connect.return_value.__exit__.assert_called_once()
        engine.dispose.assert_called_once()

    def test_ac07_arbitrary_shared_connection_cannot_be_injected(self):
        connection = self.connection()
        with self.approved_for_mock_only(), patch("sqlalchemy.create_engine") as create_engine:
            with self.assertRaises(TypeError):
                trial.run_trial(
                    connection=connection, target=self.target,
                    authorization=self.authorization, trial_password="offline-unit-only",
                )
            with self.assertRaises(TypeError):
                trial.run_trial(
                    engine=MagicMock(), target=self.target,
                    authorization=self.authorization, trial_password="offline-unit-only",
                )
        create_engine.assert_not_called()
        connection.begin.assert_not_called()
        connection.execute.assert_not_called()

    def test_ac08_private_nullpool_connection_completes_and_closes(self):
        connection = self.connection()
        operations, events = self.recording_operations()
        result, configure, create_engine, engine = self.run_with_mock_operations(
            connection, operations
        )
        self.assertTrue(events)
        self.assertTrue(result.rolled_back)
        self.assertIs(
            connection.connection.driver_connection.info.transaction_status,
            TransactionStatus.INTRANS,
        )
        create_engine.assert_called_once()
        url = create_engine.call_args.args[0]
        self.assertEqual(url.drivername, "postgresql+psycopg")
        self.assertEqual((url.host, url.port, url.database, url.username), (
            self.target.host, self.target.port, self.target.database, self.target.role
        ))
        self.assertEqual(url.password, "offline-unit-only")
        self.assertIs(create_engine.call_args.kwargs["poolclass"], NullPool)
        engine.connect.assert_called_once()
        engine.connect.return_value.__exit__.assert_called_once()
        engine.dispose.assert_called_once()
        configure.assert_called_once_with(connection=connection)
        connection.begin.return_value.rollback.assert_called_once()
        connection.begin.return_value.commit.assert_not_called()

    def test_ac09_revision_globals_never_publish_private_operations(self):
        c15, c16 = trial._frozen_revisions()
        original_c15_op, original_c16_op = c15.op, c16.op
        seen = []

        for revision, method in (
            (c15, "upgrade"), (c16, "upgrade"),
            (c16, "downgrade"), (c15, "downgrade"),
        ):
            operations = Mock()
            operations.get_bind.return_value = object()

            def observe(*args, **kwargs):
                self.assertIs(c15.op, original_c15_op)
                self.assertIs(c16.op, original_c16_op)
                self.assertIsNot(c15.op, operations)
                self.assertIsNot(c16.op, operations)
                seen.append((revision.revision, method))

            for name in (
                "execute", "create_unique_constraint", "create_table",
                "create_index", "drop_index", "drop_table", "drop_constraint",
            ):
                getattr(operations, name).side_effect = observe
            trial._invoke(revision, method, operations)

        self.assertTrue(seen)
        self.assertIs(c15.op, original_c15_op)
        self.assertIs(c16.op, original_c16_op)

    def test_ac10_each_migration_uses_private_globals_and_rejects_helpers(self):
        c15, c16 = trial._frozen_revisions()
        cases = (
            (c15, "upgrade", {"__builtins__", "op", "sa", "SCHEMA_DDL"}),
            (c15, "downgrade", {"__builtins__", "op", "sa", "TABLE_ORDER"}),
            (c16, "upgrade", {"__builtins__", "op", "sa", "postgresql"}),
            (c16, "downgrade", {"__builtins__", "op"}),
        )
        for revision, method, names in cases:
            with self.subTest(revision=revision.revision, method=method):
                original = vars(revision)[method]
                original_globals = original.__globals__
                original_op = revision.op
                operations = Mock()
                isolated = trial._isolated_revision_function(
                    revision, method, operations
                )
                self.assertIsNot(isolated, original)
                self.assertIsNot(isolated.__globals__, original_globals)
                self.assertEqual(set(isolated.__globals__), names)
                self.assertIs(isolated.__globals__["op"], operations)
                self.assertIs(original.__globals__, original_globals)
                self.assertIs(revision.op, original_op)
                self.assertIsNot(original_globals["op"], operations)

        fake = ModuleType("unapproved_helper_revision")
        fake.revision = trial.C15_REVISION
        fake.op = object()
        fake.sa = trial.sqlalchemy
        fake.SCHEMA_DDL = ()

        def calls_helper():
            helper()

        fake.helper = lambda: None
        fake.upgrade = FunctionType(calls_helper.__code__, vars(fake), "upgrade")
        with self.assertRaises(trial.TrialBlocked):
            trial._isolated_revision_function(fake, "upgrade", Mock())

        fake.upgrade = FunctionType(c15.upgrade.__code__, vars(fake), "upgrade")
        fake.SCHEMA_DDL = ["mutable DDL list"]
        with self.assertRaises(trial.TrialBlocked):
            trial._isolated_revision_function(fake, "upgrade", Mock())

        def closure_factory():
            captured = object()

            def closed_over():
                return captured

            return closed_over

        closed_over = closure_factory()
        fake.upgrade = FunctionType(
            closed_over.__code__, vars(fake), "upgrade",
            None, closed_over.__closure__,
        )
        with self.assertRaises(trial.TrialBlocked):
            trial._isolated_revision_function(fake, "upgrade", Mock())

        def nested_migration():
            op.execute(sa.DDL(SCHEMA_DDL[0]))

            def hidden_helper():
                return 1

            return hidden_helper

        fake.SCHEMA_DDL = ()
        fake.upgrade = FunctionType(
            nested_migration.__code__, vars(fake), "upgrade"
        )
        with self.assertRaises(trial.TrialBlocked):
            trial._isolated_revision_function(fake, "upgrade", Mock())

    def test_ac11_exception_leaves_no_bind_in_revision_modules(self):
        c15, c16 = trial._frozen_revisions()
        original_c15_op, original_c16_op = c15.op, c16.op
        private_bind = object()
        operations = Mock()
        operations.get_bind.return_value = private_bind
        operations.execute.side_effect = RuntimeError("simulated DDL failure")
        with self.assertRaisesRegex(RuntimeError, "simulated DDL failure"):
            trial._invoke(c15, "upgrade", operations)
        for revision, original_op in (
            (c15, original_c15_op), (c16, original_c16_op)
        ):
            self.assertIs(revision.op, original_op)
            self.assertIs(vars(revision)["op"], original_op)
            self.assertIsNot(vars(revision)["upgrade"].__globals__["op"], operations)
            self.assertFalse(any(
                value is operations or value is private_bind
                for value in vars(revision).values()
            ))

    def test_ac12_concurrent_invocations_keep_distinct_namespaces(self):
        c15, _ = trial._frozen_revisions()
        original_op = c15.op
        first, second = Mock(), Mock()
        first_globals = trial._isolated_revision_function(
            c15, "upgrade", first
        ).__globals__
        second_globals = trial._isolated_revision_function(
            c15, "upgrade", second
        ).__globals__
        self.assertIsNot(first_globals, second_globals)
        self.assertIs(first_globals["op"], first)
        self.assertIs(second_globals["op"], second)

        barrier = Barrier(2)

        def invoke_with(operations):
            def execute(statement):
                if operations.execute.call_count == 1:
                    barrier.wait(timeout=10)
                self.assertIs(c15.op, original_op)

            operations.execute.side_effect = execute
            trial._invoke(c15, "upgrade", operations)

        with ThreadPoolExecutor(max_workers=2) as workers:
            one = workers.submit(invoke_with, first)
            two = workers.submit(invoke_with, second)
            one.result(timeout=15)
            two.result(timeout=15)
        self.assertEqual(first.execute.call_count, len(c15.SCHEMA_DDL))
        self.assertEqual(second.execute.call_count, len(c15.SCHEMA_DDL))
        self.assertIs(c15.op, original_op)

    def test_ac13_later_failure_still_rolls_back_closes_and_disposes(self):
        c15, c16 = trial._frozen_revisions()
        original_c15_op, original_c16_op = c15.op, c16.op
        connection = self.connection()
        operations, _ = self.recording_operations()
        operations.create_unique_constraint.side_effect = RuntimeError(
            "simulated C16 DDL failure"
        )
        with (
            self.approved_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (_, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock()),
            patch.object(trial, "Operations", return_value=operations),
        ):
            with self.assertRaisesRegex(RuntimeError, "simulated C16 DDL failure"):
                trial.run_trial(
                    target=self.target, authorization=self.authorization,
                    trial_password="offline-unit-only",
                )
        connection.begin.return_value.rollback.assert_called_once()
        connection.begin.return_value.commit.assert_not_called()
        engine.connect.return_value.__exit__.assert_called_once()
        engine.dispose.assert_called_once()
        self.assertIs(c15.op, original_c15_op)
        self.assertIs(c16.op, original_c16_op)

    def test_mismatched_host_port_database_role_or_version_refuses_before_ddl(self):
        cases = (
            {"host": "0.0.0.0"}, {"port": 5433},
            {"database": trial.AUTHORITATIVE_DATABASE},
            {"database": "frcaixinha_2_2_c16_trial_other"},
            {"role": "frc22_owner"}, {"version": 170000},
            {"version": 190000},
        )
        with self.approved_for_mock_only():
            for change in cases:
                with self.subTest(change=change):
                    connection = self.connection(identity=self.identity(**change))
                    self.assert_no_ddl_after_rejection(connection)
                    connection.begin.return_value.rollback.assert_called_once()

    def test_superuser_createdb_recovery_and_read_only_refuse_before_ddl(self):
        cases = (
            {"superuser": True}, {"createdb": True},
            {"recovery": True}, {"read_only": "on"},
        )
        with self.approved_for_mock_only():
            for change in cases:
                with self.subTest(change=change):
                    connection = self.connection(identity=self.identity(**change))
                    self.assert_no_ddl_after_rejection(connection)
                    connection.begin.return_value.rollback.assert_called_once()

    def test_nonempty_or_malformed_schema_refuses_before_ddl(self):
        cases = (
            (("public", "existing_table", "r"),),
            (("other_schema", "existing_table", "r"),),
            (("public", "existing_index", "i"),),
            (("bad",),),
        )
        with self.approved_for_mock_only():
            for relations in cases:
                with self.subTest(relations=relations):
                    connection = self.connection(inventories=(relations,))
                    self.assert_no_ddl_after_rejection(connection)
                    connection.begin.return_value.rollback.assert_called_once()

    def test_source_mismatch_blocks_before_transaction_or_ddl(self):
        connection = self.connection()
        with self.approved_for_mock_only(), patch.object(
            trial, "_sha256_file", return_value="0" * 64
        ):
            self.assert_no_ddl_after_rejection(connection)
        connection.begin.assert_not_called()
        connection.execute.assert_not_called()

    def test_upgrade_and_downgrade_order_with_rollback(self):
        connection = self.connection()
        operations, events = self.recording_operations()
        result, configure, create_engine, engine = self.run_with_mock_operations(connection, operations)
        self.assertEqual(result.upgrades, (trial.C15_REVISION, trial.C16_REVISION))
        self.assertEqual(result.downgrades, (trial.C16_REVISION, trial.C15_REVISION))
        self.assertTrue(result.rolled_back)
        configure.assert_called_once_with(connection=connection)
        self.assertEqual(sum(name == "execute" for name, _, _ in events[:33]), 33)
        self.assertTrue(events[0][1][0].statement.startswith("CREATE TABLE license_plans"))
        self.assertEqual(events[33][0], "create_unique_constraint")
        self.assertEqual(sum(name == "create_table" for name, _, _ in events), 2)
        first_drop = next(i for i, (name, _, _) in enumerate(events) if name == "drop_index")
        self.assertGreater(first_drop, 33)
        self.assertEqual(events[-1][1][0].statement, "DROP TABLE license_plans")
        connection.begin.return_value.rollback.assert_called_once()
        connection.begin.return_value.commit.assert_not_called()

    def test_exception_restores_revision_bindings_and_rolls_back(self):
        c15, c16 = trial._frozen_revisions()
        original_c15_op, original_c16_op = c15.op, c16.op
        connection = self.connection()
        operations = Mock()
        operations.execute.side_effect = RuntimeError("simulated DDL failure")
        with (
            self.approved_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (_, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock()),
            patch.object(trial, "Operations", return_value=operations),
        ):
            with self.assertRaisesRegex(RuntimeError, "simulated DDL failure"):
                trial.run_trial(
                    target=self.target, authorization=self.authorization,
                    trial_password="offline-unit-only",
                )
        engine.dispose.assert_called_once()
        engine.connect.return_value.__exit__.assert_called_once()
        self.assertIs(c15.op, original_c15_op)
        self.assertIs(c16.op, original_c16_op)
        connection.begin.return_value.rollback.assert_called_once()
        connection.begin.return_value.commit.assert_not_called()

    def test_no_real_connections_or_credential_arguments(self):
        connection = self.connection()
        operations, _ = self.recording_operations()
        with patch("psycopg.connect") as connect:
            self.run_with_mock_operations(connection, operations)
        connect.assert_not_called()
        with patch("sqlalchemy.create_engine") as create_engine:
            with self.assertRaises(TypeError):
                trial.run_trial(
                    connection, target=self.target, authorization=self.authorization,
                    trial_password="offline-unit-only",
                )
            with self.assertRaises(TypeError):
                trial.run_trial(
                    target=self.target, authorization=self.authorization,
                    trial_password="offline-unit-only", password="forbidden",
                )
        create_engine.assert_not_called()

    @contextmanager
    def approved_schema_for_mock_only(self):
        with (
            patch.object(trial, "APPROVED_SCHEMA_TRIAL_TARGET", self.schema_target),
            patch.object(
                trial, "APPROVED_SCHEMA_TRIAL_CHECKPOINT",
                self.schema_authorization.checkpoint,
            ),
        ):
            yield

    @property
    def schema_target(self):
        return trial.SchemaTrialTarget(
            "127.0.0.1", 5432, trial.AUTHORITATIVE_DATABASE,
            "frc22_trial_unit", "frc22_c16_trial_unit",
        )

    @property
    def schema_authorization(self):
        return trial.SchemaTrialAuthorization(
            "C16-R11.15-OFFLINE-UNIT", self.schema_target
        )

    def schema_connection(
        self, *, identity=None, role=_UNSET, schemas=None, relations=None,
        path=None, fks=(), constraints=None,
    ):
        target = self.schema_target
        if identity is None:
            identity = (
                target.database, target.role, target.host, target.port,
                180002, False, False, False, "off",
            )
        if role is _UNSET:
            role = (True, False, False, False, True, True, True, True)
        if schemas is None:
            schemas = [
                ("public",),
                *(("public", target.schema) for _ in range(5)),
                ("public",),
            ]
        if relations is None:
            baseline = (("public", "existing_unrelated", "r"),)
            def stage(names):
                return baseline + tuple((target.schema, name, "r") for name in names)
            relations = [
                baseline, stage(()), stage(trial.C15_TABLES),
                stage(trial.C16_TABLES), stage(trial.C15_TABLES),
                stage(()), baseline,
            ]
        if constraints is None:
            baseline_constraints = (("public", "existing_constraint", "c"),)
            constraints = [baseline_constraints] * 7
        if path is None:
            path = (
                target.schema, f"{target.schema}, pg_catalog, pg_temp",
                (target.schema, "pg_catalog"),
            )
        schema_iter = iter(schemas)
        relation_iter = iter(relations)
        constraint_iter = iter(constraints)
        connection = self.connection(identity=identity)
        driver = connection.connection.driver_connection
        connection.in_transaction.side_effect = lambda: (
            connection.begin.called and not connection.begin.return_value.rollback.called
        )
        connection.begin.return_value.rollback.side_effect = lambda: setattr(
            driver.info, "transaction_status", TransactionStatus.IDLE
        )
        original_execute = connection.execute.side_effect

        def execute(statement, parameters=None):
            if statement is trial._ROLE_SQL:
                return FakeResult(one=role)
            if statement is trial._SCHEMAS_SQL:
                return FakeResult(rows=tuple((name,) for name in next(schema_iter)))
            if statement is trial._RELATIONS_SQL:
                return FakeResult(rows=next(relation_iter))
            if statement is trial._CONSTRAINTS_SQL:
                return FakeResult(rows=next(constraint_iter))
            if statement is trial._PATH_SQL:
                return FakeResult(one=path)
            if statement is trial._SET_PATH_SQL:
                self.assertEqual(
                    parameters, {"path": f"{target.schema}, pg_catalog, pg_temp"}
                )
                return FakeResult(one=parameters["path"])
            if statement is trial._FKS_SQL:
                self.assertEqual(parameters, {"schema": target.schema})
                return FakeResult(rows=fks)
            return original_execute(statement)

        connection.execute.side_effect = execute
        return connection

    def run_schema_with_mock_operations(self, connection, operations):
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (create_engine, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock())
            as configure,
            patch.object(trial, "Operations", return_value=operations),
        ):
            result = trial.run_schema_trial(
                target=self.schema_target,
                authorization=self.schema_authorization,
                trial_password="offline-unit-only",
            )
        return result, configure, create_engine, engine

    def test_schema_gate_defaults_to_none_and_preserves_old_refusal(self):
        self.assertIsNone(trial.APPROVED_SCHEMA_TRIAL_TARGET)
        self.assertIsNone(trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT)
        with patch("sqlalchemy.create_engine") as create_engine:
            with self.assertRaises(trial.TrialBlocked):
                trial.run_schema_trial(
                    target=self.schema_target,
                    authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        create_engine.assert_not_called()
        forbidden = trial.TrialTarget(
            "127.0.0.1", 5432, trial.AUTHORITATIVE_DATABASE,
            trial.AUTHORITATIVE_ROLE,
        )
        with patch.object(trial, "APPROVED_TRIAL_TARGET", forbidden), patch.object(
            trial, "APPROVED_TRIAL_CHECKPOINT", "offline-unit"
        ):
            with self.assertRaises(trial.TrialBlocked):
                trial._validate_request(
                    forbidden, trial.TrialAuthorization("offline-unit", forbidden)
                )

    def test_schema_target_and_authorization_fail_closed_before_connection(self):
        target = self.schema_target
        invalid = (
            None,
            trial.SchemaTrialTarget("localhost", 5432, target.database, target.role, target.schema),
            trial.SchemaTrialTarget(target.host, 5433, target.database, target.role, target.schema),
            trial.SchemaTrialTarget(target.host, target.port, "other_db", target.role, target.schema),
            trial.SchemaTrialTarget(target.host, target.port, target.database, "postgres", target.schema),
            trial.SchemaTrialTarget(target.host, target.port, target.database,
                                    trial.AUTHORITATIVE_ROLE, target.schema),
            *(
                trial.SchemaTrialTarget(
                    target.host, target.port, target.database, target.role, name
                )
                for name in (
                    "", "public", "pg_temp", "pg_catalog",
                    "information_schema", "frc22_c16_trial_x;DROP",
                    "frc22_c16_trial_x, public", "frc22_c16_trial_X",
                )
            ),
        )
        with self.approved_schema_for_mock_only(), patch(
            "sqlalchemy.create_engine"
        ) as create_engine:
            for candidate in invalid:
                with self.subTest(candidate=candidate):
                    with self.assertRaises(trial.TrialBlocked):
                        trial.run_schema_trial(
                            target=candidate,
                            authorization=trial.SchemaTrialAuthorization(
                                self.schema_authorization.checkpoint, candidate
                            ),
                            trial_password="offline-unit-only",
                        )
            for auth in (None, trial.SchemaTrialAuthorization("wrong", target)):
                with self.assertRaises(trial.TrialBlocked):
                    trial.run_schema_trial(
                        target=target, authorization=auth,
                        trial_password="offline-unit-only",
                    )
        create_engine.assert_not_called()

    def test_schema_role_and_identity_reject_unsafe_privileges(self):
        cases = (
            {"identity": (
                self.schema_target.database, self.schema_target.role,
                "0.0.0.0", 5432, 180002, False, False, False, "off",
            )},
            {"identity": (
                self.schema_target.database, self.schema_target.role,
                "127.0.0.1", 5432, 170000, False, False, False, "off",
            )},
            {"identity": (
                self.schema_target.database, self.schema_target.role,
                "127.0.0.1", 5432, 180002, True, False, False, "off",
            )},
            {"identity": (
                self.schema_target.database, self.schema_target.role,
                "127.0.0.1", 5432, 180002, False, True, False, "off",
            )},
            *({"role": role} for role in (
                None, (True, True, False, False, True, True, True, True),
                (True, False, True, False, True, True, True, True),
                (True, False, False, True, True, True, True, True),
                (True, False, False, False, True, False, True, True),
                (True, False, False, False, True, True, False, True),
                (True, False, False, False, True, True, True, False),
            )),
        )
        for change in cases:
            with self.subTest(change=change):
                connection = self.schema_connection(**change)
                with (
                    self.approved_schema_for_mock_only(),
                    self.private_engine_for_mock_only(connection) as (_, engine),
                    patch.object(trial, "Operations") as operations,
                ):
                    with self.assertRaises(trial.TrialBlocked):
                        trial.run_schema_trial(
                            target=self.schema_target,
                            authorization=self.schema_authorization,
                            trial_password="offline-unit-only",
                        )
                connection.exec_driver_sql.assert_not_called()
                operations.assert_not_called()
                connection.begin.return_value.rollback.assert_called_once()
                engine.dispose.assert_called_once()

    def test_schema_existing_name_blocks_before_ddl(self):
        connection = self.schema_connection(schemas=[("public", self.schema_target.schema)])
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection),
        ):
            with self.assertRaises(trial.TrialBlocked):
                trial.run_schema_trial(
                    target=self.schema_target,
                    authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        connection.exec_driver_sql.assert_not_called()

    def test_schema_search_path_rejects_fallback_and_shadowing(self):
        target = self.schema_target
        for path in (
            (target.schema, f"{target.schema}, public", (target.schema, "public")),
            ("public", f"{target.schema}, pg_catalog, pg_temp", ("public",)),
            (target.schema, f"{target.schema}, pg_catalog, pg_temp", ("pg_temp_3", target.schema)),
            (target.schema, f"{target.schema}, pg_catalog, pg_temp", (target.schema, "public")),
            (target.schema, f"{target.schema}, pg_catalog, pg_temp", (target.schema, "other")),
            (target.schema, f"{target.schema}, pg_catalog, pg_temp", (target.schema,)),
            (target.schema, f"{target.schema}, pg_catalog, pg_temp",
             (target.schema, target.schema, "pg_catalog")),
        ):
            with self.subTest(path=path):
                connection = self.schema_connection(path=path)
                with self.assertRaises(trial.TrialBlocked):
                    trial._require_schema_path(connection, target.schema)

    def test_schema_autocommit_and_inactive_transaction_block_before_ddl(self):
        for modification in (
            lambda c: setattr(c.connection.driver_connection, "autocommit", True),
            lambda c: setattr(c.get_execution_options, "return_value",
                              {"isolation_level": "AUTOCOMMIT"}),
        ):
            connection = self.schema_connection()
            modification(connection)
            with (
                self.approved_schema_for_mock_only(),
                self.private_engine_for_mock_only(connection),
            ):
                with self.assertRaises(trial.TrialBlocked):
                    trial.run_schema_trial(
                        target=self.schema_target,
                        authorization=self.schema_authorization,
                        trial_password="offline-unit-only",
                    )
            connection.exec_driver_sql.assert_not_called()

        connection = self.schema_connection()
        connection.connection.driver_connection.info.transaction_status = (
            TransactionStatus.IDLE
        )
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection),
        ):
            with self.assertRaises(trial.TrialBlocked):
                trial.run_schema_trial(
                    target=self.schema_target,
                    authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        connection.exec_driver_sql.assert_not_called()
        connection.begin.return_value.rollback.assert_called_once()

    def test_schema_lost_driver_blocks_before_first_migration_ddl(self):
        connection = self.schema_connection()
        operations, events = self.recording_operations()
        driver = connection.connection.driver_connection

        def lose_driver(statement):
            driver.info.transaction_status = TransactionStatus.IDLE

        connection.exec_driver_sql.side_effect = lose_driver
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection),
            patch.object(trial.MigrationContext, "configure") as configure,
            patch.object(trial, "Operations", return_value=operations),
        ):
            with self.assertRaises(trial.TrialBlocked):
                trial.run_schema_trial(
                    target=self.schema_target,
                    authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        self.assertEqual(events, [])
        configure.assert_not_called()
        connection.begin.return_value.rollback.assert_called_once()

    def test_schema_swapped_driver_and_path_change_block_before_migrations(self):
        for change in ("driver", "path"):
            with self.subTest(change=change):
                connection = self.schema_connection()
                operations, events = self.recording_operations()
                if change == "driver":
                    connection.exec_driver_sql.side_effect = (
                        lambda statement: setattr(
                            connection.connection, "driver_connection",
                            Mock(spec=PsycopgConnection),
                        )
                    )
                else:
                    original_execute = connection.execute.side_effect

                    def changed_path(statement, parameters=None):
                        if statement is trial._PATH_SQL:
                            return FakeResult(one=(
                                "public", "public", ("public", "pg_catalog"),
                            ))
                        return original_execute(statement, parameters)

                    connection.execute.side_effect = changed_path
                with (
                    self.approved_schema_for_mock_only(),
                    self.private_engine_for_mock_only(connection),
                    patch.object(trial.MigrationContext, "configure") as configure,
                    patch.object(trial, "Operations", return_value=operations),
                ):
                    with self.assertRaises(trial.TrialBlocked):
                        trial.run_schema_trial(
                            target=self.schema_target,
                            authorization=self.schema_authorization,
                            trial_password="offline-unit-only",
                        )
                self.assertEqual(events, [])
                configure.assert_not_called()
                connection.begin.return_value.rollback.assert_called_once()

    def test_schema_catalog_rejects_cross_schema_relation_and_fk(self):
        target = self.schema_target
        baseline = (("public", "existing_unrelated", "r"),)
        escaped = baseline + (("public", "escaped_index", "i"),) + tuple(
            (target.schema, name, "r") for name in trial.C15_TABLES
        )
        for change in (
            {"relations": [baseline, baseline, escaped]},
            {"constraints": [
                (("public", "existing_constraint", "c"),),
                (("public", "existing_constraint", "c"),),
                (("public", "existing_constraint", "c"),
                 ("public", "escaped_constraint", "c")),
            ]},
            {"fks": (("frc22_c16_trial_unit", "public"),)},
        ):
            with self.subTest(change=change):
                connection = self.schema_connection(**change)
                operations, events = self.recording_operations()
                with (
                    self.approved_schema_for_mock_only(),
                    self.private_engine_for_mock_only(connection),
                    patch.object(trial.MigrationContext, "configure", return_value=Mock()),
                    patch.object(trial, "Operations", return_value=operations),
                ):
                    with self.assertRaises(trial.TrialBlocked):
                        trial.run_schema_trial(
                            target=target,
                            authorization=self.schema_authorization,
                            trial_password="offline-unit-only",
                        )
                connection.begin.return_value.rollback.assert_called_once()
                if "relations" in change or "constraints" in change:
                    self.assertTrue(events)

    def test_schema_sequence_rollback_and_private_resources_are_mocked(self):
        connection = self.schema_connection()
        operations, events = self.recording_operations()
        result, configure, create_engine, engine = self.run_schema_with_mock_operations(
            connection, operations
        )
        self.assertTrue(result.rolled_back)
        self.assertEqual(result.upgrades, (trial.C15_REVISION, trial.C16_REVISION))
        self.assertEqual(result.downgrades, (trial.C16_REVISION, trial.C15_REVISION))
        self.assertEqual(sum(name == "execute" for name, _, _ in events[:33]), 33)
        self.assertEqual(events[33][0], "create_unique_constraint")
        self.assertEqual(events[-1][1][0].statement, "DROP TABLE license_plans")
        self.assertEqual(connection.exec_driver_sql.call_count, 1)
        self.assertEqual(
            connection.exec_driver_sql.call_args.args[0],
            f'CREATE SCHEMA "{self.schema_target.schema}"',
        )
        configure.assert_called_once_with(connection=connection)
        self.assertIs(create_engine.call_args.kwargs["poolclass"], NullPool)
        connection.begin.return_value.rollback.assert_called_once()
        connection.begin.return_value.commit.assert_not_called()
        engine.connect.return_value.__exit__.assert_called_once()
        engine.dispose.assert_called_once()

    def schema_connection_for_c16_failure(self, *, residue=False):
        target = self.schema_target
        baseline = (("public", "existing_unrelated", "r"),)
        baseline_constraints = (("public", "existing_constraint", "c"),)
        return self.schema_connection(
            schemas=[
                ("public",),
                ("public", target.schema),
                ("public", target.schema),
                ("public", target.schema) if residue else ("public",),
            ],
            relations=[
                baseline,
                baseline,
                baseline + tuple((target.schema, name, "r") for name in trial.C15_TABLES),
                baseline,
            ],
            constraints=[baseline_constraints] * 4,
        )

    def test_schema_exception_rolls_back_closes_and_disposes(self):
        connection = self.schema_connection_for_c16_failure()
        operations, _ = self.recording_operations()
        operations.create_table.side_effect = RuntimeError("simulated failure")
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (_, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock()),
            patch.object(trial, "Operations", return_value=operations),
        ):
            with self.assertRaisesRegex(RuntimeError, "simulated failure"):
                trial.run_schema_trial(
                    target=self.schema_target,
                    authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        connection.begin.return_value.rollback.assert_called_once()
        engine.connect.return_value.__exit__.assert_called_once()
        engine.dispose.assert_called_once()

    def test_schema_migration_failure_checks_catalog_after_rollback(self):
        target = self.schema_target
        connection = self.schema_connection_for_c16_failure()
        operations, _ = self.recording_operations()
        original_error = RuntimeError("migration failed")
        operations.create_table.side_effect = original_error
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (_, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock()),
            patch.object(trial, "Operations", return_value=operations),
        ):
            with self.assertRaisesRegex(RuntimeError, "migration failed") as raised:
                trial.run_schema_trial(
                    target=target, authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        self.assertIs(raised.exception, original_error)
        connection.begin.return_value.rollback.assert_called_once()
        connection.rollback.assert_called_once()
        engine.connect.return_value.__exit__.assert_called_once()
        engine.dispose.assert_called_once()
        for statement in (
            trial._SCHEMAS_SQL, trial._RELATIONS_SQL, trial._CONSTRAINTS_SQL
        ):
            self.assertEqual(
                sum(call.args[0] is statement for call in connection.execute.call_args_list),
                4,
                "catalog must be checked again after rollback on migration failure",
            )

    def test_schema_failure_with_post_rollback_residue_preserves_cause(self):
        connection = self.schema_connection_for_c16_failure(residue=True)
        operations, _ = self.recording_operations()
        original = RuntimeError("migration failed")
        operations.create_table.side_effect = original
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (_, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock()),
            patch.object(trial, "Operations", return_value=operations),
        ):
            with self.assertRaises(trial.TrialBlocked) as raised:
                trial.run_schema_trial(
                    target=self.schema_target,
                    authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        self.assertIs(raised.exception.original_error, original)
        self.assertIs(raised.exception.__cause__, original)
        self.assertIn("residue", str(raised.exception.inventory_error))
        connection.begin.return_value.rollback.assert_called_once()
        connection.rollback.assert_called_once()
        engine.dispose.assert_called_once()

    def test_schema_failure_with_rollback_error_blocks_inventory(self):
        connection = self.schema_connection_for_c16_failure()
        operations, _ = self.recording_operations()
        original = RuntimeError("migration failed")
        rollback_error = RuntimeError("rollback failed")
        operations.create_table.side_effect = original
        connection.begin.return_value.rollback.side_effect = rollback_error
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (_, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock()),
            patch.object(trial, "Operations", return_value=operations),
        ):
            with self.assertRaises(trial.TrialBlocked) as raised:
                trial.run_schema_trial(
                    target=self.schema_target,
                    authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        self.assertIs(raised.exception.__cause__, original)
        self.assertIs(raised.exception.rollback_error, rollback_error)
        self.assertIn("unverified", str(raised.exception.inventory_error))
        connection.begin.return_value.rollback.assert_called_once()
        connection.rollback.assert_not_called()
        engine.connect.return_value.__exit__.assert_called_once()
        engine.dispose.assert_called_once()

    def test_schema_failure_with_post_rollback_inventory_error_preserves_cause(self):
        connection = self.schema_connection_for_c16_failure()
        original_execute = connection.execute.side_effect
        reads = 0
        inventory_error = RuntimeError("catalog unavailable")

        def fail_last_inventory(statement, parameters=None):
            nonlocal reads
            if statement is trial._SCHEMAS_SQL:
                reads += 1
                if reads == 4:
                    raise inventory_error
            return original_execute(statement, parameters)

        connection.execute.side_effect = fail_last_inventory
        operations, _ = self.recording_operations()
        original = RuntimeError("migration failed")
        operations.create_table.side_effect = original
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (_, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock()),
            patch.object(trial, "Operations", return_value=operations),
        ):
            with self.assertRaises(trial.TrialBlocked) as raised:
                trial.run_schema_trial(
                    target=self.schema_target,
                    authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        self.assertEqual(reads, 4)
        self.assertIs(raised.exception.__cause__, original)
        self.assertIs(raised.exception.inventory_error, inventory_error)
        connection.begin.return_value.rollback.assert_called_once()
        connection.rollback.assert_called_once()
        engine.dispose.assert_called_once()

    def test_schema_failure_with_intrans_after_rollback_blocks_inventory(self):
        connection = self.schema_connection_for_c16_failure()
        connection.begin.return_value.rollback.side_effect = lambda: None
        operations, _ = self.recording_operations()
        original = RuntimeError("migration failed")
        operations.create_table.side_effect = original
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (_, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock()),
            patch.object(trial, "Operations", return_value=operations),
        ):
            with self.assertRaises(trial.TrialBlocked) as raised:
                trial.run_schema_trial(
                    target=self.schema_target,
                    authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        self.assertIs(raised.exception.__cause__, original)
        self.assertIn("state is unverified", str(raised.exception.inventory_error))
        self.assertEqual(
            sum(call.args[0] is trial._SCHEMAS_SQL
                for call in connection.execute.call_args_list),
            3,
        )
        connection.rollback.assert_called_once()
        engine.dispose.assert_called_once()

    def test_schema_audit_transaction_rollback_error_blocks_success(self):
        connection = self.schema_connection()
        audit_error = RuntimeError("audit rollback failed")
        connection.rollback.side_effect = audit_error
        operations, _ = self.recording_operations()
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (_, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock()),
            patch.object(trial, "Operations", return_value=operations),
        ):
            with self.assertRaises(trial.TrialBlocked) as raised:
                trial.run_schema_trial(
                    target=self.schema_target,
                    authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        self.assertIsNone(raised.exception.original_error)
        self.assertIsNone(raised.exception.rollback_error)
        self.assertIsNone(raised.exception.inventory_error)
        self.assertIs(raised.exception.audit_rollback_error, audit_error)
        connection.begin.return_value.rollback.assert_called_once()
        connection.rollback.assert_called_once()
        engine.connect.return_value.__exit__.assert_called_once()
        engine.dispose.assert_called_once()

    def test_schema_post_rollback_residue_blocks_pass(self):
        target = self.schema_target
        # The final catalog snapshot still contains the uncommitted schema.
        schemas = [
            ("public",),
            *(("public", target.schema) for _ in range(5)),
            ("public", target.schema),
        ]
        connection = self.schema_connection(schemas=schemas)
        operations, _ = self.recording_operations()
        with (
            self.approved_schema_for_mock_only(),
            self.private_engine_for_mock_only(connection) as (_, engine),
            patch.object(trial.MigrationContext, "configure", return_value=Mock()),
            patch.object(trial, "Operations", return_value=operations),
        ):
            with self.assertRaises(trial.TrialBlocked):
                trial.run_schema_trial(
                    target=target, authorization=self.schema_authorization,
                    trial_password="offline-unit-only",
                )
        connection.begin.return_value.rollback.assert_called_once()
        engine.dispose.assert_called_once()


if __name__ == "__main__":
    unittest.main()
