"""C15-R2: offline checks for the frozen PostgreSQL schema revision.

These tests inspect declarations and intercepted Alembic operations. They do
not connect to PostgreSQL or prove INSERT, upgrade, downgrade, or WAL recovery.
"""

import hashlib
import io
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from alembic.config import Config
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import dialect

from app.db.models import Base
from migrations.versions import c15r2_20261020_initial_schema as revision


C15_SOURCE_SHA256 = "d5b23fd54281242d6fc4837a860b3181a06ac57ece0ee4bfe32cedae04c4c420"
C15_TABLE_ORDER = (
    "license_plans", "user_identities", "contracting_parties",
    "license_price_versions", "tenants", "cycles", "license_offers",
    "role_grants", "memberships", "term_acceptances",
    "license_payment_obligations", "quotas", "payments", "payment_attempts",
    "payment_reconciliation_events",
)
C15_INDEX_NAMES = {
    "uq_license_plans_id_limits", "uq_user_identities_email_lower",
    "uq_license_price_versions_open_plan", "ix_tenants_admin_user_id",
    "ix_tenants_contracting_party_id", "ix_license_offers_tenant_party",
    "ix_license_offers_tenant_plan", "uq_role_grants_global_start",
    "uq_role_grants_tenant_start", "uq_memberships_active_identity_cycle",
    "ix_term_acceptances_tenant_offer",
    "ix_license_payment_obligations_tenant_offer",
    "ix_quotas_tenant_cycle_membership", "ix_payments_tenant_obligation",
    "ix_payments_tenant_offer", "uq_payments_provider_receiver_external",
    "ix_payment_attempts_tenant_payment_number",
    "ix_payment_reconciliation_events_tenant_payment_attempt",
}


