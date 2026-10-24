"""Compilação SQL e simulações do leitor de replay (sem PostgreSQL real)."""
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock, create_autospec
from uuid import UUID

from psycopg import Connection as PsycopgConnection
from psycopg.pq import TransactionStatus
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection, Engine

from app.g3c_completed_replay_pg import (
    ReplayRepositoryUnavailable, completed_replay_statement,
    fetch_verified_completed_replay, replay_identity_lock_statement,
    replay_party_lock_statement, replay_recheck_statement,
)
from app.g3c_transaction_guards_offline import TransactionGateError


NOW = datetime(2026, 10, 23, 14, tzinfo=timezone.utc)
RESERVATION = UUID(int=410)
IDENTITY = UUID(int=411)
PARTY = UUID(int=412)
ORIGIN = b"O" * 32
ATTEMPT = b"A" * 32
FINGERPRINT = b"F" * 32


def _sql(call):
    return str(call.args[0].compile(dialect=postgresql.dialect()))


class ReplayPostgresStatementOfflineTests(unittest.TestCase):
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
        self.reserved = (
            RESERVATION, ORIGIN, ATTEMPT, FINGERPRINT,
            IDENTITY, PARTY, "COMPLETED",
            NOW - timedelta(minutes=1), NOW + timedelta(minutes=14),
        )
        self.party = (PARTY, "PF", IDENTITY, None)
        self._load()

    def _load(self, *, reserved="DEFAULT", identity=IDENTITY,
              party="DEFAULT", rechecked="DEFAULT", clock=NOW):
        first = self.reserved if reserved == "DEFAULT" else reserved
        part = self.party if party == "DEFAULT" else party
        again = self.reserved if rechecked == "DEFAULT" else rechecked
        self.conn.execute.side_effect = [
            Mock(one_or_none=Mock(return_value=first)),
            Mock(scalar_one_or_none=Mock(return_value=identity)),
            Mock(one_or_none=Mock(return_value=part)),
            Mock(one_or_none=Mock(return_value=again)),
            Mock(scalar_one=Mock(return_value=clock)),
        ]

    def _read(self, **kw):
        args = dict(
            origin_digest=ORIGIN, attempt_digest=ATTEMPT,
            request_fingerprint=FINGERPRINT,
        )
        args.update(kw)
        return fetch_verified_completed_replay(self.conn, **args)

    def test_query_locks_registration_then_identity_then_party(self):
        statements = (
            completed_replay_statement(
                origin_digest=ORIGIN, attempt_digest=ATTEMPT,
            ),
            replay_identity_lock_statement(identity_id=IDENTITY),
            replay_party_lock_statement(party_id=PARTY),
            replay_recheck_statement(reservation_id=RESERVATION),
        )
        sql = [str(stmt.compile(dialect=postgresql.dialect()))
               for stmt in statements]
        self.assertIn("FOR UPDATE OF registration_idempotency", sql[0])
        self.assertIn("registration_idempotency.state =", sql[0])
        self.assertNotIn(" JOIN ", sql[0])
        self.assertIn("FOR UPDATE OF user_identities", sql[1])
        self.assertIn("FOR UPDATE OF contracting_parties", sql[2])
        self.assertNotIn("FOR UPDATE", sql[3])
        self.assertTrue(all("INSERT INTO" not in value for value in sql))

    def test_matching_completed_pf_returns_existing_only(self):
        self.assertEqual(self._read(), (IDENTITY, PARTY))
        self.assertEqual(self.conn.execute.call_count, 5)
        calls = self.conn.execute.call_args_list
        for number, table in enumerate((
            "registration_idempotency", "user_identities",
            "contracting_parties", "registration_idempotency",
        )):
            self.assertIn(table, _sql(calls[number]))
        self.assertIn("clock_timestamp()", _sql(calls[4]))
        self.conn.commit.assert_not_called()
        self.conn.rollback.assert_not_called()
        self.conn.begin_nested.assert_not_called()

    def test_matching_completed_pj_returns_existing_only(self):
        self._load(party=(PARTY, "PJ", None, IDENTITY))
        self.assertEqual(self._read(), (IDENTITY, PARTY))

    def test_requires_existing_explicit_transaction(self):
        self.conn.in_transaction.return_value = False
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read()
        self.conn.execute.assert_not_called()

    def test_rejects_wrong_digest_without_sql(self):
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read(request_fingerprint=b"short")
        self.conn.execute.assert_not_called()

    def test_absent_row_is_generic_denial(self):
        self._load(reserved=None)
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read()
        self.assertEqual(self.conn.execute.call_count, 1)

    def test_bad_ids_are_denied_before_identity_lock(self):
        self._load(reserved=self.reserved[:4] + (None,) + self.reserved[5:])
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read()
        self.assertEqual(self.conn.execute.call_count, 1)

    def test_missing_identity_denied_before_party_lock(self):
        self._load(identity=None)
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read()
        self.assertEqual(self.conn.execute.call_count, 2)

    def test_missing_or_changed_party_denied_before_recheck(self):
        for party in (None, (UUID(int=999), "PF", IDENTITY, None)):
            with self.subTest(party=party):
                self.conn.execute.reset_mock()
                self._load(party=party)
                with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
                    self._read()
                self.assertEqual(self.conn.execute.call_count, 3)

    def test_registration_changed_after_wait_is_denied(self):
        changed = self.reserved[:5] + (UUID(int=999),) + self.reserved[6:]
        self._load(rechecked=changed)
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read()
        self.assertEqual(self.conn.execute.call_count, 4)

    def test_crossed_pf_identity_is_denied(self):
        self._load(party=(PARTY, "PF", UUID(int=100), None))
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read()

    def test_expired_after_waiting_for_lock_is_denied(self):
        self._load(clock=NOW + timedelta(minutes=20))
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read()
        self.assertEqual(self.conn.execute.call_count, 5)

    def test_storage_error_at_each_lock_is_neutral(self):
        for step in range(5):
            with self.subTest(step=step):
                self.conn.execute.reset_mock()
                self._load()
                responses = list(self.conn.execute.side_effect)
                responses[step] = RuntimeError("sensitive-db-detail")
                self.conn.execute.side_effect = responses
                with self.assertRaisesRegex(
                    ReplayRepositoryUnavailable, "^REPLAY_STORAGE_UNAVAILABLE$"
                ) as exc:
                    self._read()
                self.assertNotIn("sensitive", str(exc.exception))
                self.assertIsNone(exc.exception.__cause__)
                self.assertEqual(self.conn.execute.call_count, step + 1)

    def test_autocommit_denied_before_replay_lock(self):
        self.driver.autocommit = True
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read()
        self.conn.execute.assert_not_called()

    def test_no_physical_postgresql_or_migration_in_suite(self):
        import inspect
        import app.g3c_completed_replay_pg as module
        source = inspect.getsource(module)
        self.assertNotIn("create_engine", source)
        self.assertNotIn("psycopg.connect", source)
        self.assertNotIn("alembic.command", source)


if __name__ == "__main__":
    unittest.main()
