"""G3-C / IN04: compilação e stubs SEM conexão a PostgreSQL real."""
import unittest
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, create_autospec
from uuid import UUID

from psycopg import Connection as PsycopgConnection
from psycopg.pq import TransactionStatus
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection, Engine

from app.g3c_session_pg import (
    SessionRepositoryUnavailable, current_session_statement,
    read_current_session_identity,
)
from app.g3c_transaction_guards_offline import TransactionGateError


NOW = datetime(2026, 10, 23, 14, tzinfo=timezone.utc)
IDENTITY = UUID(int=501)
VERIFIER = b"V" * 32


class CurrentSessionPostgresOfflineTests(unittest.TestCase):
    def setUp(self):
        self.conn = create_autospec(Connection, instance=True)
        self.conn.in_transaction.return_value = True
        self.conn.closed = False
        self.conn.invalidated = False
        self.conn.get_transaction.return_value.is_active = True
        self.conn.dialect = SimpleNamespace(name="postgresql", driver="psycopg")
        self.conn.engine = create_autospec(Engine, instance=True)
        self.conn.engine.get_execution_options.return_value = {}
        self.conn.get_execution_options.return_value = {}
        self.driver = create_autospec(PsycopgConnection, instance=True)
        self.driver.autocommit = False
        self.driver.info = SimpleNamespace(
            transaction_status=TransactionStatus.INTRANS,
        )
        self.conn.connection = SimpleNamespace(driver_connection=self.driver)
        self.row = (
            IDENTITY, IDENTITY, "ATIVA", "ACTIVE",
            NOW - timedelta(minutes=30), NOW - timedelta(minutes=20),
            NOW - timedelta(minutes=1), NOW + timedelta(minutes=14), None,
        )
        self._load()

    def _load(self, clock=NOW, row=None):
        if row is None:
            row = self.row
        self.conn.execute.side_effect = [
            Mock(one_or_none=Mock(return_value=row)),
            Mock(scalar_one=Mock(return_value=clock)),
        ]

    def test_sql_uses_inner_joins_and_share_locks_on_three_rows(self):
        stmt = current_session_statement(verifier_sha256=VERIFIER)
        sql = str(stmt.compile(dialect=postgresql.dialect()))
        self.assertIn("identity_sessions.identity_id = user_identities.id", sql)
        self.assertIn("identity_credentials.identity_id = user_identities.id", sql)
        self.assertIn("identity_sessions.verifier_sha256 =", sql)
        self.assertIn(
            "FOR SHARE OF identity_sessions, user_identities, identity_credentials",
            sql,
        )
        self.assertNotIn("INSERT INTO", sql)
        self.assertNotIn("UPDATE identity_sessions SET", sql)

    def test_valid_session_returns_id_only(self):
        self.assertEqual(
            read_current_session_identity(self.conn, verifier_sha256=VERIFIER),
            IDENTITY,
        )
        self.assertEqual(self.conn.execute.call_count, 2)
        clock_sql = str(self.conn.execute.call_args_list[1].args[0].compile(
            dialect=postgresql.dialect()))
        self.assertIn("clock_timestamp()", clock_sql)

    def test_requires_explicit_transaction(self):
        self.conn.in_transaction.return_value = False
        with self.assertRaisesRegex(TransactionGateError, "^SESSION_LOOKUP_DENIED$"):
            read_current_session_identity(
                self.conn, verifier_sha256=VERIFIER,
            )
        self.conn.execute.assert_not_called()

    def test_invalid_verifier_fails_before_database(self):
        with self.assertRaisesRegex(TransactionGateError, "^SESSION_LOOKUP_DENIED$"):
            read_current_session_identity(
                self.conn, verifier_sha256=b"short",
            )
        self.conn.execute.assert_not_called()

    def test_absent_verifier_returns_none_without_time_query(self):
        self.conn.execute.side_effect = [
            Mock(one_or_none=Mock(return_value=None)),
        ]
        self.assertIsNone(
            read_current_session_identity(self.conn, verifier_sha256=VERIFIER))
        self.assertEqual(self.conn.execute.call_count, 1)

    def test_suspended_identity_revoked_credential_or_session_denied(self):
        alterations = (
            (IDENTITY, IDENTITY, "SUSPENSA", "ACTIVE") + self.row[4:],
            (IDENTITY, IDENTITY, "ATIVA", "REVOKED") + self.row[4:],
            self.row[:8] + (NOW,),
            (UUID(int=555),) + self.row[1:],
        )
        for altered in alterations:
            with self.subTest(status=altered[2]):
                self.conn.execute.reset_mock()
                self._load(row=altered)
                self.assertIsNone(
                    read_current_session_identity(self.conn, verifier_sha256=VERIFIER))

    def test_password_or_email_verified_after_session_denied(self):
        for index in (4, 5):
            current = list(self.row)
            current[index] = NOW - timedelta(seconds=30)
            self.conn.execute.reset_mock()
            self._load(row=tuple(current))
            self.assertIsNone(
                read_current_session_identity(self.conn, verifier_sha256=VERIFIER))

    def test_clock_after_waiting_for_lock_expires_session(self):
        self._load(clock=NOW + timedelta(minutes=20))
        self.assertIsNone(
            read_current_session_identity(self.conn, verifier_sha256=VERIFIER))

    def test_db_exception_is_generic(self):
        self.conn.execute.side_effect = RuntimeError("secret SQL detail")
        with self.assertRaisesRegex(
            SessionRepositoryUnavailable, "^SESSION_STORAGE_UNAVAILABLE$"
        ) as exc:
            read_current_session_identity(self.conn, verifier_sha256=VERIFIER)
        self.assertNotIn("secret", str(exc.exception))

    def test_autocommit_denied_before_session_lock(self):
        self.driver.autocommit = True
        with self.assertRaisesRegex(TransactionGateError, "^SESSION_LOOKUP_DENIED$"):
            read_current_session_identity(self.conn, verifier_sha256=VERIFIER)
        self.conn.execute.assert_not_called()

    def test_no_role_or_tenant_implicit_authorization(self):
        import inspect
        import app.g3c_session_pg as module
        source = inspect.getsource(module)
        self.assertNotIn("RoleGrant(", source)
        self.assertNotIn("create_engine", source)
        self.assertNotIn("psycopg.connect", source)


if __name__ == "__main__":
    unittest.main()
