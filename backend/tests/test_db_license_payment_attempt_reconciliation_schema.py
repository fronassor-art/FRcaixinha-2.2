"""C13-R1: garantias de DDL, sem conexao, INSERT ou conciliacao real.

As matrizes de casos ilustram as chaves e CHECKs declarados. Somente ensaios
futuros em PostgreSQL podem provar insercao, concorrencia, replay, imutabilidade
e a conciliacao de uma observacao externa.
"""

from decimal import Decimal
import re
import unittest
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    LargeBinary,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, dialect
from sqlalchemy.schema import CreateIndex, CreateTable

from app.db.models import (
    Base,
    Payment,
    PaymentAttempt,
    PaymentReconciliationEvent,
)


class PaymentAttemptReconciliationSchemaTests(unittest.TestCase):
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

    def test_exact_tables_identity_and_timestamps(self):
        cases = (
            (PaymentAttempt, {
                "id", "created_at", "updated_at", "tenant_id", "payment_id",
                "attempt_number", "expected_amount", "environment",
                "idempotency_key", "provider", "charge_ref", "receiver_ref",
                "status",
            }),
            (PaymentReconciliationEvent, {
                "id", "created_at", "updated_at", "tenant_id", "payment_id",
                "attempt_id", "environment", "observation_source", "provider",
                "event_key", "provider_status", "observed_amount",
                "observed_currency", "observed_receiver_ref", "observed_at",
                "evidence_ref", "evidence_hash", "status",
            }),
        )
        for model, names in cases:
            with self.subTest(model=model.__name__):
                table = model.__table__
                self.assertIn(table.name, Base.metadata.tables)
                self.assertEqual(set(table.c.keys()), names)
                self.assertIsInstance(table.c.id.type, PGUUID)
                self.assertTrue(table.c.id.type.as_uuid)
                self.assertTrue(table.c.id.primary_key)
                self.assertTrue(callable(table.c.id.default.arg))
                for name in ("created_at", "updated_at"):
                    column = table.c[name]
                    self.assertIsInstance(column.type, DateTime)
                    self.assertTrue(column.type.timezone)
                    self.assertFalse(column.nullable)
                    self.assertIsNotNone(column.server_default)
                self.assertIsNotNone(table.c.updated_at.onupdate)

    def test_environment_domain_matches_approved_contract(self):
        approved = ("DEMO", "HOMOLOGACAO", "PRODUCAO")
        for model in (Payment, PaymentAttempt, PaymentReconciliationEvent):
            with self.subTest(model=model.__name__):
                check = self.checks(model.__table__)[
                    f"ck_{model.__tablename__}_environment_valid"
                ]
                values = tuple(re.findall(r"'([^']*)'", check))
                self.assertEqual(values, approved)
                self.assertFalse(model.__table__.c.environment.nullable)
                for environment in (*approved, "SANDBOX", "TEST", "", "OUTRO"):
                    with self.subTest(environment=environment):
                        self.assertEqual(
                            environment in values, environment in approved
                        )

    def test_payment_changes_only_by_parent_composite_key(self):
        self.assertIn(
            ("id", "tenant_id", "expected_amount", "environment"),
            self.uniques(Payment.__table__),
        )
        self.assertEqual(
            self.foreign_keys(PaymentAttempt.__table__),
            {("payment_id", "tenant_id", "expected_amount", "environment"): (
                ("payments.id", "payments.tenant_id",
                 "payments.expected_amount", "payments.environment"),
                "RESTRICT",
            )},
        )
        self.assertEqual(
            self.uniques(PaymentAttempt.__table__),
            {
                ("payment_id", "attempt_number"),
                ("idempotency_key",),
                ("id", "payment_id", "tenant_id", "environment"),
            },
        )

    def test_attempt_required_fields_money_and_initial_state(self):
        columns = PaymentAttempt.__table__.c
        for name in ("tenant_id", "payment_id", "idempotency_key"):
            self.assertIsInstance(columns[name].type, PGUUID)
            self.assertFalse(columns[name].nullable)
        self.assertIsNone(columns.idempotency_key.default)
        self.assertIsInstance(columns.attempt_number.type, Integer)
        for name in ("attempt_number", "environment", "status"):
            self.assertFalse(columns[name].nullable)
        self.assertIsInstance(columns.expected_amount.type, Numeric)
        self.assertEqual(
            (columns.expected_amount.type.precision,
             columns.expected_amount.type.scale),
            (18, 2),
        )
        self.assertTrue(columns.expected_amount.type.asdecimal)
        self.assertFalse(columns.expected_amount.nullable)
        self.assertEqual(columns.status.default.arg, "NAO_INICIADA_INATIVA")
        self.assertEqual(
            str(columns.status.server_default.arg), "'NAO_INICIADA_INATIVA'"
        )
        for name in ("provider", "charge_ref", "receiver_ref"):
            self.assertTrue(columns[name].nullable)
        self.assertEqual(
            self.checks(PaymentAttempt.__table__),
            {
                "ck_payment_attempts_attempt_number_positive":
                    "attempt_number > 0",
                "ck_payment_attempts_environment_valid":
                    "environment IN ('DEMO', 'HOMOLOGACAO', 'PRODUCAO')",
                "ck_payment_attempts_status_initial_only":
                    "status = 'NAO_INICIADA_INATIVA'",
                "ck_payment_attempts_initial_external_fields_absent":
                    "provider IS NULL AND charge_ref IS NULL AND receiver_ref IS NULL",
            },
        )
        for number in (-1, 0, 1, 2):
            with self.subTest(number=number):
                self.assertEqual(number > 0, number in (1, 2))
        for field in ("provider", "charge_ref", "receiver_ref"):
            with self.subTest(external_field=field):
                self.assertIn(f"{field} IS NULL",
                              self.checks(PaymentAttempt.__table__)[
                                  "ck_payment_attempts_initial_external_fields_absent"
                              ])

    def test_event_composite_link_rejects_cross_scope_at_ddl_level(self):
        self.assertEqual(
            self.foreign_keys(PaymentReconciliationEvent.__table__),
            {("attempt_id", "payment_id", "tenant_id", "environment"): (
                (
                    "payment_attempts.id", "payment_attempts.payment_id",
                    "payment_attempts.tenant_id",
                    "payment_attempts.environment",
                ),
                "RESTRICT",
            )},
        )
        attempt_id, payment_id, tenant_id = uuid4(), uuid4(), uuid4()
        parent = (attempt_id, payment_id, tenant_id, "DEMO")
        cases = (
            (parent, True),
            ((uuid4(), payment_id, tenant_id, "DEMO"), False),
            ((attempt_id, uuid4(), tenant_id, "DEMO"), False),
            ((attempt_id, payment_id, uuid4(), "DEMO"), False),
            ((attempt_id, payment_id, tenant_id, "HOMOLOGACAO"), False),
            ((attempt_id, payment_id, tenant_id, "PRODUCAO"), False),
        )
        for child, matches in cases:
            with self.subTest(child=child):
                self.assertEqual(child == parent, matches)
        # O FK anterior e os NOT NULL sao a garantia; a matriz nao executa SQL.
        for name in ("attempt_id", "payment_id", "tenant_id", "environment"):
            self.assertFalse(PaymentReconciliationEvent.__table__.c[name].nullable)

    def test_attempt_payment_link_rejects_cross_scope_at_ddl_level(self):
        self.assertEqual(
            self.foreign_keys(PaymentAttempt.__table__),
            {("payment_id", "tenant_id", "expected_amount", "environment"): (
                ("payments.id", "payments.tenant_id",
                 "payments.expected_amount", "payments.environment"),
                "RESTRICT",
            )},
        )
        payment_id, tenant_id = uuid4(), uuid4()
        amount = Decimal("49.90")
        approved = ("DEMO", "HOMOLOGACAO", "PRODUCAO")
        for environment in approved:
            parent = (payment_id, tenant_id, amount, environment)
            cases = (
                (parent, True),
                ((uuid4(), tenant_id, amount, environment), False),
                ((payment_id, uuid4(), amount, environment), False),
                ((payment_id, tenant_id, Decimal("49.91"), environment), False),
            ) + tuple(
                ((payment_id, tenant_id, amount, other), False)
                for other in approved if other != environment
            )
            for child, matches in cases:
                with self.subTest(parent=parent, child=child):
                    self.assertEqual(child == parent, matches)
        # A FK composta e os NOT NULL sao a garantia DDL; nao ha INSERT aqui.
        for name in ("payment_id", "tenant_id", "expected_amount", "environment"):
            self.assertFalse(PaymentAttempt.__table__.c[name].nullable)

    def test_attempt_number_key_and_event_deduplication_scopes(self):
        number_key = ("payment_id", "attempt_number")
        self.assertIn(number_key, self.uniques(PaymentAttempt.__table__))
        self.assertIn(
            ("idempotency_key",), self.uniques(PaymentAttempt.__table__)
        )
        dedup = ("provider", "environment", "observation_source", "event_key")
        self.assertEqual(
            self.uniques(PaymentReconciliationEvent.__table__), {dedup}
        )
        for name in dedup:
            with self.subTest(name=name):
                self.assertFalse(PaymentReconciliationEvent.__table__.c[name].nullable)
        scope = ("prov", "DEMO", "WEBHOOK", "event-1")
        self.assertEqual(scope, tuple(scope))
        for changed in (
            ("other", *scope[1:]),
            (scope[0], "HOMOLOGACAO", *scope[2:]),
            (scope[0], "PRODUCAO", *scope[2:]),
            (*scope[:2], "CONSULTA", scope[3]),
            (*scope[:3], "event-2"),
        ):
            self.assertNotEqual(scope, changed)

    def test_event_observation_is_evidence_not_payment_confirmation(self):
        columns = PaymentReconciliationEvent.__table__.c
        for name in ("tenant_id", "payment_id", "attempt_id"):
            self.assertIsInstance(columns[name].type, PGUUID)
        self.assertIsInstance(columns.observed_amount.type, Numeric)
        self.assertEqual(
            (columns.observed_amount.type.precision,
             columns.observed_amount.type.scale),
            (18, 2),
        )
        self.assertTrue(columns.observed_amount.nullable)
        for name in ("observed_currency", "observed_receiver_ref", "observed_at"):
            self.assertTrue(columns[name].nullable)
        self.assertTrue(columns.observed_at.type.timezone)
        self.assertFalse(columns.evidence_ref.nullable)
        self.assertIsInstance(columns.evidence_hash.type, LargeBinary)
        self.assertFalse(columns.evidence_hash.nullable)
        self.assertFalse(columns.provider_status.nullable)
        self.assertEqual(columns.status.default.arg, "REGISTRADO_NAO_CONCILIADO")
        self.assertEqual(
            str(columns.status.server_default.arg),
            "'REGISTRADO_NAO_CONCILIADO'",
        )
        self.assertNotIn("confirmed_amount", columns)
        self.assertNotIn("confirmed_at", columns)
        self.assertNotIn("payload", columns)
        self.assertNotIn("token", columns)
        self.assertNotIn("credential", columns)
        # Valores divergentes sao colunas proprias, sem CHECK de igualdade
        # com Payment e sem FK que os inclua.
        fk_columns = next(iter(self.foreign_keys(
            PaymentReconciliationEvent.__table__
        )))
        self.assertTrue({
            "observed_amount", "observed_currency", "observed_receiver_ref"
        }.isdisjoint(fk_columns))
        self.assertEqual(
            self.checks(PaymentReconciliationEvent.__table__)[
                "ck_payment_reconciliation_events_status_initial_only"
            ],
            "status = 'REGISTRADO_NAO_CONCILIADO'",
        )

    def test_event_nonblank_refs_hash_and_status_checks(self):
        checks = self.checks(PaymentReconciliationEvent.__table__)
        expected = {
            "environment_valid": "environment IN ('DEMO', 'HOMOLOGACAO', 'PRODUCAO')",
            "provider_nonblank": "provider ~ '[^[:space:]]'",
            "observation_source_nonblank":
                "observation_source ~ '[^[:space:]]'",
            "event_key_nonblank": "event_key ~ '[^[:space:]]'",
            "provider_status_nonblank": "provider_status ~ '[^[:space:]]'",
            "observed_currency_nonblank":
                "observed_currency IS NULL OR observed_currency ~ '[^[:space:]]'",
            "observed_receiver_ref_nonblank":
                "observed_receiver_ref IS NULL OR "
                "observed_receiver_ref ~ '[^[:space:]]'",
            "evidence_ref_nonblank": "evidence_ref ~ '[^[:space:]]'",
            "evidence_hash_sha256_length":
                "octet_length(evidence_hash) = 32",
            "status_initial_only": "status = 'REGISTRADO_NAO_CONCILIADO'",
        }
        self.assertEqual(
            checks,
            {
                f"ck_payment_reconciliation_events_{name}": value
                for name, value in expected.items()
            },
        )
        for value in ("", " ", "\t\n", "evidence-1"):
            with self.subTest(value=value):
                self.assertEqual(
                    bool(re.search(r"\S", value)), value == "evidence-1"
                )

    def test_tenant_first_indexes_and_postgresql_ddl(self):
        attempt_indexes = {
            index.name: index for index in PaymentAttempt.__table__.indexes
        }
        event_indexes = {
            index.name: index
            for index in PaymentReconciliationEvent.__table__.indexes
        }
        self.assertEqual(
            {name: tuple(column.name for column in index.columns)
             for name, index in attempt_indexes.items()},
            {"ix_payment_attempts_tenant_payment_number":
             ("tenant_id", "payment_id", "attempt_number")},
        )
        self.assertEqual(
            {name: tuple(column.name for column in index.columns)
             for name, index in event_indexes.items()},
            {"ix_payment_reconciliation_events_tenant_payment_attempt":
             ("tenant_id", "payment_id", "attempt_id")},
        )
        for index in (*attempt_indexes.values(), *event_indexes.values()):
            sql = str(CreateIndex(index).compile(dialect=dialect()))
            self.assertIn("ON " + index.table.name + " (tenant_id", sql)

        cases = (
            (Payment, (
                "environment VARCHAR(16) NOT NULL",
                "UNIQUE (id, tenant_id, expected_amount, environment)",
                "environment IN ('DEMO', 'HOMOLOGACAO', 'PRODUCAO')",
            )),
            (PaymentAttempt, (
                "expected_amount NUMERIC(18, 2) NOT NULL",
                "idempotency_key UUID NOT NULL",
                "status VARCHAR(32) DEFAULT 'NAO_INICIADA_INATIVA' NOT NULL",
                "FOREIGN KEY(payment_id, tenant_id, expected_amount, environment)",
                "REFERENCES payments (id, tenant_id, expected_amount, "
                "environment) "
                "ON DELETE RESTRICT",
                "UNIQUE (payment_id, attempt_number)",
            )),
            (PaymentReconciliationEvent, (
                "observed_amount NUMERIC(18, 2)",
                "observed_at TIMESTAMP WITH TIME ZONE",
                "evidence_hash BYTEA NOT NULL",
                "status VARCHAR(32) DEFAULT 'REGISTRADO_NAO_CONCILIADO' NOT NULL",
                "FOREIGN KEY(attempt_id, payment_id, tenant_id, environment)",
                "REFERENCES payment_attempts (id, payment_id, tenant_id, "
                "environment) ON DELETE RESTRICT",
                "UNIQUE (provider, environment, observation_source, event_key)",
            )),
        )
        for model, fragments in cases:
            ddl = str(CreateTable(model.__table__).compile(dialect=dialect()))
            for fragment in fragments:
                with self.subTest(model=model.__name__, fragment=fragment):
                    self.assertIn(fragment, ddl)


if __name__ == "__main__":
    unittest.main()
