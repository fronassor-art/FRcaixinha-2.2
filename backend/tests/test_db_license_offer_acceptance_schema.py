"""C11: vínculos de oferta/aceite, inspecionados sem conexão ao PostgreSQL."""

import unittest
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    LargeBinary,
    Numeric,
    SmallInteger,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import INET, UUID as PGUUID, dialect
from sqlalchemy.schema import CreateIndex, CreateTable

from app.db.models import (
    Base,
    LicenseOffer,
    LicensePlan,
    TermAcceptance,
    Tenant,
)


class LicenseOfferAcceptanceSchemaTests(unittest.TestCase):
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

    @staticmethod
    def foreign_keys(table):
        return {
            tuple(element.parent.name for element in constraint.elements):
            (
                tuple(element.target_fullname for element in constraint.elements),
                constraint.ondelete,
            )
            for constraint in table.constraints
            if isinstance(constraint, ForeignKeyConstraint)
        }

    def test_identity_timestamps_and_column_sets(self):
        cases = (
            (LicenseOffer, {
                "id", "created_at", "updated_at", "tenant_id",
                "contracting_party_id", "signer_user_id", "plan_id",
                "price_version_id", "contracting_party_name_snapshot",
                "plan_member_limit", "plan_quota_limit",
                "requested_member_count", "requested_quota_count",
                "period", "duration_months", "effective_price", "currency",
                "document_version", "document_ref", "document_hash", "issued_at", "expires_at",
                "status",
            }),
            (TermAcceptance, {
                "id", "created_at", "updated_at", "tenant_id", "cycle_id",
                "offer_id", "user_id", "price_version_id", "effective_price",
                "period", "duration_months", "document_version",
                "document_hash", "accepted_at", "ip_address", "evidence_ref",
                "scope",
            }),
        )
        for model, expected in cases:
            with self.subTest(model=model.__name__):
                table = model.__table__
                self.assertIn(table.name, Base.metadata.tables)
                self.assertEqual(set(table.c.keys()), expected)
                self.assertIsInstance(table.c.id.type, PGUUID)
                self.assertTrue(table.c.id.primary_key)
                self.assertTrue(callable(table.c.id.default.arg))
                for name in ("created_at", "updated_at"):
                    column = table.c[name]
                    self.assertIsInstance(column.type, DateTime)
                    self.assertTrue(column.type.timezone)
                    self.assertFalse(column.nullable)
                    self.assertIsNotNone(column.server_default)

    def test_offer_same_tenant_party_plan_capacity_and_price_version(self):
        self.assertIn(("id", "contracting_party_id"),
                      self.uniques(Tenant.__table__))
        plan_index = next(
            index for index in LicensePlan.__table__.indexes
            if index.name == "uq_license_plans_id_limits"
        )
        self.assertTrue(plan_index.unique)
        self.assertEqual(
            tuple(column.name for column in plan_index.columns),
            ("id", "member_limit", "quota_limit"),
        )
        fks = self.foreign_keys(LicenseOffer.__table__)
        self.assertEqual(
            fks[("tenant_id", "contracting_party_id")],
            (("tenants.id", "tenants.contracting_party_id"), "RESTRICT"),
        )
        self.assertEqual(
            fks[("plan_id", "plan_member_limit", "plan_quota_limit")],
            (("license_plans.id", "license_plans.member_limit",
              "license_plans.quota_limit"), "RESTRICT"),
        )
        self.assertEqual(
            fks[("plan_id", "price_version_id")],
            (("license_price_versions.plan_id",
              "license_price_versions.id"), "RESTRICT"),
        )
        self.assertEqual(
            fks[("signer_user_id",)],
            (("user_identities.id",), "RESTRICT"),
        )
        self.assertEqual(len(fks), 4)

    def test_offer_types_and_initial_inactive_state(self):
        columns = LicenseOffer.__table__.c
        for name in (
            "tenant_id", "contracting_party_id", "signer_user_id",
            "plan_id", "price_version_id",
        ):
            self.assertIsInstance(columns[name].type, PGUUID)
            self.assertFalse(columns[name].nullable)
        for name in (
            "plan_member_limit", "plan_quota_limit",
            "requested_member_count", "requested_quota_count",
        ):
            self.assertIsInstance(columns[name].type, Integer)
            self.assertFalse(columns[name].nullable)
        self.assertIsInstance(columns.duration_months.type, SmallInteger)
        self.assertIsInstance(columns.effective_price.type, Numeric)
        self.assertEqual(
            (columns.effective_price.type.precision,
             columns.effective_price.type.scale), (18, 2),
        )
        self.assertTrue(columns.effective_price.type.asdecimal)
        self.assertIsInstance(columns.document_hash.type, LargeBinary)
        for name in ("issued_at", "expires_at"):
            self.assertIsInstance(columns[name].type, DateTime)
            self.assertTrue(columns[name].type.timezone)
            self.assertFalse(columns[name].nullable)
        self.assertEqual(columns.status.default.arg, "RASCUNHO_INATIVO")
        self.assertEqual(str(columns.status.server_default.arg),
                         "'RASCUNHO_INATIVO'")
        self.assertEqual(str(columns.currency.server_default.arg), "'BRL'")

    def test_offer_structural_negative_guards(self):
        checks = self.checks(LicenseOffer.__table__)
        self.assertEqual(
            checks["ck_license_offers_requested_members_within_plan"],
            "requested_member_count > 0 AND requested_member_count <= plan_member_limit",
        )
        self.assertEqual(
            checks["ck_license_offers_requested_quotas_within_plan"],
            "requested_quota_count > 0 AND requested_quota_count <= plan_quota_limit",
        )
        self.assertEqual(
            checks["ck_license_offers_period_duration_valid"],
            "(period = 'MENSAL' AND duration_months = 1) OR "
            "(period = 'ANUAL' AND duration_months = 12)",
        )
        for name, expected in (
            ("plan_limits_positive", "plan_member_limit > 0 AND plan_quota_limit > 0"),
            ("effective_price_positive", "effective_price > 0"),
            ("currency_brl", "currency = 'BRL'"),
            ("finite_validity", "expires_at > issued_at"),
            ("document_ref_nonblank", "length(btrim(document_ref)) > 0"),
            ("status_initial_only", "status = 'RASCUNHO_INATIVO'"),
            ("document_hash_sha256_length",
             "octet_length(document_hash) = 32"),
        ):
            self.assertEqual(checks[f"ck_license_offers_{name}"], expected)
        self.assertIn(
            "contracting_party_name_snapshot ~ '[^[:space:]]'",
            checks["ck_license_offers_party_name_nonblank"],
        )
        self.assertIn(
            "document_version ~ '[^[:space:]]'",
            checks["ck_license_offers_document_version_nonblank"],
        )

    def test_acceptance_same_offer_signer_price_period_and_document(self):
        offer_key = (
            "id", "tenant_id", "signer_user_id", "price_version_id",
            "effective_price", "period", "duration_months",
            "document_version", "document_hash",
        )
        acceptance_key = (
            "offer_id", "tenant_id", "user_id", "price_version_id",
            "effective_price", "period", "duration_months",
            "document_version", "document_hash",
        )
        self.assertIn(offer_key, self.uniques(LicenseOffer.__table__))
        self.assertEqual(self.uniques(TermAcceptance.__table__),
                         {("offer_id",), ("id", "offer_id", "tenant_id", "price_version_id", "effective_price")})
        fks = self.foreign_keys(TermAcceptance.__table__)
        self.assertEqual(
            fks[acceptance_key],
            (tuple(f"license_offers.{name}" for name in offer_key), "RESTRICT"),
        )
        self.assertEqual(
            fks[("user_id",)],
            (("user_identities.id",), "RESTRICT"),
        )
        self.assertEqual(len(fks), 2)

    def test_acceptance_types_scope_cycle_and_evidence(self):
        columns = TermAcceptance.__table__.c
        for name in (
            "tenant_id", "offer_id", "user_id", "price_version_id",
        ):
            self.assertIsInstance(columns[name].type, PGUUID)
            self.assertFalse(columns[name].nullable)
        self.assertIsInstance(columns.cycle_id.type, PGUUID)
        self.assertTrue(columns.cycle_id.nullable)
        self.assertIsInstance(columns.effective_price.type, Numeric)
        self.assertEqual(
            (columns.effective_price.type.precision,
             columns.effective_price.type.scale), (18, 2),
        )
        self.assertTrue(columns.effective_price.type.asdecimal)
        self.assertIsInstance(columns.document_hash.type, LargeBinary)
        self.assertIsInstance(columns.accepted_at.type, DateTime)
        self.assertTrue(columns.accepted_at.type.timezone)
        self.assertFalse(columns.accepted_at.nullable)
        self.assertIsInstance(columns.ip_address.type, INET)
        self.assertFalse(columns.ip_address.nullable)
        self.assertEqual(columns.scope.default.arg, "LICENCA")
        checks = self.checks(TermAcceptance.__table__)
        for name, expected in (
            ("scope_initial_only", "scope = 'LICENCA'"),
            ("license_cycle_absent", "cycle_id IS NULL"),
            ("effective_price_positive", "effective_price > 0"),
            ("document_hash_sha256_length",
             "octet_length(document_hash) = 32"),
            ("evidence_ref_nonblank", "evidence_ref ~ '[^[:space:]]'"),
        ):
            self.assertEqual(checks[f"ck_term_acceptances_{name}"], expected)

    def test_tenant_first_indexes_and_postgresql_ddl(self):
        offer_indexes = {
            index.name: index for index in LicenseOffer.__table__.indexes
        }
        self.assertEqual(
            {name: tuple(column.name for column in index.columns)
             for name, index in offer_indexes.items()},
            {
                "ix_license_offers_tenant_party":
                    ("tenant_id", "contracting_party_id"),
                "ix_license_offers_tenant_plan": ("tenant_id", "plan_id"),
            },
        )
        acceptance_index = next(iter(TermAcceptance.__table__.indexes))
        self.assertEqual(
            tuple(column.name for column in acceptance_index.columns),
            ("tenant_id", "offer_id"),
        )
        self.assertIn(
            "CREATE UNIQUE INDEX uq_license_plans_id_limits",
            str(CreateIndex(next(iter(LicensePlan.__table__.indexes))).compile(
                dialect=dialect())),
        )
        for model, fragments in (
            (LicenseOffer, (
                "effective_price NUMERIC(18, 2) NOT NULL",
                "duration_months SMALLINT NOT NULL",
                "document_hash BYTEA NOT NULL",
                "issued_at TIMESTAMP WITH TIME ZONE NOT NULL",
                "expires_at TIMESTAMP WITH TIME ZONE NOT NULL",
                "FOREIGN KEY(tenant_id, contracting_party_id)",
                "FOREIGN KEY(plan_id, plan_member_limit, plan_quota_limit)",
                "FOREIGN KEY(plan_id, price_version_id)",
            )),
            (TermAcceptance, (
                "effective_price NUMERIC(18, 2) NOT NULL",
                "accepted_at TIMESTAMP WITH TIME ZONE NOT NULL",
                "ip_address INET NOT NULL",
                "cycle_id UUID",
                "FOREIGN KEY(offer_id, tenant_id, user_id, price_version_id, "
                "effective_price, period, duration_months, document_version, "
                "document_hash)",
            )),
        ):
            ddl = str(CreateTable(model.__table__).compile(dialect=dialect()))
            for fragment in fragments:
                with self.subTest(model=model.__name__, fragment=fragment):
                    self.assertIn(fragment, ddl)

    def test_decimal_money_is_exact_in_schema_not_postgresql_execution(self):
        for amount in (Decimal("89.90"), Decimal("109.90"),
                       Decimal("129.90")):
            with self.subTest(amount=amount):
                self.assertEqual(amount.as_tuple().exponent, -2)
                self.assertNotIsInstance(amount, float)


if __name__ == "__main__":
    unittest.main()
