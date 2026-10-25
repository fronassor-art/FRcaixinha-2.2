"""G3-C / IN04: compilação e stubs SEM conexão a PostgreSQL real."""
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock, create_autospec
from uuid import UUID

from psycopg import Connection as PsycopgConnection
from psycopg.pq import TransactionStatus
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection, Engine

from app.g3c_session_pg import (
    SessionRepositoryUnavailable, current_session_statement,
    session_identity_lock_statement, session_credential_lock_statement,
    session_lock_statement, read_current_session_identity,
)
from app.g3c_transaction_guards_offline import TransactionGateError


NOW = datetime(2026, 10, 23, 14, tzinfo=timezone.utc)
IDENTITY = UUID(int=501)
SESSION = UUID(int=502)
VERIFIER = b"V" * 32


def _sql(call):
    return str(call.args[0].compile(dialect=postgresql.dialect()))


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
        self.identity = (
            IDENTITY, "ATIVA", NOW - timedelta(minutes=30),
        )
        self.credential = (
            IDENTITY, "ACTIVE", NOW - timedelta(minutes=20),
        )
        self.session = (
            SESSION, IDENTITY, NOW - timedelta(minutes=1),
            NOW + timedelta(minutes=14), None,
        )
        self._load()

    def _load(self, *, found="DEFAULT", identity="DEFAULT",
              credential="DEFAULT", session="DEFAULT", clock=NOW):
        candidate = (SESSION, IDENTITY) if found == "DEFAULT" else found
        person = self.identity if identity == "DEFAULT" else identity
        secret = self.credential if credential == "DEFAULT" else credential
        active = self.session if session == "DEFAULT" else session
        self.conn.execute.side_effect = [
            Mock(one_or_none=Mock(return_value=candidate)),
            Mock(one_or_none=Mock(return_value=person)),
            Mock(one_or_none=Mock(return_value=secret)),
            Mock(one_or_none=Mock(return_value=active)),
            Mock(scalar_one=Mock(return_value=clock)),
        ]

    def _read(self, verifier=VERIFIER):
        return read_current_session_identity(
            self.conn, verifier_sha256=verifier,
        )

    def test_sql_locates_then_locks_identity_credential_session(self):
        statements = (
            current_session_statement(verifier_sha256=VERIFIER),
            session_identity_lock_statement(identity_id=IDENTITY),
            session_credential_lock_statement(identity_id=IDENTITY),
            session_lock_statement(session_id=SESSION, verifier_sha256=VERIFIER),
        )
        sql = [str(stmt.compile(dialect=postgresql.dialect()))
               for stmt in statements]
        self.assertNotIn("FOR SHARE", sql[0])
        self.assertNotIn("FOR UPDATE", sql[0])
        self.assertIn("identity_sessions.verifier_sha256 =", sql[0])
        self.assertIn("FOR UPDATE OF user_identities", sql[1])
        self.assertIn("FOR SHARE OF identity_credentials", sql[2])
        self.assertIn("FOR SHARE OF identity_sessions", sql[3])
        self.assertTrue(all(" JOIN " not in value for value in sql))
        self.assertTrue(all("INSERT INTO" not in value for value in sql))

    def test_valid_session_returns_id_only(self):
        self.assertEqual(self._read(), IDENTITY)
        self.assertEqual(self.conn.execute.call_count, 5)
        calls = self.conn.execute.call_args_list
        for number, table in enumerate((
            "identity_sessions", "user_identities",
            "identity_credentials", "identity_sessions",
        )):
            self.assertIn(table, _sql(calls[number]))
        self.assertIn("clock_timestamp()", _sql(calls[4]))
        self.conn.commit.assert_not_called()
        self.conn.rollback.assert_not_called()
        self.conn.begin_nested.assert_not_called()

    def test_requires_explicit_transaction(self):
        self.conn.in_transaction.return_value = False
        with self.assertRaisesRegex(TransactionGateError, "^SESSION_LOOKUP_DENIED$"):
            self._read()
        self.conn.execute.assert_not_called()

    def test_invalid_verifier_fails_before_database(self):
        with self.assertRaisesRegex(TransactionGateError, "^SESSION_LOOKUP_DENIED$"):
            self._read(b"short")
        self.conn.execute.assert_not_called()

    def test_absent_verifier_returns_none_without_time_query(self):
        self._load(found=None)
        self.assertIsNone(self._read())
        self.assertEqual(self.conn.execute.call_count, 1)

    def test_preliminary_identity_link_changed_denied(self):
        self._load(found=(SESSION, UUID(int=999)))
        self.assertIsNone(self._read())
        self.assertEqual(self.conn.execute.call_count, 2)

    def test_missing_row_at_each_lock_denies_without_clock(self):
        for stage, kwargs, count in (
            ("identity", {"identity": None}, 2),
            ("credential", {"credential": None}, 3),
            ("session", {"session": None}, 4),
        ):
            with self.subTest(stage=stage):
                self.conn.execute.reset_mock()
                self._load(**kwargs)
                self.assertIsNone(self._read())
                self.assertEqual(self.conn.execute.call_count, count)

    def test_session_link_changed_after_wait_is_denied(self):
        altered = list(self.session)
        altered[1] = UUID(int=999)
        self._load(session=tuple(altered))
        self.assertIsNone(self._read())
        self.assertEqual(self.conn.execute.call_count, 4)

    def test_suspended_identity_revoked_credential_or_session_denied(self):
        cases = (
            {"identity": (IDENTITY, "SUSPENSA", self.identity[2])},
            {"credential": (IDENTITY, "REVOKED", self.credential[2])},
            {"session": self.session[:4] + (NOW,)},
        )
        for case in cases:
            with self.subTest(case=case):
                self.conn.execute.reset_mock()
                self._load(**case)
                self.assertIsNone(self._read())
                self.assertEqual(self.conn.execute.call_count, 5)

    def test_password_or_email_verified_after_session_denied(self):
        for case in (
            {"identity": (
                IDENTITY, "ATIVA", NOW - timedelta(seconds=30),
            )},
            {"credential": (
                IDENTITY, "ACTIVE", NOW - timedelta(seconds=30),
            )},
        ):
            with self.subTest(case=case):
                self.conn.execute.reset_mock()
                self._load(**case)
                self.assertIsNone(self._read())

    def test_clock_after_waiting_for_lock_expires_session(self):
        self._load(clock=NOW + timedelta(minutes=20))
        self.assertIsNone(self._read())
        self.assertEqual(self.conn.execute.call_count, 5)

    def test_db_exception_at_each_lock_is_generic(self):
        for step in range(5):
            with self.subTest(step=step):
                self.conn.execute.reset_mock()
                self._load()
                responses = list(self.conn.execute.side_effect)
                responses[step] = RuntimeError("secret SQL detail")
                self.conn.execute.side_effect = responses
                with self.assertRaisesRegex(
                    SessionRepositoryUnavailable, "^SESSION_STORAGE_UNAVAILABLE$"
                ) as exc:
                    self._read()
                self.assertNotIn("secret", str(exc.exception))
                self.assertIsNone(exc.exception.__cause__)
                self.assertEqual(self.conn.execute.call_count, step + 1)

    def test_autocommit_denied_before_session_lock(self):
        self.driver.autocommit = True
        with self.assertRaisesRegex(TransactionGateError, "^SESSION_LOOKUP_DENIED$"):
            self._read()
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
