"""C10: esquema do catálogo; compila PostgreSQL sem abrir conexão."""

import unittest
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Computed,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.schema import CreateIndex, CreateTable

from app.db.models import Base, LicensePlan, LicensePriceVersion


class LicenseCatalogSchemaTests(unittest.TestCase):
    @staticmethod
    def checks(table):
        return {
            constraint.name: str(constraint.sqltext)
            for constraint in table.constraints
            if isinstance(constraint, CheckConstraint)
        }

    @staticmethod
    def uniques(table):
        return {
            tuple(column.name for column in constraint.columns)
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        }

    def test_tables_identity_and_timestamps(self):
        for model in (LicensePlan, LicensePriceVersion):
            with self.subTest(model=model.__name__):
                table = model.__table__
                self.assertIn(table.name, Base.metadata.tables)
                self.assertIsInstance(table.c.id.type, PGUUID)
                self.assertTrue(table.c.id.primary_key)
                self.assertTrue(callable(table.c.id.default.arg))
                for name in ("created_at", "updated_at"):
                    column = table.c[name]
                    self.assertIsInstance(column.type, DateTime)
                    self.assertTrue(column.type.timezone)
                    self.assertFalse(column.nullable)
                    self.assertIsNotNone(column.server_default)

    def test_plan_names_capacity_and_initial_lock(self):
        table = LicensePlan.__table__
        columns = table.c
        self.assertEqual(
            set(columns.keys()),
            {"id", "created_at", "updated_at", "name",
             "member_limit", "quota_limit", "status"},
        )
        self.assertFalse(columns.name.nullable)
        self.assertEqual(self.uniques(table), {("name",)})
        for name in ("member_limit", "quota_limit"):
            self.assertIsInstance(columns[name].type, Integer)
            self.assertTrue(columns[name].nullable)
        self.assertEqual(columns.status.default.arg, "INATIVO")
        self.assertEqual(str(columns.status.server_default.arg), "'INATIVO'")
        checks = self.checks(table)
        self.assertEqual(checks["ck_license_plans_status_initial_only"],
                         "status = 'INATIVO'")
        self.assertEqual(
            checks["ck_license_plans_name_valid"],
            "name IN ('Essencial', 'Intermediário', 'Ampliado')",
        )
        capacity = checks["ck_license_plans_approved_capacity"]
        for fragment in (
            "member_limit IS NOT DISTINCT FROM 20",
            "quota_limit IS NOT DISTINCT FROM 40",
            "member_limit IS NOT DISTINCT FROM 50",
            "quota_limit IS NOT DISTINCT FROM 50",
            "name = 'Ampliado' AND member_limit IS NULL AND quota_limit IS NULL",
        ):
            self.assertIn(fragment, capacity)
        self.assertIn("member_limit > 0",
                      checks["ck_license_plans_member_limit_positive"])
        self.assertIn("quota_limit > 0",
                      checks["ck_license_plans_quota_limit_positive"])
        self.assertIn("member_limit IS NOT NULL AND quota_limit IS NOT NULL",
                      checks["ck_license_plans_capacity_pair_valid"])

    def test_price_types_computed_annual_and_validity(self):
        table = LicensePriceVersion.__table__
        columns = table.c
        self.assertEqual(
            set(columns.keys()),
            {"id", "created_at", "updated_at", "plan_id",
             "previous_price_version_id", "monthly_price",
             "annual_price_computed", "effective_from", "effective_to",
             "changed_by", "reason"},
        )
        for name in ("plan_id", "previous_price_version_id", "changed_by"):
            self.assertIsInstance(columns[name].type, PGUUID)
        self.assertFalse(columns.plan_id.nullable)
        self.assertTrue(columns.previous_price_version_id.nullable)
        self.assertFalse(columns.changed_by.nullable)
        for name in ("monthly_price", "annual_price_computed"):
            column = columns[name]
            self.assertIsInstance(column.type, Numeric)
            self.assertEqual((column.type.precision, column.type.scale),
                             (18, 2))
            self.assertTrue(column.type.asdecimal)
            self.assertFalse(column.nullable)
        computed = columns.annual_price_computed.computed
        self.assertIsInstance(computed, Computed)
        self.assertEqual(str(computed.sqltext), "monthly_price * 10")
        self.assertTrue(computed.persisted)
        for name in ("effective_from", "effective_to"):
            self.assertIsInstance(columns[name].type, DateTime)
            self.assertTrue(columns[name].type.timezone)
        self.assertFalse(columns.effective_from.nullable)
        self.assertTrue(columns.effective_to.nullable)
        self.assertFalse(columns.reason.nullable)
        checks = self.checks(table)
        self.assertEqual(checks["ck_license_price_versions_monthly_price_positive"],
                         "monthly_price > 0")
        self.assertEqual(checks["ck_license_price_versions_effective_interval_valid"],
                         "effective_to IS NULL OR effective_to > effective_from")
        self.assertEqual(checks["ck_license_price_versions_reason_nonblank"],
                         "reason ~ '[^[:space:]]'")

    def test_price_foreign_keys_and_version_chain(self):
        table = LicensePriceVersion.__table__
        self.assertEqual(
            self.uniques(table),
            {("plan_id", "id"), ("plan_id", "effective_from"),
             ("previous_price_version_id",)},
        )
        # plan_id belongs both to the plan FK and to the composite
        # previous-version FK. Collection iteration order selects neither.
        plan_fks = table.c.plan_id.foreign_keys
        self.assertCountEqual(
            [fk.target_fullname for fk in plan_fks],
            ["license_plans.id", "license_price_versions.plan_id"],
        )
        plan_fk, = (
            fk for fk in plan_fks
            if fk.target_fullname == "license_plans.id"
        )
        actor_fk, = table.c.changed_by.foreign_keys
        self.assertEqual(plan_fk.target_fullname, "license_plans.id")
        self.assertEqual(actor_fk.target_fullname, "user_identities.id")
        self.assertEqual(plan_fk.ondelete, "RESTRICT")
        self.assertEqual(actor_fk.ondelete, "RESTRICT")
        previous_fk = next(
            constraint for constraint in table.constraints
            if isinstance(constraint, ForeignKeyConstraint)
            and len(constraint.elements) == 2
        )
        self.assertEqual(
            tuple(element.parent.name for element in previous_fk.elements),
            ("plan_id", "previous_price_version_id"),
        )
        self.assertEqual(
            tuple(element.target_fullname for element in previous_fk.elements),
            ("license_price_versions.plan_id", "license_price_versions.id"),
        )
        self.assertEqual(previous_fk.ondelete, "RESTRICT")
        self.assertIn(
            "previous_price_version_id <> id",
            self.checks(table)["ck_license_price_versions_previous_version_distinct"],
        )

    def test_one_open_version_per_plan(self):
        indexes = LicensePriceVersion.__table__.indexes
        self.assertEqual(len(indexes), 1)
        index = next(iter(indexes))
        self.assertTrue(index.unique)
        self.assertEqual(tuple(column.name for column in index.columns),
                         ("plan_id",))
        self.assertEqual(
            str(CreateIndex(index).compile(dialect=dialect())),
            "CREATE UNIQUE INDEX uq_license_price_versions_open_plan "
            "ON license_price_versions (plan_id) WHERE effective_to IS NULL",
        )

    def test_postgresql_ddl_compiles_without_connection(self):
        plan_ddl = str(CreateTable(LicensePlan.__table__).compile(dialect=dialect()))
        price_ddl = str(CreateTable(LicensePriceVersion.__table__).compile(
            dialect=dialect()))
        for fragment in (
            "member_limit INTEGER",
            "quota_limit INTEGER",
            "status VARCHAR(32) DEFAULT 'INATIVO' NOT NULL",
            "name IN ('Essencial', 'Intermediário', 'Ampliado')",
            "name = 'Ampliado' AND member_limit IS NULL AND quota_limit IS NULL",
        ):
            self.assertIn(fragment, plan_ddl)
        for fragment in (
            "monthly_price NUMERIC(18, 2) NOT NULL",
            "annual_price_computed NUMERIC(18, 2) GENERATED ALWAYS AS "
            "(monthly_price * 10) STORED NOT NULL",
            "effective_from TIMESTAMP WITH TIME ZONE NOT NULL",
            "effective_to TIMESTAMP WITH TIME ZONE",
            "FOREIGN KEY(plan_id) REFERENCES license_plans (id) ON DELETE RESTRICT",
            "FOREIGN KEY(changed_by) REFERENCES user_identities (id) ON DELETE RESTRICT",
            "FOREIGN KEY(plan_id, previous_price_version_id) REFERENCES "
            "license_price_versions (plan_id, id) ON DELETE RESTRICT",
        ):
            self.assertIn(fragment, price_ddl)

    def test_approved_prices_use_exact_decimal_arithmetic(self):
        cases = (
            ("Essencial", Decimal("89.90"), Decimal("899.00")),
            ("Intermediário", Decimal("109.90"), Decimal("1099.00")),
            ("Ampliado", Decimal("129.90"), Decimal("1299.00")),
        )
        for name, monthly, annual in cases:
            with self.subTest(plan=name):
                self.assertEqual(monthly * Decimal(10), annual)
                self.assertEqual(annual.as_tuple().exponent, -2)


if __name__ == "__main__":
    unittest.main()
