"""Paridade offline ORM/Alembic da minuta P4; nenhuma tabela foi criada.

A comparacao textual compila PostgreSQL em memoria. Nao testa INSERT,
concorrencia, rollback real, alteracao de alembic_version ou restauracao PG.
"""

import io
import re
import unittest
from unittest.mock import patch

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.schema import CreateIndex, CreateTable

from app.db.models import (
    Base, EmailConfirmationChallenge, IdentityCredential,
    IdentitySession, RegistrationIdempotency,
)
from migrations.versions import f2p4_20261022_auth_bootstrap_draft as revision


TABLE_NAMES = (
    "identity_credentials",
    "email_confirmation_challenges",
    "registration_idempotency",
    "identity_sessions",
)


class AuthBootstrapOrmParityTests(unittest.TestCase):
    @staticmethod
    def render_upgrade():
        out = io.StringIO()
        ctx = MigrationContext.configure(
            dialect_name="postgresql",
            opts={"as_sql": True, "output_buffer": out},
        )
        with patch.object(revision, "op", Operations(ctx)):
            revision.upgrade()
        return out.getvalue()

    @staticmethod
    def table_parts(sql):
        """Preserva cada coluna/constraint; ignora ordem e whitespace apenas."""
        chunk = sql[sql.index("(\n") + 2: sql.rindex("\n)")]
        return {
            re.sub(r"\s+", " ", line.strip().rstrip(",")).replace("%%", "%")
            for line in chunk.splitlines() if line.strip()
        }

    @staticmethod
    def normalize_ddl(ddl):
        return re.sub(r"\s+", " ", ddl.strip().rstrip(";")).replace("%%", "%")

    def test_exact_new_models_and_existing_schema_remain_disjoint(self):
        expected = {
            "identity_credentials": IdentityCredential,
            "email_confirmation_challenges": EmailConfirmationChallenge,
            "registration_idempotency": RegistrationIdempotency,
            "identity_sessions": IdentitySession,
        }
        self.assertEqual(revision._TABLE_ORDER, TABLE_NAMES)
        self.assertEqual(len(Base.metadata.tables), 21)
        self.assertEqual(
            set(TABLE_NAMES), set(Base.metadata.tables) -
            {
                "license_plans", "user_identities", "contracting_parties",
                "license_price_versions", "tenants", "cycles", "license_offers",
                "role_grants", "memberships", "term_acceptances",
                "license_payment_obligations", "quotas", "payments",
                "payment_attempts", "payment_reconciliation_events",
                "license_subscriptions", "license_entitlement_segments",
            },
        )
        for name, model in expected.items():
            with self.subTest(name=name):
                self.assertIs(model.__table__, Base.metadata.tables[name])

    def test_all_four_create_table_fragments_match_orm(self):
        sql = self.render_upgrade()
        pg = dialect()
        self.assertEqual(sql.count("CREATE TABLE "), 4)
        for name in TABLE_NAMES:
            with self.subTest(name=name):
                match = re.search(
                    rf"CREATE TABLE {name} \(\n.*?\n\);",
                    sql, re.DOTALL,
                )
                self.assertIsNotNone(match)
                actual = self.table_parts(match.group())
                mapped = self.table_parts(
                    str(CreateTable(Base.metadata.tables[name]).compile(
                        dialect=pg,
                    ))
                )
                self.assertEqual(actual, mapped)

    def test_all_three_create_index_fragments_match_orm(self):
        sql = self.render_upgrade()
        pg = dialect()
        indexes = [
            index for name in TABLE_NAMES
            for index in Base.metadata.tables[name].indexes
        ]
        self.assertEqual(len(indexes), 3)
        self.assertEqual(sql.count("CREATE INDEX "), 3)
        for index in indexes:
            with self.subTest(index=index.name):
                expected = self.normalize_ddl(str(CreateIndex(index).compile(
                    dialect=pg,
                )))
                self.assertIn(expected, self.normalize_ddl(sql))

    def test_only_digest_and_verifier_fields_not_raw_secrets(self):
        for name in TABLE_NAMES:
            with self.subTest(name=name):
                columns = Base.metadata.tables[name].c
                for forbidden in (
                    "password", "token", "delivery_secret", "cpf", "cnpj",
                    "raw_email", "key_material",
                ):
                    self.assertNotIn(forbidden, columns)
        self.assertIn(
            "password_digest", Base.metadata.tables["identity_credentials"].c,
        )
        self.assertIn(
            "verifier_sha256",
            Base.metadata.tables["email_confirmation_challenges"].c,
        )
        self.assertIn(
            "verifier_sha256", Base.metadata.tables["identity_sessions"].c,
        )

    def test_compilation_never_connects_to_pg(self):
        with patch("psycopg.connect") as connect:
            sql = self.render_upgrade()
            for name in TABLE_NAMES:
                str(CreateTable(Base.metadata.tables[name]).compile(
                    dialect=dialect(),
                ))
        connect.assert_not_called()
        self.assertNotIn("INSERT INTO", sql)
        self.assertNotIn("CASCADE", sql)


if __name__ == "__main__":
    unittest.main()
