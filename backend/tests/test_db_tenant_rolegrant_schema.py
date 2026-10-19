"""Verificacoes estruturais de Tenant e RoleGrant sem conexao a banco."""

import re
import unittest
from datetime import datetime, timedelta, timezone

from sqlalchemy import CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.schema import CreateIndex, CreateTable

from app.db.models import Base, RoleGrant, Tenant


class TenantRoleGrantSchemaTests(unittest.TestCase):
    @staticmethod
    def checks(table):
        return {
            constraint.name: str(constraint.sqltext)
            for constraint in table.constraints
            if isinstance(constraint, CheckConstraint)
        }

    def test_tables_uuid_and_timestamps(self):
        self.assertEqual(
            set(Base.metadata.tables),
            {"user_identities", "contracting_parties", "tenants", "cycles", "role_grants", "memberships", "quotas", "license_plans", "license_price_versions", "license_offers", "term_acceptances", "license_payment_obligations", "payments"},
        )
        for entity in (Tenant, RoleGrant):
            with self.subTest(entity=entity.__name__):
                columns = entity.__table__.c
                self.assertTrue(columns.id.primary_key)
                self.assertIsInstance(columns.id.type, PGUUID)
                self.assertTrue(columns.id.type.as_uuid)
                for name in ("created_at", "updated_at"):
                    self.assertFalse(columns[name].nullable)
                    self.assertIsInstance(columns[name].type, DateTime)
                    self.assertTrue(columns[name].type.timezone)

    def test_tenant_foreign_keys_and_required_fields(self):
        columns = Tenant.__table__.c
        for name, target in (
            ("admin_user_id", "user_identities.id"),
            ("contracting_party_id", "contracting_parties.id"),
        ):
            with self.subTest(column=name):
                self.assertFalse(columns[name].nullable)
                self.assertEqual(len(columns[name].foreign_keys), 1)
                fk = next(iter(columns[name].foreign_keys))
                self.assertEqual(fk.target_fullname, target)
                self.assertEqual(fk.ondelete, "RESTRICT")
        self.assertFalse(columns.display_name.nullable)

    def test_tenant_preliminary_state_and_nonblank_name(self):
        columns = Tenant.__table__.c
        status = columns.status
        self.assertFalse(status.nullable)
        self.assertEqual(status.default.arg, "RASCUNHO_INATIVO")
        self.assertEqual(str(status.server_default.arg), "'RASCUNHO_INATIVO'")
        self.assertEqual(
            self.checks(Tenant.__table__),
            {
                "ck_tenants_status_initial_only": "status = 'RASCUNHO_INATIVO'",
                "ck_tenants_display_name_nonblank":
                    "display_name ~ '[^[:space:]]'",
            },
        )
        for value, valid in (
            ("Caixinha A", True),
            ("", False),
            ("   ", False),
            (" \t\n ", False),
        ):
            with self.subTest(display_name=value):
                self.assertEqual(bool(re.search(r"\S", value)), valid)
        for value in ("", " ", "ATIVO", "SUSPENSO"):
            self.assertNotEqual(value, "RASCUNHO_INATIVO")

    def test_role_foreign_keys_dates_and_no_implicit_grant(self):
        columns = RoleGrant.__table__.c
        for name, target, nullable in (
            ("user_id", "user_identities.id", False),
            ("tenant_id", "tenants.id", True),
        ):
            with self.subTest(column=name):
                self.assertEqual(columns[name].nullable, nullable)
                self.assertEqual(len(columns[name].foreign_keys), 1)
                fk = next(iter(columns[name].foreign_keys))
                self.assertEqual(fk.target_fullname, target)
                self.assertEqual(fk.ondelete, "RESTRICT")
        self.assertFalse(columns.role.nullable)
        self.assertIsNone(columns.role.default)
        for name, nullable in (
            ("active_from", False),
            ("active_until", True),
            ("revoked_at", True),
        ):
            with self.subTest(column=name):
                self.assertEqual(columns[name].nullable, nullable)
                self.assertTrue(columns[name].type.timezone)
                self.assertIsNone(columns[name].default)
                self.assertIsNone(columns[name].server_default)

    def test_role_scope_domain_positive_and_negative_cases(self):
        checks = self.checks(RoleGrant.__table__)
        self.assertEqual(
            checks["ck_role_grants_role_valid"],
            "role IN ('MASTER', 'TENANT_ADMIN', 'TENANT_MEMBER')",
        )
        self.assertEqual(
            checks["ck_role_grants_role_scope_valid"],
            "(role = 'MASTER' AND tenant_id IS NULL) OR "
            "(role IN ('TENANT_ADMIN', 'TENANT_MEMBER') "
            "AND tenant_id IS NOT NULL)",
        )
        cases = (
            ("MASTER", None, True),
            ("MASTER", "tenant-a", False),
            ("TENANT_ADMIN", "tenant-a", True),
            ("TENANT_ADMIN", None, False),
            ("TENANT_MEMBER", "tenant-b", True),
            ("TENANT_MEMBER", None, False),
            ("UNKNOWN", "tenant-a", False),
            ("", None, False),
        )
        for role, tenant_id, valid in cases:
            with self.subTest(role=role, tenant_id=tenant_id):
                expected = (
                    (role == "MASTER" and tenant_id is None)
                    or (
                        role in ("TENANT_ADMIN", "TENANT_MEMBER")
                        and tenant_id is not None
                    )
                )
                self.assertEqual(expected, valid)

    def test_role_interval_and_revocation_structure(self):
        self.assertEqual(
            self.checks(RoleGrant.__table__)["ck_role_grants_active_interval_valid"],
            "active_until IS NULL OR active_until > active_from",
        )
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for end, valid in (
            (None, True),
            (start + timedelta(seconds=1), True),
            (start, False),
            (start - timedelta(seconds=1), False),
        ):
            with self.subTest(active_until=end):
                self.assertEqual(end is None or end > start, valid)
        self.assertTrue(RoleGrant.__table__.c.revoked_at.nullable)

    def test_exact_duplicate_indexes_and_multiple_roles(self):
        indexes = {index.name: index for index in RoleGrant.__table__.indexes}
        self.assertEqual(
            set(indexes),
            {"uq_role_grants_global_start", "uq_role_grants_tenant_start"},
        )
        expected = (
            (
                "uq_role_grants_global_start",
                ("user_id", "role", "active_from"),
                "WHERE tenant_id IS NULL",
            ),
            (
                "uq_role_grants_tenant_start",
                ("tenant_id", "user_id", "role", "active_from"),
                "WHERE tenant_id IS NOT NULL",
            ),
        )
        for name, columns, where in expected:
            with self.subTest(index=name):
                index = indexes[name]
                self.assertTrue(index.unique)
                self.assertEqual(
                    tuple(column.name for column in index.expressions),
                    columns,
                )
                sql = str(CreateIndex(index).compile(dialect=dialect()))
                self.assertIn("CREATE UNIQUE INDEX " + name, sql)
                self.assertIn(where, sql)
        self.assertFalse(bool(RoleGrant.__table__.c.user_id.unique))
        self.assertFalse(bool(RoleGrant.__table__.c.tenant_id.unique))

    def test_postgresql_ddl_compiles_without_connection(self):
        tenant_ddl = str(CreateTable(Tenant.__table__).compile(dialect=dialect()))
        role_ddl = str(CreateTable(RoleGrant.__table__).compile(dialect=dialect()))
        for fragment in (
            "DEFAULT 'RASCUNHO_INATIVO' NOT NULL",
            "display_name ~ '[^[:space:]]'",
            "status = 'RASCUNHO_INATIVO'",
            "FOREIGN KEY(admin_user_id) REFERENCES user_identities (id)",
            "FOREIGN KEY(contracting_party_id) REFERENCES contracting_parties (id)",
            "ON DELETE RESTRICT",
        ):
            with self.subTest(tenant_fragment=fragment):
                self.assertIn(fragment, tenant_ddl)
        for fragment in (
            "role IN ('MASTER', 'TENANT_ADMIN', 'TENANT_MEMBER')",
            "tenant_id IS NULL",
            "tenant_id IS NOT NULL",
            "active_until IS NULL OR active_until > active_from",
            "FOREIGN KEY(user_id) REFERENCES user_identities (id)",
            "FOREIGN KEY(tenant_id) REFERENCES tenants (id)",
            "TIMESTAMP WITH TIME ZONE",
            "ON DELETE RESTRICT",
        ):
            with self.subTest(role_fragment=fragment):
                self.assertIn(fragment, role_ddl)