class InitialMigrationSchemaTests(unittest.TestCase):
    @staticmethod
    def normalized(sql):
        return re.sub(r"\s+", " ", sql).strip()

    @classmethod
    def table_parts(cls, sql):
        return {
            cls.normalized(line.strip().rstrip(","))
            for line in sql.splitlines()[1:-1]
            if line.strip()
        }

    def test_revision_identity_and_dependency_order(self):
        self.assertEqual(revision.revision, "c15r2_20261020")
        self.assertIsNone(revision.down_revision)
        self.assertIsNone(revision.branch_labels)
        self.assertIsNone(revision.depends_on)
        self.assertEqual(len(Base.metadata.tables), 17)
        self.assertEqual(
            set(Base.metadata.tables),
            set(C15_TABLE_ORDER) | {
                "license_subscriptions", "license_entitlement_segments",
            },
        )
        self.assertEqual(revision.TABLE_ORDER, C15_TABLE_ORDER)
        self.assertNotIn("license_subscriptions", revision.TABLE_ORDER)

    def test_alembic_discovers_single_initial_revision_without_env(self):
        config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        scripts = ScriptDirectory.from_config(config)
        self.assertEqual(scripts.get_heads(), ["f2p4_20261022"])
        self.assertEqual(scripts.get_base(), revision.revision)
        self.assertEqual(
            scripts.get_revision("c16r5_20261020").down_revision,
            revision.revision,
        )

    def test_frozen_ddl_matches_independent_c15_fingerprint(self):
        # This digest is from the C15 Git blob before C16, not current ORM.
        source = Path(revision.__file__).read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), C15_SOURCE_SHA256)
        tables = tuple(
            sql.split()[2] for sql in revision.SCHEMA_DDL
            if sql.startswith("CREATE TABLE ")
        )
        indexes = {
            sql.split()[3] if sql.startswith("CREATE UNIQUE INDEX ")
            else sql.split()[2]
            for sql in revision.SCHEMA_DDL
            if sql.startswith(("CREATE INDEX ", "CREATE UNIQUE INDEX "))
        }
        self.assertEqual(tables, C15_TABLE_ORDER)
        self.assertEqual(indexes, C15_INDEX_NAMES)
        self.assertEqual(len(tables), 15)
        self.assertEqual(len(indexes), 18)

    def test_unique_index_precedes_dependent_offer(self):
        sql = revision.SCHEMA_DDL
        index_position = next(
            i for i, statement in enumerate(sql)
            if statement.startswith("CREATE UNIQUE INDEX uq_license_plans_id_limits ")
        )
        offer_position = next(
            i for i, statement in enumerate(sql)
            if statement.startswith("CREATE TABLE license_offers ")
        )
        self.assertLess(index_position, offer_position)

    def test_postgresql_specific_structure_is_retained(self):
        sql = "\n".join(revision.SCHEMA_DDL)
        for fragment in (
            "JSONB",
            "INET",
            "UUID",
            "TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL",
            "NUMERIC(18, 2)",
            "GENERATED ALWAYS AS (monthly_price * 10) STORED",
            "WHERE tenant_id IS NULL",
            "WHERE tenant_id IS NOT NULL",
            "WHERE effective_to IS NULL",
            "lower(email)",
            "environment IN ('DEMO', 'HOMOLOGACAO', 'PRODUCAO')",
            "REFERENCES payments (id, tenant_id, expected_amount, environment) ON DELETE RESTRICT",
            "REFERENCES payment_attempts (id, payment_id, tenant_id, environment) ON DELETE RESTRICT",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, sql)

    def test_revision_ddl_compiles_with_postgresql_dialect(self):
        pg = dialect()
        for statement in revision.SCHEMA_DDL:
            with self.subTest(statement=statement.splitlines()[0]):
                compiled = str(sa.DDL(statement).compile(dialect=pg))
                self.assertEqual(compiled, statement)
        for name in reversed(revision.TABLE_ORDER):
            statement = f"DROP TABLE {name}"
            self.assertEqual(str(sa.DDL(statement).compile(dialect=pg)), statement)

    def test_alembic_compiles_both_directions_in_memory(self):
        for direction, method, keyword, count in (
            ("upgrade", revision.upgrade, "CREATE TABLE ", 15),
            ("downgrade", revision.downgrade, "DROP TABLE ", 15),
        ):
            with self.subTest(direction=direction):
                output = io.StringIO()
                context = MigrationContext.configure(
                    dialect_name="postgresql",
                    opts={"as_sql": True, "output_buffer": output},
                )
                with patch.object(revision, "op", Operations(context)):
                    method()
                rendered = output.getvalue()
                self.assertEqual(rendered.count(keyword), count)
                if direction == "upgrade":
                    self.assertIn("CREATE UNIQUE INDEX uq_license_plans_id_limits", rendered)
                    self.assertIn("WHERE tenant_id IS NULL", rendered)
                    self.assertIn("CHECK (provider ~ '[^[:space:]]')", rendered)
                else:
                    self.assertNotIn("CASCADE", rendered)

    def test_upgrade_only_submits_frozen_schema_ddl(self):
        with patch.object(revision.op, "execute") as execute:
            revision.upgrade()
        statements = [call.args[0] for call in execute.call_args_list]
        self.assertEqual(
            tuple(statement.statement for statement in statements),
            revision.SCHEMA_DDL,
        )
        self.assertTrue(all(isinstance(statement, sa.DDL) for statement in statements))
        self.assertTrue(
            all(
                statement.statement.startswith(
                    ("CREATE TABLE ", "CREATE INDEX ", "CREATE UNIQUE INDEX ")
                )
                for statement in statements
            )
        )

    def test_downgrade_drops_tables_in_reverse_order_without_cascade(self):
        with patch.object(revision.op, "execute") as execute:
            revision.downgrade()
        statements = [call.args[0] for call in execute.call_args_list]
        self.assertEqual(
            tuple(statement.statement for statement in statements),
            tuple(f"DROP TABLE {name}" for name in reversed(revision.TABLE_ORDER)),
        )
        self.assertTrue(all(isinstance(statement, sa.DDL) for statement in statements))


if __name__ == "__main__":
    unittest.main()
