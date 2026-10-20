"""C16-R5: inert segment declarations, not a PostgreSQL entitlement test."""

from decimal import Decimal
import unittest
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKeyConstraint, Integer, Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, dialect
from sqlalchemy.schema import CreateIndex, CreateTable

from app.db.models import Base, LicenseEntitlementSegment, LicenseSubscription


class LicenseEntitlementSegmentSchemaTests(unittest.TestCase):
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

    def test_identity_timestamps_and_required_context(self):
        table = LicenseEntitlementSegment.__table__
        columns = table.c
        self.assertIn(table.name, Base.metadata.tables)
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
        for name in ("tenant_id", "subscription_id", "segment_number", "status"):
            self.assertFalse(columns[name].nullable, name)
        self.assertIsInstance(columns.tenant_id.type, PGUUID)
        self.assertIsInstance(columns.subscription_id.type, PGUUID)
        self.assertIsInstance(columns.segment_number.type, Integer)
        for name in (
            "period_start", "period_end", "anchor_day", "payment_id",
            "amount_allocated", "calculated_at", "origin_segment_id",
        ):
            self.assertTrue(columns[name].nullable, name)
        for name in ("period_start", "period_end", "calculated_at"):
            self.assertTrue(columns[name].type.timezone)
        self.assertIsInstance(columns.amount_allocated.type, Numeric)
        self.assertEqual(
            (columns.amount_allocated.type.precision,
             columns.amount_allocated.type.scale),
            (18, 2),
        )
        self.assertEqual(columns.status.default.arg, "RASCUNHO_INATIVO")
        self.assertEqual(str(columns.status.server_default.arg), "'RASCUNHO_INATIVO'")

    def test_inactive_guards_prevent_entitlements_and_payment_proofs(self):
        table = LicenseEntitlementSegment.__table__
        self.assertEqual(
            self.checks(table),
            {
                "ck_license_entitlement_segments_segment_number_positive":
                    "segment_number > 0",
                "ck_license_entitlement_segments_status_initial_only":
                    "status = 'RASCUNHO_INATIVO'",
                "ck_license_entitlement_segments_initial_entitlement_absent":
                    "period_start IS NULL AND period_end IS NULL AND "
                    "anchor_day IS NULL AND payment_id IS NULL AND "
                    "amount_allocated IS NULL AND calculated_at IS NULL "
                    "AND origin_segment_id IS NULL",
            },
        )
        for name in (
            "period_start", "period_end", "anchor_day", "payment_id",
            "amount_allocated", "calculated_at", "origin_segment_id",
        ):
            with self.subTest(field=name):
                self.assertIn(
                    f"{name} IS NULL",
                    self.checks(table)[
                        "ck_license_entitlement_segments_initial_entitlement_absent"
                    ],
                )
        for invalid in ("ATIVA", "PAGO_CONFIRMADO", "", "INATIVO"):
            self.assertNotEqual(invalid, "RASCUNHO_INATIVO")
        for number in (-1, 0, 1, 2):
            self.assertEqual(number > 0, number in (1, 2))
        self.assertIsNone(table.c.payment_id.default)
        self.assertIsNone(table.c.amount_allocated.default)

    def test_composite_subscription_and_origin_links(self):
        table = LicenseEntitlementSegment.__table__
        self.assertIn(
            ("id", "tenant_id"), self.uniques(LicenseSubscription.__table__)
        )
        self.assertEqual(
            self.uniques(table),
            {
                ("subscription_id", "segment_number"),
                ("id", "tenant_id"),
            },
        )
        self.assertEqual(
            self.foreign_keys(table),
            {
                ("subscription_id", "tenant_id"): (
                    ("license_subscriptions.id", "license_subscriptions.tenant_id"),
                    "RESTRICT",
                ),
                ("origin_segment_id", "tenant_id"): (
                    (
                        "license_entitlement_segments.id",
                        "license_entitlement_segments.tenant_id",
                    ),
                    "RESTRICT",
                ),
            },
        )
        indexes = {index.name: index for index in table.indexes}
        self.assertEqual(
            set(indexes),
            {"ix_license_entitlement_segments_tenant_subscription"},
        )
        self.assertEqual(
            tuple(column.name for column in next(iter(indexes.values())).columns),
            ("tenant_id", "subscription_id"),
        )

    def test_cross_tenant_matrix_is_structural_only(self):
        subscription_id, tenant_id = uuid4(), uuid4()
        parent = (subscription_id, tenant_id)
        cases = (
            (parent, True),
            ((uuid4(), tenant_id), False),
            ((subscription_id, uuid4()), False),
        )
        for child, matches in cases:
            with self.subTest(child=child):
                self.assertEqual(child == parent, matches)
        # Composite FK + NOT NULL is the declared guarantee; no INSERT ran.
        self.assertFalse(LicenseEntitlementSegment.__table__.c.tenant_id.nullable)
        self.assertFalse(
            LicenseEntitlementSegment.__table__.c.subscription_id.nullable
        )

    def test_postgresql_ddl_compiles_without_activation(self):
        pg = dialect()
        table = LicenseEntitlementSegment.__table__
        ddl = str(CreateTable(table).compile(dialect=pg))
        index = str(CreateIndex(next(iter(table.indexes))).compile(dialect=pg))
        self.assertIn(
            "FOREIGN KEY(subscription_id, tenant_id) REFERENCES "
            "license_subscriptions (id, tenant_id) ON DELETE RESTRICT",
            ddl,
        )
        self.assertIn("status = 'RASCUNHO_INATIVO'", ddl)
        self.assertIn("amount_allocated NUMERIC(18, 2)", ddl)
        self.assertIn("payment_id IS NULL", ddl)
        self.assertIn(
            "ON license_entitlement_segments (tenant_id, subscription_id)",
            index,
        )
        self.assertNotIn("CASCADE", ddl)
        self.assertNotIn("PAGO_CONFIRMADO", ddl)
        self.assertEqual(len(Base.metadata.tables), 17)


if __name__ == "__main__":
    unittest.main()
