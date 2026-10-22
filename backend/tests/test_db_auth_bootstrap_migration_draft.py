"""Inspeção offline da minuta P4; não prova upgrade ou rollback PostgreSQL."""

import io
from pathlib import Path
import unittest
from unittest.mock import patch

from alembic.config import Config
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from app.db.models import Base
from migrations.versions import f2p4_20261022_auth_bootstrap_draft as revision


TABLES = (
    "identity_credentials", "email_confirmation_challenges",
    "registration_idempotency", "identity_sessions",
)


class AuthBootstrapMigrationDraftTests(unittest.TestCase):
    def render(self, method):
        output = io.StringIO()
        context = MigrationContext.configure(
            dialect_name="postgresql",
            opts={"as_sql": True, "output_buffer": output},
        )
        with patch.object(revision, "op", Operations(context)):
            method()
        return output.getvalue()

    def test_single_head_extends_frozen_c16(self):
        config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        scripts = ScriptDirectory.from_config(config)
        self.assertEqual(revision.revision, "f2p4_20261022")
        self.assertEqual(revision.down_revision, "c16r5_20261020")
        self.assertEqual(scripts.get_heads(), [revision.revision])
        self.assertEqual(scripts.get_revision(revision.down_revision).down_revision,
                         "c15r2_20261020")
        self.assertEqual(revision._TABLE_ORDER, TABLES)

    def test_upgrade_compiles_four_tables_and_three_indexes(self):
        sql = self.render(revision.upgrade)
        self.assertEqual(sql.count("CREATE TABLE "), 4)
        self.assertEqual(sql.count("CREATE INDEX "), 3)
        positions = [sql.index(f"CREATE TABLE {name}") for name in TABLES]
        self.assertEqual(positions, sorted(positions))
        for expected in (
            "REFERENCES user_identities (id) ON DELETE RESTRICT",
            "REFERENCES contracting_parties (id) ON DELETE RESTRICT",
            "UNIQUE (origin_digest, attempt_digest)",
            "password_digest LIKE 'scrypt$v1$%%'",
            "INTERVAL '10 minutes'", "INTERVAL '15 minutes'",
            "octet_length(verifier_sha256) = 32",
            "PENDING_EMAIL", "INITIAL_EMAIL",
        ):
            with self.subTest(fragment=expected):
                self.assertIn(expected, sql)
        self.assertNotIn("CASCADE", sql)
        self.assertNotIn("INSERT INTO", sql)

    def test_downgrade_drops_only_new_objects_in_reverse_order(self):
        sql = self.render(revision.downgrade)
        self.assertEqual(sql.count("DROP TABLE "), 4)
        self.assertEqual(sql.count("DROP INDEX "), 3)
        positions = [sql.index(f"DROP TABLE {name}") for name in reversed(TABLES)]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn("CASCADE", sql)
        self.assertNotIn("user_identities", sql)
        self.assertNotIn("contracting_parties", sql)

    def test_draft_models_mirror_without_sql_connection(self):
        self.assertEqual(len(Base.metadata.tables), 21)
        self.assertEqual(set(TABLES) & set(Base.metadata.tables), set(TABLES))
        with patch("psycopg.connect") as connect:
            self.render(revision.upgrade)
            self.render(revision.downgrade)
        connect.assert_not_called()
