"""C16-R5: schema-only checks; no PostgreSQL connection or license activation."""

from decimal import Decimal
import io
import re
import unittest
from unittest.mock import patch
from uuid import uuid4

from alembic.config import Config
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from pathlib import Path
from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKeyConstraint, Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, dialect
from sqlalchemy.schema import AddConstraint, CreateIndex, CreateTable

from app.db.models import Base, LicenseOffer, LicenseSubscription, TermAcceptance
from migrations.versions import c16r5_20261020_license_subscription_inactive as revision


class LicenseSubscriptionSchemaTests(unittest.TestCase):
    @staticmethod
    def uniques(table):
        return {
            tuple(column.name for column in constraint.columns)
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        }

    @staticmethod
    def foreign_keys(table):
        return {
            tuple(element.parent.name for element in constraint.elements): (
                tuple(element.target_fullname for element in constraint.elements),
                constraint.ondelete,
            )
            for constraint in table.constraints
            if isinstance(constraint, ForeignKeyConstraint)
        }

    @staticmethod
    def checks(table):
        return {
            constraint.name: str(constraint.sqltext)
            for constraint in table.constraints
            if isinstance(constraint, CheckConstraint)
        }

    @staticmethod
    def normalized(sql):
        return re.sub(r"\s+", " ", sql).strip().rstrip(";")

    @classmethod
    def table_parts(cls, sql):
        body = sql[sql.index("(\n") + 2:sql.rindex("\n)")]
        return {
            cls.normalized(line.strip().rstrip(","))
            for line in body.splitlines() if line.strip()
        }

    def test_identity_columns_and_inactive_values(self):
        table = LicenseSubscription.__table__
        columns = table.c
        self.assertIn("license_subscriptions", Base.metadata.tables)
        self.assertIsInstance(columns.id.type, PGUUID)
        self.assertTrue(columns.id.type.as_uuid)
        self.assertTrue(columns.id.primary_key)
        self.assertTrue(callable(columns.id.default.arg))
        for name in ("created_at", "updated_at"):
            self.assertIsInstance(columns[name].type, DateTime)
            self.assertTrue(columns[name].type.timezone)
            self.assertFalse(columns[name].nullable)
            self.assertIsNotNone(columns[name].server_default)
        self.assertIsNotNone(columns.updated_at.onupdate)
        for name in (
            "tenant_id", "contracting_party_id", "plan_id", "offer_id",
            "term_acceptance_id", "price_version_id", "period",
            "duration_months", "effective_price", "status",
        ):
            self.assertFalse(columns[name].nullable, name)
        for name in ("paid_payment_id", "starts_at", "ends_at", "anchor_day"):
            self.assertTrue(columns[name].nullable, name)
        for name in ("starts_at", "ends_at"):
            self.assertTrue(columns[name].type.timezone)
        self.assertIsInstance(columns.effective_price.type, Numeric)
        self.assertEqual(
            (columns.effective_price.type.precision, columns.effective_price.type.scale),
            (18, 2),
        )
        self.assertEqual(columns.status.default.arg, "RASCUNHO_INATIVO")
        self.assertEqual(str(columns.status.server_default.arg), "'RASCUNHO_INATIVO'")
        self.assertEqual(
            self.checks(table),
            {
                "ck_license_subscriptions_period_duration_valid":
                    "(period = 'MENSAL' AND duration_months = 1) OR "
                    "(period = 'ANUAL' AND duration_months = 12)",
                "ck_license_subscriptions_effective_price_positive":
                    "effective_price > 0",
                "ck_license_subscriptions_status_initial_only":
                    "status = 'RASCUNHO_INATIVO'",
                "ck_license_subscriptions_initial_entitlement_absent":
                    "paid_payment_id IS NULL AND starts_at IS NULL AND "
                    "ends_at IS NULL AND anchor_day IS NULL",
            },
        )
        self.assertFalse(columns.paid_payment_id.foreign_keys)
        for period, duration, valid in (
            ("MENSAL", 1, True), ("ANUAL", 12, True),
            ("MENSAL", 12, False), ("ANUAL", 1, False), ("TEST", 1, False),
        ):
            with self.subTest(period=period, duration=duration):
                self.assertEqual(
                    (period == "MENSAL" and duration == 1)
                    or (period == "ANUAL" and duration == 12),
                    valid,
                )

    def test_composite_links_and_commercial_uniqueness(self):
        offer_key = (
            "id", "tenant_id", "contracting_party_id", "plan_id",
            "price_version_id", "effective_price", "period", "duration_months",
        )
        self.assertIn(offer_key, self.uniques(LicenseOffer.__table__))
        self.assertIn(
            ("id", "offer_id", "tenant_id", "price_version_id", "effective_price"),
            self.uniques(TermAcceptance.__table__),
        )
        self.assertEqual(
            self.uniques(LicenseSubscription.__table__),
            {
                ("offer_id",), ("term_acceptance_id",), ("id", "tenant_id"),
            },
        )
        self.assertEqual(
            self.foreign_keys(LicenseSubscription.__table__),
            {
                ("tenant_id", "contracting_party_id"): (
                    ("tenants.id", "tenants.contracting_party_id"), "RESTRICT",
                ),
                ("offer_id", "tenant_id", "contracting_party_id", "plan_id",
                 "price_version_id", "effective_price", "period",
                 "duration_months"): (
                    tuple(f"license_offers.{name}" for name in offer_key),
                    "RESTRICT",
                ),
                ("term_acceptance_id", "offer_id", "tenant_id",
                 "price_version_id", "effective_price"): (
                    (
                        "term_acceptances.id", "term_acceptances.offer_id",
                        "term_acceptances.tenant_id",
                        "term_acceptances.price_version_id",
                        "term_acceptances.effective_price",
                    ),
                    "RESTRICT",
                ),
            },
        )
        indexes = {index.name: index for index in LicenseSubscription.__table__.indexes}
        self.assertEqual(set(indexes), {"ix_license_subscriptions_tenant_offer"})
        self.assertEqual(
            tuple(column.name for column in
                  indexes["ix_license_subscriptions_tenant_offer"].columns),
            ("tenant_id", "offer_id"),
        )
        self.assertNotIn(("tenant_id",), self.uniques(LicenseSubscription.__table__))

    def test_cross_scope_matrix_is_structural_only(self):
        offer_id, tenant_id, party_id, plan_id, version_id = (uuid4() for _ in range(5))
        price = Decimal("89.90")
        parent = (offer_id, tenant_id, party_id, plan_id, version_id,
                  price, "MENSAL", 1)
        variants = (
            parent,
            (uuid4(), tenant_id, party_id, plan_id, version_id, price, "MENSAL", 1),
            (offer_id, uuid4(), party_id, plan_id, version_id, price, "MENSAL", 1),
            (offer_id, tenant_id, uuid4(), plan_id, version_id, price, "MENSAL", 1),
            (offer_id, tenant_id, party_id, uuid4(), version_id, price, "MENSAL", 1),
            (offer_id, tenant_id, party_id, plan_id, uuid4(), price, "MENSAL", 1),
            (offer_id, tenant_id, party_id, plan_id, version_id,
             Decimal("89.91"), "MENSAL", 1),
            (offer_id, tenant_id, party_id, plan_id, version_id,
             price, "ANUAL", 12),
        )
        for child in variants:
            with self.subTest(child=child):
                self.assertEqual(child == parent, child is parent)
        # FK + NOT NULL in DDL protect these tuples; no INSERT was executed.
        for name in (
            "offer_id", "tenant_id", "contracting_party_id", "plan_id",
            "price_version_id", "effective_price", "period", "duration_months",
        ):
            self.assertFalse(LicenseSubscription.__table__.c[name].nullable)

    def test_revision_chain_and_offline_postgresql_ddl(self):
        config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        scripts = ScriptDirectory.from_config(config)
        self.assertEqual(revision.revision, "c16r5_20261020")
        self.assertEqual(revision.down_revision, "c15r2_20261020")
        self.assertEqual(scripts.get_base(), "c15r2_20261020")
        self.assertEqual(scripts.get_heads(), ["c16r5_20261020"])
        output = io.StringIO()
        context = MigrationContext.configure(
            dialect_name="postgresql",
            opts={"as_sql": True, "output_buffer": output},
        )
        with patch.object(revision, "op", Operations(context)):
            revision.upgrade()
        rendered = output.getvalue()
        self.assertEqual(rendered.count("CREATE TABLE "), 2)
        self.assertEqual(rendered.count("CREATE INDEX "), 2)
        self.assertIn(
            "ALTER TABLE license_offers ADD CONSTRAINT "
            "uq_license_offers_c16_subscription_link UNIQUE",
            rendered,
        )
        self.assertLess(
            rendered.index("uq_license_offers_c16_subscription_link"),
            rendered.index("CREATE TABLE license_subscriptions"),
        )
        self.assertLess(
            rendered.index("CREATE TABLE license_subscriptions"),
            rendered.index("CREATE TABLE license_entitlement_segments"),
        )
        pg = dialect()
        offer_key = next(
            constraint for constraint in LicenseOffer.__table__.constraints
            if constraint.name == "uq_license_offers_c16_subscription_link"
        )
        self.assertIn(
            self.normalized(str(AddConstraint(offer_key).compile(dialect=pg))),
            self.normalized(rendered),
        )
        for table_name in ("license_subscriptions", "license_entitlement_segments"):
            with self.subTest(table=table_name):
                match = re.search(
                    rf"CREATE TABLE {table_name} \(\n.*?\n\);",
                    rendered, re.DOTALL,
                )
                self.assertIsNotNone(match)
                expected = str(CreateTable(Base.metadata.tables[table_name]).compile(
                    dialect=pg
                ))
                self.assertEqual(self.table_parts(match.group()), self.table_parts(expected))
                index = next(iter(Base.metadata.tables[table_name].indexes))
                self.assertIn(
                    self.normalized(str(CreateIndex(index).compile(dialect=pg))),
                    self.normalized(rendered),
                )
        self.assertNotRegex(
            rendered, r"\b(?:INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|CREATE\s+DATABASE|CASCADE)\b"
        )

    def test_downgrade_order_is_explicit_without_cascade(self):
        output = io.StringIO()
        context = MigrationContext.configure(
            dialect_name="postgresql",
            opts={"as_sql": True, "output_buffer": output},
        )
        with patch.object(revision, "op", Operations(context)):
            revision.downgrade()
        rendered = output.getvalue()
        self.assertLess(
            rendered.index("DROP TABLE license_entitlement_segments"),
            rendered.index("DROP TABLE license_subscriptions"),
        )
        self.assertLess(
            rendered.index("DROP TABLE license_subscriptions"),
            rendered.index("DROP CONSTRAINT uq_license_offers_c16_subscription_link"),
        )
        self.assertEqual(rendered.count("DROP TABLE "), 2)
        self.assertEqual(rendered.count("DROP INDEX "), 2)
        self.assertNotIn("CASCADE", rendered)


if __name__ == "__main__":
    unittest.main()
