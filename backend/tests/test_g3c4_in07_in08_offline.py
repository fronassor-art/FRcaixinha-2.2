"""IN-07/IN-08: bloqueio F2P4 e limites offline de DDL e TTL.

O contraexemplo destrutivo original permanece congelado nos testes de
auditoria F2P4. Nenhum teste aplica migration ou consulta PostgreSQL.
"""

import io
import inspect
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.schema import CreateIndex

from app.db.models import (
    EmailConfirmationChallenge, IdentitySession, RegistrationIdempotency,
)
from app.email_confirmation_offline import (
    prepare_email_challenge, verify_and_consume_email_challenge,
)
from app.offline_credentials import PasswordCheck
from app.opaque_sessions_offline import (
    prepare_opaque_session, resolve_opaque_session,
)
from migrations.versions import f2p4_20261022_auth_bootstrap_draft as revision


NOW = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)
IDENTITY = UUID(int=901)
CHALLENGE = UUID(int=902)
SESSION = UUID(int=903)
NEW_TABLES = (
    "identity_credentials", "email_confirmation_challenges",
    "registration_idempotency", "identity_sessions",
)


class _Entropy:
    def generate(self, length):
        return b"S" * length


class _Ids:
    def new_uuid(self):
        return SESSION


class _Consumer:
    def __init__(self):
        self.calls = 0

    def consume_once(self, _id, _verifier):
        self.calls += 1
        return True


class _SessionStore:
    def __init__(self, record):
        self.record = record
        self.calls = 0

    def find_by_verifier(self, _verifier):
        self.calls += 1
        return self.record


