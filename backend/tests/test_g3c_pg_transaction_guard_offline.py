"""Provas offline da guarda física G3-C; não abre conexão PostgreSQL."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, create_autospec

from psycopg import Connection as PsycopgConnection
from psycopg.pq import TransactionStatus
from sqlalchemy.engine import Connection, Engine

from app.g3c_pg_transaction_guard import require_pg_transaction
from app.g3c_transaction_guards_offline import TransactionGateError


class PhysicalPostgresTransactionGuardTests(unittest.TestCase):
    def setUp(self):
        self.connection = create_autospec(Connection, instance=True)
        self.connection.closed = False
        self.connection.invalidated = False
        self.connection.in_transaction.return_value = True
        self.transaction = Mock(is_active=True)
        self.connection.get_transaction.return_value = self.transaction
        self.connection.dialect = SimpleNamespace(name="postgresql", driver="psycopg")
        self.connection.engine = create_autospec(Engine, instance=True)
        self.connection.engine.get_execution_options.return_value = {}
        self.connection.get_execution_options.return_value = {}
        self.driver = create_autospec(PsycopgConnection, instance=True)
        self.driver.autocommit = False
        self.driver.info = SimpleNamespace(
            transaction_status=TransactionStatus.INTRANS,
        )
        self.connection.connection = SimpleNamespace(driver_connection=self.driver)

    def allowed(self):
        require_pg_transaction(self.connection, denial="REPLAY_DENIED")

    def denied(self):
        with self.assertRaisesRegex(
            TransactionGateError, "^REPLAY_DENIED$"
        ) as caught:
            self.allowed()
        self.assertNotIn("sensitive", str(caught.exception))
        self.connection.execute.assert_not_called()
        self.connection.commit.assert_not_called()
        self.connection.rollback.assert_not_called()

    def test_intrans_psycopg_passes_without_extra_sql(self):
        self.allowed()
        self.connection.execute.assert_not_called()
        self.connection.commit.assert_not_called()
        self.connection.rollback.assert_not_called()

    def test_driver_autocommit_denied_despite_logical_transaction(self):
        self.driver.autocommit = True
        self.denied()

    def test_engine_autocommit_option_denied(self):
        self.connection.engine.get_execution_options.return_value = {
            "isolation_level": "AUTOCOMMIT"
        }
        self.denied()

    def test_connection_autocommit_option_denied(self):
        self.connection.get_execution_options.return_value = {
            "isolation_level": "autocommit"
        }
        self.denied()

    def test_idle_is_started_by_select_one_on_same_connection(self):
        self.driver.info.transaction_status = TransactionStatus.IDLE

        def start_transaction(statement):
            self.assertEqual(str(statement), "SELECT 1")
            self.driver.info.transaction_status = TransactionStatus.INTRANS
            return Mock(scalar_one=Mock(return_value=1))

        self.connection.execute.side_effect = start_transaction
        self.allowed()
        self.connection.execute.assert_called_once()
        self.connection.commit.assert_not_called()
        self.connection.rollback.assert_not_called()

    def test_idle_that_remains_idle_is_denied(self):
        self.driver.info.transaction_status = TransactionStatus.IDLE
        self.connection.execute.return_value.scalar_one.return_value = 1
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self.allowed()
        self.connection.execute.assert_called_once()

    def test_invalid_physical_states_denied_without_sql(self):
        for status in (
            TransactionStatus.INERROR, TransactionStatus.UNKNOWN,
            TransactionStatus.ACTIVE, object(),
        ):
            with self.subTest(status=status):
                self.driver.info.transaction_status = status
                self.denied()

    def test_missing_or_inactive_logical_transaction_denied(self):
        for change in (
            lambda: setattr(self.connection.in_transaction, "return_value", False),
            lambda: setattr(self.connection.get_transaction, "return_value", None),
            lambda: setattr(self.transaction, "is_active", False),
        ):
            with self.subTest(change=change):
                self.setUp()
                change()
                self.denied()

    def test_closed_or_invalidated_connection_denied(self):
        self.connection.closed = True
        self.denied()
        self.connection.closed = False
        self.connection.invalidated = True
        self.denied()

    def test_wrong_dialect_or_driver_denied(self):
        self.connection.dialect.name = "sqlite"
        self.denied()
        self.connection.dialect.name = "postgresql"
        self.connection.dialect.driver = "psycopg2"
        self.denied()
        self.connection.dialect.driver = "psycopg"
        self.connection.connection.driver_connection = object()
        self.denied()

    def test_absent_driver_attribute_or_unknown_options_denied(self):
        self.connection.connection = object()
        self.denied()
        self.connection.connection = SimpleNamespace(driver_connection=self.driver)
        self.connection.get_execution_options.return_value = Mock()
        self.denied()

    def test_inspection_exception_is_redacted_before_sql(self):
        self.connection.get_execution_options.side_effect = RuntimeError(
            "sensitive driver detail"
        )
        self.denied()

    def test_missing_or_unreadable_transaction_status_is_denied(self):
        self.driver.info = object()
        self.denied()

    def test_connection_swap_after_idle_start_is_denied(self):
        self.driver.info.transaction_status = TransactionStatus.IDLE

        def swap_connection(_statement):
            self.driver.info.transaction_status = TransactionStatus.INTRANS
            self.connection.connection = SimpleNamespace(
                driver_connection=create_autospec(PsycopgConnection, instance=True)
            )
            return Mock(scalar_one=Mock(return_value=1))

        self.connection.execute.side_effect = swap_connection
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self.allowed()
        self.connection.execute.assert_called_once()

    def test_physical_state_lost_after_idle_start_is_denied(self):
        events = []

        class StatusInfo:
            def __init__(self):
                self.state = TransactionStatus.IDLE

            @property
            def transaction_status(self):
                events.append(("read", self.state))
                return self.state

            def transition(self, state):
                self.state = state
                events.append(("transition", state))

        info = StatusInfo()
        self.driver.info = info

        def start_transaction(statement):
            self.assertEqual(str(statement), "SELECT 1")
            self.assertIs(self.connection.connection.driver_connection, self.driver)
            events.append(("sql", str(statement)))
            info.transition(TransactionStatus.INTRANS)

            def lose_transaction():
                self.assertIs(info.state, TransactionStatus.INTRANS)
                info.transition(TransactionStatus.INERROR)
                return 1

            return Mock(scalar_one=Mock(side_effect=lose_transaction))

        self.connection.execute.side_effect = start_transaction
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self.allowed()
        self.connection.execute.assert_called_once()
        self.assertEqual(events, [
            ("read", TransactionStatus.IDLE),
            ("sql", "SELECT 1"),
            ("transition", TransactionStatus.INTRANS),
            ("transition", TransactionStatus.INERROR),
            ("read", TransactionStatus.INERROR),
        ])
        self.connection.begin_nested.assert_not_called()
        self.connection.commit.assert_not_called()
        self.connection.rollback.assert_not_called()


if __name__ == "__main__":
    unittest.main()
