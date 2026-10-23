"""IN-02: testes sintéticos do writer com SQL compilado, sem banco real."""
import base64
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, create_autospec, patch
from uuid import UUID

from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection

from app.email_confirmation_offline import EmailChallengeRecord
from app.identity_registration_offline import (
    PreparedIdentity, PreparedParty, PreparedRegistration,
)
from app.initial_registration_bootstrap import InitialRegistrationIntent
from app.offline_credentials import PasswordDigest
from app.g3c_initial_registration_pg import (
    InitialRegistrationStorageUnavailable, InitialRegistrationWriteResult,
    complete_attempt_statement, reserve_attempt_statement,
    write_initial_registration_within_transaction,
)
from app.g3c_transaction_guards_offline import TransactionGateError


NOW = datetime(2026, 10, 23, 14, tzinfo=timezone.utc)
IDENTITY = UUID(int=10010)
PARTY = UUID(int=10011)
CHALLENGE = UUID(int=10012)
ORIGIN = b"O" * 32
ATTEMPT = b"A" * 32
FINGERPRINT = b"F" * 32
VERIFIER = b"V" * 32


def intent(pj=False):
    identity = PreparedIdentity(
        IDENTITY, "Pessoa Ficticia", b"encrypted",
        b"C" * 32, "person@example.org", "91912345678",
    )
    party = PreparedParty(
        PARTY, "PJ" if pj else "PF", "Pessoa Ficticia",
        None if pj else IDENTITY,
        IDENTITY if pj else None,
        b"encrypted-cnpj" if pj else None,
        b"N" * 32 if pj else None,
    )
    challenge = EmailChallengeRecord(
        CHALLENGE, IDENTITY, identity.email,
        NOW, NOW + timedelta(minutes=10), VERIFIER,
    )
    return InitialRegistrationIntent(
        PreparedRegistration(identity, party),
        f"local:{IDENTITY}",
        PasswordDigest(
            "scrypt$v1$16384$8$1$"
            + base64.b64encode(b"S" * 16).decode("ascii") + "$"
            + base64.b64encode(b"H" * 32).decode("ascii")
        ),
        "PENDING_EMAIL", challenge, ORIGIN, ATTEMPT, FINGERPRINT,
        NOW + timedelta(minutes=15),
    )


