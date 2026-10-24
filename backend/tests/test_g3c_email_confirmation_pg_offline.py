"""IN-03: ensaios sintéticos de confirmação futura, sem conexão PostgreSQL."""
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock, create_autospec
from uuid import UUID

from psycopg import Connection as PsycopgConnection
from psycopg.pq import TransactionStatus
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection, Engine

from app.email_confirmation_offline import _digest
from app.g3c_email_confirmation_pg import (
    EmailConfirmationStorageUnavailable,
    challenge_lookup_statement, email_identity_lock_statement,
    email_credential_lock_statement, challenge_lock_statement,
    challenge_consume_statement, identity_verify_statement,
    confirm_initial_email_within_transaction,
)
from app.g3c_transaction_guards_offline import TransactionGateError


NOW = datetime(2026, 10, 23, 13, tzinfo=timezone.utc)
USER = UUID(int=17001)
CHALLENGE = UUID(int=17002)
CONTACT = "person@example.org"
SECRET = b"S" * 32
DIGEST = _digest(CHALLENGE, USER, CONTACT, SECRET)


def _sql(call):
    return str(call.args[0].compile(dialect=postgresql.dialect()))


class InitialEmailPostgresOfflineTests(unittest.TestCase):
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
        self.conn.begin_nested.return_value.__exit__.return_value = False
        self.identity = (
            USER, CONTACT, "PENDENTE", None, NOW - timedelta(minutes=2),
        )
        self.credential = (USER, "PENDING_EMAIL")
        self.challenge = (
            CHALLENGE, USER, DIGEST, "INITIAL_EMAIL",
            NOW - timedelta(minutes=1), NOW + timedelta(minutes=9),
            None, None,
        )
        self._results()

    def _results(self, *, found="DEFAULT", identity="DEFAULT",
                 credential="DEFAULT", challenge="DEFAULT", clock=NOW,
                 consumed=CHALLENGE, verified=USER):
        candidate = (CHALLENGE, USER) if found == "DEFAULT" else found
        person = self.identity if identity == "DEFAULT" else identity
        secret = self.credential if credential == "DEFAULT" else credential
        proof = self.challenge if challenge == "DEFAULT" else challenge
        self.conn.execute.side_effect = [
            Mock(one_or_none=Mock(return_value=candidate)),
            Mock(one_or_none=Mock(return_value=person)),
            Mock(one_or_none=Mock(return_value=secret)),
            Mock(one_or_none=Mock(return_value=proof)),
            Mock(scalar_one=Mock(return_value=clock)),
            Mock(scalar_one_or_none=Mock(return_value=consumed)),
            Mock(scalar_one_or_none=Mock(return_value=verified)),
        ]

    def _confirm(self, **kwargs):
        args = dict(challenge_id=CHALLENGE, identity_id=USER, candidate=SECRET)
        args.update(kwargs)
        return confirm_initial_email_within_transaction(self.conn, **args)

    def _assert_rollback_to_savepoint(self):
        self.conn.begin_nested.assert_called_once()
        self.assertIsNotNone(
            self.conn.begin_nested.return_value.__exit__.call_args.args[0]
        )
        self.conn.commit.assert_not_called()
        self.conn.rollback.assert_not_called()

    def test_query_locks_identity_then_credential_then_challenge(self):
        statements = (
            challenge_lookup_statement(challenge_id=CHALLENGE),
            email_identity_lock_statement(identity_id=USER),
            email_credential_lock_statement(identity_id=USER),
            challenge_lock_statement(challenge_id=CHALLENGE, identity_id=USER),
        )
        sql = [str(stmt.compile(dialect=postgresql.dialect()))
               for stmt in statements]
        self.assertNotIn("FOR UPDATE", sql[0])
        self.assertIn("FOR UPDATE OF user_identities", sql[1])
        self.assertIn("FOR UPDATE OF identity_credentials", sql[2])
        self.assertIn("FOR UPDATE OF email_confirmation_challenges", sql[3])
        self.assertTrue(all(" JOIN " not in value for value in sql))

    def test_challenge_update_conditional_and_clock_from_database(self):
        statement = challenge_consume_statement(
            challenge_id=CHALLENGE, identity_id=USER,
            verifier_sha256=DIGEST,
        )
        sql = str(statement.compile(dialect=postgresql.dialect()))
        for phrase in (
            "UPDATE email_confirmation_challenges SET",
            "consumed_at=clock_timestamp()",
            "consumed_at IS NULL",
            "revoked_at IS NULL",
            "purpose =",
            "expires_at > clock_timestamp()",
            "issued_at <= clock_timestamp()",
            "RETURNING email_confirmation_challenges.id",
        ):
            self.assertIn(phrase, sql)

    def test_identity_update_marks_only_verified_at_not_active(self):
        statement = identity_verify_statement(identity_id=USER, email=CONTACT)
        sql = str(statement.compile(dialect=postgresql.dialect()))
        self.assertIn("UPDATE user_identities SET", sql)
        self.assertIn("email_verified_at=clock_timestamp()", sql)
        self.assertIn("email_verified_at IS NULL", sql)
        self.assertIn("user_identities.status =", sql)
        self.assertIn("user_identities.email =", sql)
        self.assertIn("RETURNING user_identities.id", sql)
        self.assertNotIn("status='ATIVA'", sql)

    def test_valid_verifier_and_current_contact_update_once(self):
        self.assertTrue(self._confirm())
        self.assertEqual(self.conn.execute.call_count, 7)
        calls = self.conn.execute.call_args_list
        for number, table in enumerate((
            "email_confirmation_challenges", "user_identities",
            "identity_credentials", "email_confirmation_challenges",
        )):
            self.assertIn(table, _sql(calls[number]))
        self.assertIn("clock_timestamp()", _sql(calls[4]))
        self.assertIn("UPDATE email_confirmation_challenges", _sql(calls[5]))
        self.assertIn("UPDATE user_identities", _sql(calls[6]))
        self.conn.begin_nested.assert_called_once()
        self.assertIsNone(
            self.conn.begin_nested.return_value.__exit__.call_args.args[0]
        )
        self.conn.commit.assert_not_called()
        self.conn.rollback.assert_not_called()

    def test_denies_without_outer_transaction_before_any_sql(self):
        self.conn.in_transaction.return_value = False
        with self.assertRaisesRegex(TransactionGateError, "^EMAIL_CONFIRMATION_DENIED$"):
            self._confirm()
        self.conn.execute.assert_not_called()
        self.conn.begin_nested.assert_not_called()

    def test_invalid_inputs_rejected_before_any_sql(self):
        bad = (
            {"candidate": b"small"},
            {"candidate": "token"},
            {"identity_id": UUID(int=0)},
            {"challenge_id": UUID(int=0)},
            {"challenge_id": USER},
        )
        for kw in bad:
            with self.subTest(keys=list(kw)):
                self.conn.execute.reset_mock()
                with self.assertRaisesRegex(
                    TransactionGateError, "^EMAIL_CONFIRMATION_DENIED$"
                ):
                    self._confirm(**kw)
                self.conn.execute.assert_not_called()

    def test_nonexistent_challenge_returns_false_without_mutation(self):
        self._results(found=None)
        self.assertFalse(self._confirm())
        self.assertEqual(self.conn.execute.call_count, 1)
        self._assert_rollback_to_savepoint()

    def test_preliminary_link_changed_denied_before_identity_lock(self):
        self._results(found=(CHALLENGE, UUID(int=999)))
        self.assertFalse(self._confirm())
        self.assertEqual(self.conn.execute.call_count, 1)
        self._assert_rollback_to_savepoint()

    def test_failure_at_each_lock_denies_before_mutation(self):
        for stage, kwargs, expected in (
            ("identity", {"identity": None}, 2),
            ("credential", {"credential": None}, 3),
            ("challenge", {"challenge": None}, 4),
        ):
            with self.subTest(stage=stage):
                self.conn.execute.reset_mock()
                self.conn.begin_nested.reset_mock()
                self._results(**kwargs)
                self.assertFalse(self._confirm())
                self.assertEqual(self.conn.execute.call_count, expected)
                self._assert_rollback_to_savepoint()

    def test_challenge_link_changed_after_wait_is_denied(self):
        altered = list(self.challenge)
        altered[1] = UUID(int=999)
        self._results(challenge=tuple(altered))
        self.assertFalse(self._confirm())
        self.assertEqual(self.conn.execute.call_count, 4)
        self._assert_rollback_to_savepoint()

    def test_wrong_secret_returns_false_without_update(self):
        self.assertFalse(self._confirm(candidate=b"W" * 32))
        self.assertEqual(self.conn.execute.call_count, 5)
        self._assert_rollback_to_savepoint()

    def test_email_change_invalidates_old_digest(self):
        changed = list(self.identity)
        changed[1] = "new@example.org"
        self._results(identity=tuple(changed))
        self.assertFalse(self._confirm())
        self.assertEqual(self.conn.execute.call_count, 5)

    def test_expired_revoked_consumed_wrong_purpose_denied(self):
        cases = (
            ("expired", "challenge", 5, NOW),
            ("consumed", "challenge", 6, NOW),
            ("revoked", "challenge", 7, NOW),
            ("purpose", "challenge", 3, "OTHER"),
            ("status", "identity", 2, "SUSPENSA"),
            ("verified", "identity", 3, NOW),
            ("credential", "credential", 1, "REVOKED"),
        )
        for label, target, index, value in cases:
            with self.subTest(case=label):
                self.conn.execute.reset_mock()
                self.conn.begin_nested.reset_mock()
                row = list(getattr(self, target))
                row[index] = value
                self._results(**{target: tuple(row)})
                self.assertFalse(self._confirm())
                self.assertEqual(self.conn.execute.call_count, 5)
                self._assert_rollback_to_savepoint()

    def test_server_clock_expiration_after_lock_denied(self):
        self._results(clock=NOW + timedelta(minutes=10))
        self.assertFalse(self._confirm())
        self.assertEqual(self.conn.execute.call_count, 5)

    def test_no_consume_when_update_guard_fails(self):
        self._results(consumed=None)
        self.assertFalse(self._confirm())
        self.assertEqual(self.conn.execute.call_count, 6)
        self._assert_rollback_to_savepoint()

    def test_identity_update_failure_raises_and_savepoint_rolls_back(self):
        self._results(verified=None)
        with self.assertRaisesRegex(
            EmailConfirmationStorageUnavailable,
            "^EMAIL_CONFIRMATION_STORAGE_UNAVAILABLE$",
        ):
            self._confirm()
        self.assertEqual(self.conn.execute.call_count, 7)
        self._assert_rollback_to_savepoint()

    def test_database_error_is_generic_and_rollback_scope_exists(self):
        self.conn.execute.side_effect = RuntimeError("sensitive-db-log")
        with self.assertRaisesRegex(
            EmailConfirmationStorageUnavailable,
            "^EMAIL_CONFIRMATION_STORAGE_UNAVAILABLE$",
        ) as caught:
            self._confirm()
        self.assertNotIn("sensitive", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self._assert_rollback_to_savepoint()

    def test_identity_changed_after_challenge_denies_old_verifier(self):
        changed = self.identity[:-1] + (NOW,)
        self._results(identity=changed)
        self.assertFalse(self._confirm())
        self.assertEqual(self.conn.execute.call_count, 5)

    def test_missing_identity_change_epoch_denies_without_update(self):
        changed = self.identity[:-1] + (None,)
        self._results(identity=changed)
        self.assertFalse(self._confirm())
        self.assertEqual(self.conn.execute.call_count, 5)

    def test_autocommit_denied_before_savepoint_or_email_lock(self):
        self.driver.autocommit = True
        with self.assertRaisesRegex(
            TransactionGateError, "^EMAIL_CONFIRMATION_DENIED$"
        ):
            self._confirm()
        self.conn.execute.assert_not_called()
        self.conn.begin_nested.assert_not_called()

    def test_only_mocked_sql_and_no_api_or_real_connection(self):
        import inspect
        import app.g3c_email_confirmation_pg as module
        source = inspect.getsource(module)
        for forbidden in (
            "psycopg.connect", "create_engine(", "alembic.command",
            "send_message(", "RoleGrant(", "delete(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