class G3C4In07In08OfflineTests(unittest.TestCase):
    @staticmethod
    def render(method):
        output = io.StringIO()
        context = MigrationContext.configure(
            dialect_name="postgresql",
            opts={"as_sql": True, "output_buffer": output},
        )
        with patch.object(revision, "op", Operations(context)):
            method()
        return output.getvalue()

    def test_in07_downgrade_has_no_executable_drop_calls(self):
        source = inspect.getsource(revision.downgrade)
        self.assertNotIn("op.drop_table(", source)
        self.assertNotIn("op.drop_index(", source)
        self.assertIn('raise RuntimeError("F2P4_DOWNGRADE_NOT_AUTHORIZED")',
                      source)

    def test_in07_downgrade_guard_precedes_any_alembic_operation(self):
        with patch.object(revision, "op") as operations:
            with self.assertRaisesRegex(
                RuntimeError, "^F2P4_DOWNGRADE_NOT_AUTHORIZED$"
            ):
                revision.downgrade()
        self.assertEqual(operations.method_calls, [])

    def test_in07_guard_has_no_row_count_bypass(self):
        source = inspect.getsource(revision.downgrade)
        self.assertNotIn("SELECT", source)
        self.assertNotIn("row_count", source)
        self.assertNotIn("getenv", source)
        self.assertNotIn("op.", source)
        # The historical seven-DROP counterexample remains in the audit tests.

    def test_in07_upgrade_remains_available_without_data_recovery_claim(self):
        upgrade = self.render(revision.upgrade)
        self.assertEqual(upgrade.count("CREATE TABLE "), 4)
        self.assertEqual(upgrade.count("CREATE INDEX "), 3)
        for name in NEW_TABLES:
            self.assertIn(f"CREATE TABLE {name}", upgrade)
        with self.assertRaisesRegex(
            RuntimeError, "^F2P4_DOWNGRADE_NOT_AUTHORIZED$"
        ):
            self.render(revision.downgrade)
        # This offline test does not establish real PostgreSQL rollback.

    def test_in08_check_constraints_limit_age_but_do_not_delete(self):
        cases = (
            (EmailConfirmationChallenge, "10 minutes", "issued_at"),
            (RegistrationIdempotency, "15 minutes", "created_at"),
            (IdentitySession, "15 minutes", "issued_at"),
        )
        for model, lifetime, start in cases:
            with self.subTest(table=model.__tablename__):
                table = model.__table__
                check = next(c for c in table.constraints
                             if isinstance(c, CheckConstraint)
                             and c.name == f"ck_{table.name}_lifetime")
                rule = str(check.sqltext)
                self.assertIn(f"expires_at > {start}", rule)
                self.assertIn(f"INTERVAL '{lifetime}'", rule)
                self.assertNotIn("DELETE", rule)
                self.assertNotIn("now()", rule)

    def test_in08_expiry_indexes_are_not_cleanup_jobs(self):
        for model in (
            EmailConfirmationChallenge, RegistrationIdempotency,
            IdentitySession,
        ):
            with self.subTest(table=model.__tablename__):
                indexes = [
                    idx for idx in model.__table__.indexes
                    if "expires_at" in idx.columns.keys()
                ]
                self.assertEqual(len(indexes), 1)
                sql = str(CreateIndex(indexes[0]).compile(dialect=dialect()))
                self.assertIn("CREATE INDEX", sql)
                self.assertNotIn("DELETE", sql)

    def test_in08_unique_constraints_apply_without_expiry_predicate(self):
        cases = (
            (EmailConfirmationChallenge, ("verifier_sha256",)),
            (RegistrationIdempotency, ("origin_digest", "attempt_digest")),
            (IdentitySession, ("verifier_sha256",)),
        )
        for model, columns in cases:
            with self.subTest(table=model.__tablename__):
                matching = [
                    c for c in model.__table__.constraints
                    if isinstance(c, UniqueConstraint)
                    and tuple(col.name for col in c.columns) == columns
                ]
                self.assertEqual(len(matching), 1)
                # A UNIQUE constraint is not a TTL-aware arbiter.
                self.assertIsNotNone(matching[0].name)

    def test_in08_expired_reservation_still_occupies_a_synthetic_key(self):
        """Counterexample, in memory: expiry does not erase a reserved key."""
        pair = (b"O" * 32, b"A" * 32)
        rows = {pair: {"state": "RESERVED",
                       "expires_at": NOW - timedelta(minutes=1)}}
        self.assertLess(rows[pair]["expires_at"], NOW)
        self.assertIn(pair, rows)
        self.assertEqual(rows[pair]["state"], "RESERVED")
        # Not a PostgreSQL UNIQUE/cleanup concurrency test.

    def test_in08_expired_email_challenge_fails_before_consumption(self):
        prepared = prepare_email_challenge(
            challenge_id=CHALLENGE, identity_id=IDENTITY,
            email="person@example.com", now=NOW, entropy=_Entropy(),
        )
        consumer = _Consumer()
        self.assertFalse(verify_and_consume_email_challenge(
            record=prepared.record, candidate=prepared.delivery_secret,
            identity_id=IDENTITY, email="person@example.com",
            now=NOW + timedelta(minutes=10), consumption=consumer,
        ))
        self.assertEqual(consumer.calls, 0)

    def test_in08_expired_session_fails_without_row_deletion(self):
        prepared = prepare_opaque_session(
            identity_id=IDENTITY, identity_status="ATIVA",
            email_verified_at=NOW - timedelta(minutes=1),
            password_check=PasswordCheck(True, False),
            now=NOW, entropy=_Entropy(), ids=_Ids(),
        )
        store = _SessionStore(prepared.record)
        self.assertIsNone(resolve_opaque_session(
            token=prepared.delivery_token,
            now=NOW + timedelta(minutes=15), store=store,
        ))
        self.assertEqual(store.calls, 1)
        self.assertIs(store.record, prepared.record)

    def test_in07_in08_ddl_inspection_never_opens_postgres(self):
        with patch("psycopg.connect") as pg:
            self.render(revision.upgrade)
            with self.assertRaisesRegex(
                RuntimeError, "^F2P4_DOWNGRADE_NOT_AUTHORIZED$"
            ):
                self.render(revision.downgrade)
            str(CreateIndex(next(iter(
                RegistrationIdempotency.__table__.indexes
            ))).compile(dialect=dialect()))
        pg.assert_not_called()


if __name__ == "__main__":
    unittest.main()