class InitialRegistrationPGOfflineTests(unittest.TestCase):
    def setUp(self):
        self.conn = create_autospec(Connection, instance=True)
        self.conn.in_transaction.return_value = True
        self.intent = intent()
        self.reservation = UUID(int=20020)

    def _run(self):
        with patch("app.g3c_initial_registration_pg.uuid4",
                   return_value=self.reservation):
            self.conn.execute.side_effect = [
                Mock(scalar_one_or_none=Mock(return_value=self.reservation)),
                Mock(), Mock(), Mock(), Mock(),
                Mock(scalar_one_or_none=Mock(return_value=self.reservation)),
            ]
            return write_initial_registration_within_transaction(
                self.conn, intent=self.intent,
            )

    def test_reservation_uses_unique_conflict_and_stable_server_ttl(self):
        stmt = reserve_attempt_statement(
            self.intent, reservation_id=self.reservation,
        )
        sql = str(stmt.compile(dialect=postgresql.dialect()))
        self.assertIn("INSERT INTO registration_idempotency", sql)
        self.assertIn(
            "ON CONFLICT ON CONSTRAINT uq_registration_idempotency_origin_attempt DO NOTHING",
            sql,
        )
        self.assertIn("statement_timestamp()", sql)
        self.assertIn("INTERVAL '15 minutes'", sql)
        self.assertIn("RETURNING registration_idempotency.id", sql)

    def test_completion_is_conditional_and_cannot_revive_expired(self):
        stmt = complete_attempt_statement(
            self.intent, reservation_id=self.reservation,
        )
        sql = str(stmt.compile(dialect=postgresql.dialect()))
        self.assertIn("UPDATE registration_idempotency SET", sql)
        self.assertIn("state=", sql)
        self.assertIn("expires_at > clock_timestamp()", sql)
        self.assertIn("request_fingerprint =", sql)
        self.assertIn("RETURNING registration_idempotency.id", sql)

    def test_new_pf_registration_is_one_savepoint_without_commit(self):
        outcome = self._run()
        self.assertEqual(
            outcome, InitialRegistrationWriteResult(IDENTITY, PARTY, True),
        )
        self.conn.begin_nested.assert_called_once()
        self.assertEqual(self.conn.execute.call_count, 6)
        sql = " ".join(
            str(call.args[0].compile(dialect=postgresql.dialect()))
            for call in self.conn.execute.call_args_list
        )
        for name in (
            "registration_idempotency", "user_identities",
            "contracting_parties", "identity_credentials",
            "email_confirmation_challenges",
        ):
            self.assertIn(name, sql)
        self.assertIn("INTERVAL '10 minutes'", sql)
        self.assertNotIn("COMMIT", sql)
        self.assertNotIn("role_grants", sql)
        self.assertNotIn("tenants", sql)
        self.assertNotIn("license_", sql)

    def test_new_pj_stays_preliminary(self):
        self.intent = intent(pj=True)
        outcome = self._run()
        self.assertEqual((outcome.identity_id, outcome.party_id, outcome.created),
                         (IDENTITY, PARTY, True))
        party_stmt = self.conn.execute.call_args_list[2].args[0]
        compiled = party_stmt.compile(dialect=postgresql.dialect())
        self.assertIn("contracting_parties", str(compiled))
        self.assertIn("PRELIMINAR", compiled.params.values())
        self.assertNotIn("APTO", compiled.params.values())

    def test_duplicate_completed_uses_trusted_replay_only(self):
        self.conn.execute.side_effect = [
            Mock(scalar_one_or_none=Mock(return_value=None))
        ]
        with patch("app.g3c_initial_registration_pg.fetch_verified_completed_replay",
                   return_value=(IDENTITY, PARTY)) as reader:
            outcome = write_initial_registration_within_transaction(
                self.conn, intent=self.intent,
            )
        self.assertEqual(outcome, InitialRegistrationWriteResult(
            IDENTITY, PARTY, False))
        reader.assert_called_once()
        self.assertEqual(self.conn.execute.call_count, 1)

    def test_prior_reserved_or_conflicting_fingerprint_is_denied(self):
        self.conn.execute.side_effect = [
            Mock(scalar_one_or_none=Mock(return_value=None))
        ]
        with patch("app.g3c_initial_registration_pg.fetch_verified_completed_replay",
                   side_effect=TransactionGateError("REPLAY_DENIED")):
            with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
                write_initial_registration_within_transaction(
                    self.conn, intent=self.intent,
                )
        self.assertEqual(self.conn.execute.call_count, 1)

    def test_requires_outer_transaction(self):
        self.conn.in_transaction.return_value = False
        with self.assertRaisesRegex(
            TransactionGateError, "^REGISTRATION_WRITE_DENIED$"
        ):
            write_initial_registration_within_transaction(
                self.conn, intent=self.intent,
            )
        self.conn.execute.assert_not_called()
        self.conn.begin_nested.assert_not_called()

    def test_invalid_intent_denied_before_accessing_database(self):
        for invalid in (
            replace(self.intent, origin_digest=b"short"),
            replace(self.intent, credential_state="ACTIVE"),
            replace(self.intent, auth_subject="remote:someone"),
            replace(self.intent, challenge=replace(
                self.intent.challenge, expires_at=NOW + timedelta(minutes=11),
            )),
            replace(self.intent, challenge=replace(
                self.intent.challenge, email="changed@example.org",
            )),
            replace(self.intent, registration=replace(
                self.intent.registration,
                party=replace(self.intent.registration.party,
                              pf_user_id=UUID(int=50505)),
            )),
        ):
            with self.subTest(status=invalid.credential_state):
                with self.assertRaisesRegex(
                    TransactionGateError, "^REGISTRATION_WRITE_DENIED$"
                ):
                    write_initial_registration_within_transaction(
                        self.conn, intent=invalid,
                    )
        self.conn.execute.assert_not_called()

    def test_prepared_digest_with_fake_scrypt_fields_is_denied_before_sql(self):
        """Um prefixo scrypt$v1$ sem salt e hash válidos não basta."""
        invalid = replace(
            self.intent,
            password_digest=PasswordDigest(
                "scrypt$v1$16384$8$1$not-valid-base64!$not-a-hash!"
            ),
        )
        with self.assertRaisesRegex(
            TransactionGateError, "^REGISTRATION_WRITE_DENIED$"
        ):
            write_initial_registration_within_transaction(
                self.conn, intent=invalid,
            )
        self.conn.execute.assert_not_called()

    def test_prepared_attempt_expiration_guards_final_commit_sql(self):
        """O escritor não pode transformar preparação vencida em nova tentativa."""
        statement = complete_attempt_statement(
            self.intent, reservation_id=self.reservation,
        )
        compiled = statement.compile(dialect=postgresql.dialect())
        sql = str(compiled)
        self.assertIn("registration_idempotency.expires_at > clock_timestamp()", sql)
        self.assertIn("clock_timestamp() <", sql)
        self.assertIn(self.intent.attempt_expires_at, compiled.params.values())

    def test_revoked_challenge_and_invalid_attempt_windows_fail_before_sql(self):
        for invalid in (
            replace(self.intent, attempt_expires_at=None),
            replace(self.intent, attempt_expires_at=NOW.replace(tzinfo=None)),
            replace(self.intent, attempt_expires_at=NOW + timedelta(minutes=16)),
            replace(self.intent, attempt_expires_at=NOW + timedelta(minutes=9)),
            replace(self.intent, challenge=replace(
                self.intent.challenge, revoked_at=NOW,
            )),
            replace(self.intent, challenge=replace(
                self.intent.challenge, issued_at=NOW + timedelta(minutes=1),
            )),
        ):
            with self.subTest(challenge_revoked=invalid.challenge.revoked_at is not None):
                self.conn.execute.reset_mock()
                with self.assertRaisesRegex(
                    TransactionGateError, "^REGISTRATION_WRITE_DENIED$",
                ):
                    write_initial_registration_within_transaction(
                        self.conn, intent=invalid,
                    )
                self.conn.execute.assert_not_called()

    def test_claim_returning_wrong_reservation_denied_without_writes(self):
        self.conn.execute.side_effect = [
            Mock(scalar_one_or_none=Mock(return_value=UUID(int=999999)))
        ]
        with self.assertRaisesRegex(
            TransactionGateError, "^REGISTRATION_WRITE_DENIED$"
        ):
            write_initial_registration_within_transaction(
                self.conn, intent=self.intent,
            )
        self.assertEqual(self.conn.execute.call_count, 1)

    def test_expired_completion_forces_savepoint_rollback(self):
        with patch("app.g3c_initial_registration_pg.uuid4",
                   return_value=self.reservation):
            self.conn.execute.side_effect = [
                Mock(scalar_one_or_none=Mock(return_value=self.reservation)),
                Mock(), Mock(), Mock(), Mock(),
                Mock(scalar_one_or_none=Mock(return_value=None)),
            ]
            with self.assertRaisesRegex(
                TransactionGateError, "^REGISTRATION_WRITE_DENIED$"
            ):
                write_initial_registration_within_transaction(
                    self.conn, intent=self.intent,
                )
        self.assertEqual(self.conn.execute.call_count, 6)
        self.assertTrue(self.conn.begin_nested.return_value.__exit__.called)
        self.assertIsNotNone(self.conn.begin_nested.return_value.__exit__.call_args.args[0])

    def test_database_failure_is_neutral_and_rolls_back(self):
        with patch("app.g3c_initial_registration_pg.uuid4",
                   return_value=self.reservation):
            self.conn.execute.side_effect = [
                Mock(scalar_one_or_none=Mock(return_value=self.reservation)),
                RuntimeError("sensitive DB DETAIL"),
            ]
            with self.assertRaisesRegex(
                InitialRegistrationStorageUnavailable,
                "^REGISTRATION_STORAGE_UNAVAILABLE$",
            ) as exc:
                write_initial_registration_within_transaction(
                    self.conn, intent=self.intent,
                )
        self.assertNotIn("sensitive", str(exc.exception))
        self.assertIsNone(exc.exception.__cause__)
        self.assertTrue(self.conn.begin_nested.return_value.__exit__.called)

    def test_public_repr_redacts_and_writer_does_not_return_secret(self):
        result = self._run()
        self.assertNotIn(str(IDENTITY), repr(result))
        self.assertFalse(hasattr(result, "delivery_secret"))
        self.assertFalse(hasattr(result, "password_digest"))

    def test_no_pg_connection_creation_or_implicit_service(self):
        import inspect
        import app.g3c_initial_registration_pg as module
        source = inspect.getsource(module)
        for forbidden in (
            "psycopg.connect(", "create_engine(", "alembic.command",
            "connection.commit(", "connection.rollback(", "send_message(",
            "RoleGrant(", "DELETE FROM",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
