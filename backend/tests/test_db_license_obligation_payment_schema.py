"""C12: inspeções do esquema PostgreSQL, sem inserts nem conexão."""

import unittest

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, dialect
from sqlalchemy.schema import CreateIndex, CreateTable

from app.db.models import (
    Base,
    LicensePaymentObligation,
    Payment,
    TermAcceptance,
)


class LicenseObligationPaymentSchemaTests(unittest.TestCase):
    @staticmethod
    def uniques(table):
        return {
            tuple(column.name for column in constraint.columns)
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        }

    @staticmethod
    def checks(table):
        return {
            constraint.name: str(constraint.sqltext)
            for constraint in table.constraints
            if isinstance(constraint, CheckConstraint)
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

    def test_identity_timestamps_and_exact_columns(self):
        cases = (
            (LicensePaymentObligation, {
                "id", "created_at", "updated_at", "tenant_id", "cycle_id",
                "offer_id", "term_acceptance_id", "price_version_id",
                "expected_amount", "currency", "purpose", "status",
            }),
            (Payment, {
                "id", "created_at", "updated_at", "tenant_id", "cycle_id",
                "obligation_id", "offer_id", "price_version_id",
                "expected_amount", "environment", "confirmed_amount",
                "currency", "purpose", "receiver_domain", "idempotency_key", "provider", "external_id",
                "receiver_ref", "confirmed_at", "evidence_ref", "status",
            }),
        )
        for model, expected in cases:
            with self.subTest(model=model.__name__):
                table = model.__table__
                self.assertIn(table.name, Base.metadata.tables)
                self.assertEqual(set(table.c.keys()), expected)
                self.assertNotIn("contracting_party_id", table.c)
                self.assertIsInstance(table.c.id.type, PGUUID)
                self.assertTrue(table.c.id.primary_key)
                self.assertTrue(callable(table.c.id.default.arg))
                for name in ("created_at", "updated_at"):
                    column = table.c[name]
                    self.assertIsInstance(column.type, DateTime)
                    self.assertTrue(column.type.timezone)
                    self.assertFalse(column.nullable)
                    self.assertIsNotNone(column.server_default)

    def test_obligation_links_exact_accepted_offer_version_and_amount(self):
        acceptance_key = (
            "id", "offer_id", "tenant_id", "price_version_id",
            "effective_price",
        )
        obligation_key = (
            "term_acceptance_id", "offer_id", "tenant_id",
            "price_version_id", "expected_amount",
        )
        self.assertIn(acceptance_key, self.uniques(TermAcceptance.__table__))
        self.assertEqual(
            self.foreign_keys(LicensePaymentObligation.__table__),
            {obligation_key:
             (tuple(f"term_acceptances.{name}" for name in acceptance_key),
              "RESTRICT")},
        )
        self.assertEqual(
            self.uniques(LicensePaymentObligation.__table__),
            {
                ("offer_id",), ("term_acceptance_id",),
                ("id", "tenant_id", "offer_id", "price_version_id",
                 "expected_amount"),
            },
        )

    def test_obligation_money_purpose_and_initial_state(self):
        columns = LicensePaymentObligation.__table__.c
        for name in (
            "tenant_id", "offer_id", "term_acceptance_id",
            "price_version_id",
        ):
            self.assertIsInstance(columns[name].type, PGUUID)
            self.assertFalse(columns[name].nullable)
        self.assertIsInstance(columns.cycle_id.type, PGUUID)
        self.assertTrue(columns.cycle_id.nullable)
        self.assertIsInstance(columns.expected_amount.type, Numeric)
        self.assertEqual(
            (columns.expected_amount.type.precision,
             columns.expected_amount.type.scale), (18, 2),
        )
        self.assertTrue(columns.expected_amount.type.asdecimal)
        self.assertFalse(columns.expected_amount.nullable)
        self.assertEqual(columns.status.default.arg, "RASCUNHO_INATIVO")
        checks = self.checks(LicensePaymentObligation.__table__)
        for name, expected in (
            ("license_cycle_absent", "cycle_id IS NULL"),
            ("expected_amount_positive", "expected_amount > 0"),
            ("currency_brl", "currency = 'BRL'"),
            ("purpose_license", "purpose = 'LICENCA'"),
            ("status_initial_only", "status = 'RASCUNHO_INATIVO'"),
        ):
            self.assertEqual(
                checks[f"ck_license_payment_obligations_{name}"], expected
            )
        self.assertEqual(str(columns.currency.server_default.arg), "'BRL'")
        self.assertEqual(str(columns.purpose.server_default.arg), "'LICENCA'")

    def test_payment_matches_one_obligation_and_has_stable_idempotency(self):
        obligation_key = (
            "id", "tenant_id", "offer_id", "price_version_id",
            "expected_amount",
        )
        payment_key = (
            "obligation_id", "tenant_id", "offer_id", "price_version_id",
            "expected_amount",
        )
        self.assertEqual(
            self.foreign_keys(Payment.__table__),
            {payment_key:
             (tuple(f"license_payment_obligations.{name}"
                    for name in obligation_key), "RESTRICT")},
        )
        self.assertEqual(
            self.uniques(Payment.__table__),
            {("obligation_id",), ("idempotency_key",),
             ("id", "tenant_id", "expected_amount", "environment")},
        )
        columns = Payment.__table__.c
        self.assertIsInstance(columns.idempotency_key.type, PGUUID)
        self.assertFalse(columns.idempotency_key.nullable)
        self.assertIsNone(columns.idempotency_key.default)
        for name in payment_key:
            self.assertFalse(columns[name].nullable)

    def test_payment_money_and_provider_fields_are_inactive(self):
        columns = Payment.__table__.c
        for name in ("expected_amount", "confirmed_amount"):
            column = columns[name]
            self.assertIsInstance(column.type, Numeric)
            self.assertEqual(
                (column.type.precision, column.type.scale), (18, 2)
            )
            self.assertTrue(column.type.asdecimal)
        self.assertFalse(columns.expected_amount.nullable)
        self.assertIsInstance(columns.environment.type, String)
        self.assertEqual(columns.environment.type.length, 16)
        self.assertFalse(columns.environment.nullable)
        self.assertIsNone(columns.environment.default)
        self.assertIsNone(columns.environment.server_default)
        self.assertTrue(columns.confirmed_amount.nullable)
        for name in (
            "provider", "external_id", "receiver_ref", "confirmed_at",
            "evidence_ref",
        ):
            self.assertTrue(columns[name].nullable)
        self.assertIsInstance(columns.confirmed_at.type, DateTime)
        self.assertTrue(columns.confirmed_at.type.timezone)
        self.assertEqual(
            columns.status.default.arg, "NAO_INICIADO_INATIVO"
        )
        self.assertEqual(
            str(columns.status.server_default.arg),
            "'NAO_INICIADO_INATIVO'",
        )
        checks = self.checks(Payment.__table__)
        for name, expected in (
            ("license_cycle_absent", "cycle_id IS NULL"),
            ("expected_amount_positive", "expected_amount > 0"),
            ("environment_valid",
             "environment IN ('DEMO', 'HOMOLOGACAO', 'PRODUCAO')"),
            ("confirmed_amount_nonnegative",
             "confirmed_amount IS NULL OR confirmed_amount >= 0"),
            ("currency_brl", "currency = 'BRL'"),
            ("purpose_license", "purpose = 'LICENCA'"),
            ("receiver_domain_platform",
             "receiver_domain = 'PLATAFORMA'"),
            ("status_initial_only",
             "status = 'NAO_INICIADO_INATIVO'"),
            ("provider_external_pair",
             "(provider IS NULL AND external_id IS NULL) OR "
             "(provider IS NOT NULL AND external_id IS NOT NULL)"),
            ("external_receiver_required",
             "external_id IS NULL OR receiver_ref IS NOT NULL"),
            ("initial_financial_fields_absent",
             "confirmed_amount IS NULL AND provider IS NULL "
             "AND external_id IS NULL AND receiver_ref IS NULL "
             "AND confirmed_at IS NULL AND evidence_ref IS NULL"),
        ):
            self.assertEqual(checks[f"ck_payments_{name}"], expected)
        self.assertEqual(
            str(columns.receiver_domain.server_default.arg), "'PLATAFORMA'"
        )

    def test_tenant_first_indexes_and_external_id_scope(self):
        obligation_indexes = {
            index.name: index
            for index in LicensePaymentObligation.__table__.indexes
        }
        self.assertEqual(
            {name: tuple(column.name for column in index.columns)
             for name, index in obligation_indexes.items()},
            {"ix_license_payment_obligations_tenant_offer":
             ("tenant_id", "offer_id")},
        )
        indexes = {index.name: index for index in Payment.__table__.indexes}
        self.assertEqual(
            {name: tuple(column.name for column in index.columns)
             for name, index in indexes.items()},
            {
                "ix_payments_tenant_obligation":
                    ("tenant_id", "obligation_id"),
                "ix_payments_tenant_offer": ("tenant_id", "offer_id"),
                "uq_payments_provider_receiver_external":
                    ("provider", "receiver_ref", "external_id"),
            },
        )
        external = indexes["uq_payments_provider_receiver_external"]
        self.assertTrue(external.unique)
        self.assertEqual(
            str(CreateIndex(external).compile(dialect=dialect())),
            "CREATE UNIQUE INDEX uq_payments_provider_receiver_external "
            "ON payments (provider, receiver_ref, external_id) "
            "WHERE external_id IS NOT NULL",
        )

    def test_postgresql_ddl_compiles_without_connection(self):
        cases = (
            (LicensePaymentObligation, (
                "expected_amount NUMERIC(18, 2) NOT NULL",
                "cycle_id UUID",
                "status VARCHAR(32) DEFAULT 'RASCUNHO_INATIVO' NOT NULL",
                "FOREIGN KEY(term_acceptance_id, offer_id, tenant_id, "
                "price_version_id, expected_amount)",
                "REFERENCES term_acceptances (id, offer_id, tenant_id, "
                "price_version_id, effective_price) ON DELETE RESTRICT",
            )),
            (Payment, (
                "expected_amount NUMERIC(18, 2) NOT NULL",
                "environment VARCHAR(16) NOT NULL",
                "confirmed_amount NUMERIC(18, 2)",
                "UNIQUE (id, tenant_id, expected_amount, environment)",
                "environment IN ('DEMO', 'HOMOLOGACAO', 'PRODUCAO')",
                "idempotency_key UUID NOT NULL",
                "confirmed_at TIMESTAMP WITH TIME ZONE",
                "status VARCHAR(32) DEFAULT 'NAO_INICIADO_INATIVO' NOT NULL",
                "FOREIGN KEY(obligation_id, tenant_id, offer_id, "
                "price_version_id, expected_amount)",
                "REFERENCES license_payment_obligations (id, tenant_id, "
                "offer_id, price_version_id, expected_amount) "
                "ON DELETE RESTRICT",
            )),
        )
        for model, fragments in cases:
            ddl = str(CreateTable(model.__table__).compile(dialect=dialect()))
            for fragment in fragments:
                with self.subTest(model=model.__name__, fragment=fragment):
                    self.assertIn(fragment, ddl)


if __name__ == "__main__":
    unittest.main()
