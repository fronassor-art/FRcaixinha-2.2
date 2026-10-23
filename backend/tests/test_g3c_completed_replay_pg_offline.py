"""Compilação SQL e simulações do leitor de replay (sem PostgreSQL real)."""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, create_autospec
from uuid import UUID

from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection

from app.g3c_completed_replay_pg import (
    ReplayRepositoryUnavailable, completed_replay_statement,
    fetch_verified_completed_replay,
)
from app.g3c_transaction_guards_offline import TransactionGateError


NOW = datetime(2026, 10, 23, 14, tzinfo=timezone.utc)
IDENTITY = UUID(int=411)
PARTY = UUID(int=412)
ORIGIN = b"O" * 32
ATTEMPT = b"A" * 32
FINGERPRINT = b"F" * 32


class ReplayPostgresStatementOfflineTests(unittest.TestCase):
    def setUp(self):
        self.conn = create_autospec(Connection, instance=True)
        self.conn.in_transaction.return_value = True
        self.row = (
            ORIGIN, ATTEMPT, FINGERPRINT,
            IDENTITY, PARTY, "COMPLETED",
            NOW - timedelta(minutes=1), NOW + timedelta(minutes=14),
            PARTY, "PF", IDENTITY, None,
        )
        self.conn.execute.side_effect = [
            Mock(one_or_none=Mock(return_value=self.row)),
            Mock(scalar_one=Mock(return_value=NOW)),
        ]

    def _read(self, **kw):
        args = dict(
            origin_digest=ORIGIN, attempt_digest=ATTEMPT,
            request_fingerprint=FINGERPRINT,
        )
        args.update(kw)
        return fetch_verified_completed_replay(self.conn, **args)

    def test_query_locks_both_rows_and_filters_server_side(self):
        statement = completed_replay_statement(
            origin_digest=ORIGIN, attempt_digest=ATTEMPT)
        sql = str(statement.compile(dialect=postgresql.dialect()))
        self.assertIn("FOR UPDATE OF registration_idempotency, contracting_parties", sql)
        self.assertIn("registration_idempotency.state =", sql)
        self.assertIn("registration_idempotency.party_id = contracting_parties.id", sql)
        self.assertNotIn("UPDATE registration_idempotency SET", sql)
        self.assertNotIn("INSERT INTO", sql)

    def test_matching_completed_pf_returns_existing_only(self):
        self.assertEqual(self._read(), (IDENTITY, PARTY))
        self.assertEqual(self.conn.execute.call_count, 2)
        sql = str(self.conn.execute.call_args_list[1].args[0].compile(
            dialect=postgresql.dialect()))
        self.assertIn("clock_timestamp()", sql)

    def test_matching_completed_pj_returns_existing_only(self):
        self.row = self.row[:9] + ("PJ", None, IDENTITY)
        self.conn.execute.side_effect = [
            Mock(one_or_none=Mock(return_value=self.row)),
            Mock(scalar_one=Mock(return_value=NOW)),
        ]
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
        self.conn.execute.side_effect = [
            Mock(one_or_none=Mock(return_value=None))
        ]
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read()
        self.assertEqual(self.conn.execute.call_count, 1)

    def test_crossed_pf_identity_is_denied(self):
        self.row = self.row[:10] + (UUID(int=100), None)
        self.conn.execute.side_effect = [
            Mock(one_or_none=Mock(return_value=self.row)),
            Mock(scalar_one=Mock(return_value=NOW)),
        ]
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read()

    def test_expired_after_waiting_for_lock_is_denied(self):
        self.conn.execute.side_effect = [
            Mock(one_or_none=Mock(return_value=self.row)),
            Mock(scalar_one=Mock(return_value=NOW + timedelta(minutes=20))),
        ]
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            self._read()

    def test_storage_error_is_neutral_without_secret(self):
        self.conn.execute.side_effect = RuntimeError("sensitive-db-detail")
        with self.assertRaisesRegex(
            ReplayRepositoryUnavailable, "^REPLAY_STORAGE_UNAVAILABLE$"
        ) as exc:
            self._read()
        self.assertNotIn("sensitive", str(exc.exception))

    def test_no_physical_postgresql_or_migration_in_suite(self):
        import inspect
        import app.g3c_completed_replay_pg as module
        source = inspect.getsource(module)
        self.assertNotIn("create_engine", source)
        self.assertNotIn("psycopg.connect", source)
        self.assertNotIn("alembic.command", source)


if __name__ == "__main__":
    unittest.main()
