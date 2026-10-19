"""C09: validacoes estruturais de Quota sem conexao ao PostgreSQL."""

import unittest
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.schema import CreateTable

from app.db.models import Base, Membership, Quota


class QuotaSchemaTests(unittest.TestCase):
    @staticmethod
    def checks():
        return {
            constraint.name: str(constraint.sqltext)
            for constraint in Quota.__table__.constraints
            if isinstance(constraint, CheckConstraint)
        }

    def test_columns_uuid_and_timestamps(self):
        columns = Quota.__table__.c
        self.assertIn("quotas", Base.metadata.tables)
        self.assertEqual(
            set(columns.keys()),
            {
                "id", "tenant_id", "cycle_id", "membership_id",
                "quota_number", "status", "effective_from", "effective_to",
                "created_at", "updated_at",
            },
        )
        self.assertTrue(columns.id.primary_key)
        self.assertIsInstance(columns.id.type, PGUUID)
        self.assertTrue(columns.id.type.as_uuid)
        self.assertTrue(callable(columns.id.default.arg))
        for field in ("tenant_id", "cycle_id", "membership_id"):
            with self.subTest(field=field):
                self.assertIsInstance(columns[field].type, PGUUID)
                self.assertTrue(columns[field].type.as_uuid)
                self.assertFalse(columns[field].nullable)
        for field in ("created_at", "updated_at"):
            with self.subTest(field=field):
                self.assertIsInstance(columns[field].type, DateTime)
                self.assertTrue(columns[field].type.timezone)
                self.assertFalse(columns[field].nullable)
                self.assertIsNotNone(columns[field].server_default)

    def test_composite_membership_fk_guards_tenant_and_cycle(self):
        fks = Quota.__table__.foreign_key_constraints
        self.assertEqual(len(fks), 1)
        fk = next(iter(fks))
        self.assertIsInstance(fk, ForeignKeyConstraint)
        self.assertEqual(
            tuple(item.parent.name for item in fk.elements),
            ("tenant_id", "cycle_id", "membership_id"),
        )
        self.assertEqual(
            tuple(item.target_fullname for item in fk.elements),
            ("memberships.tenant_id", "memberships.cycle_id", "memberships.id"),
        )
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_membership_has_composite_reference_key(self):
        uniques = {
            tuple(column.name for column in constraint.columns)
            for constraint in Membership.__table__.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        self.assertEqual(uniques, {("tenant_id", "cycle_id", "id")})

    def test_quota_number_is_positive_integer(self):
        number = Quota.__table__.c.quota_number
        self.assertIsInstance(number.type, Integer)
        self.assertFalse(number.nullable)
        self.assertIsNone(number.default)
        self.assertIsNone(number.server_default)
        self.assertEqual(
            self.checks()["ck_quotas_quota_number_positive"],
            "quota_number > 0",
        )
        for value, valid in ((-1, False), (0, False), (1, True), (20, True)):
            with self.subTest(value=value):
                self.assertEqual(value > 0, valid)

    def test_unique_number_per_tenant_cycle_and_multiple_member_quotas(self):
        table = Quota.__table__
        uniques = {
            tuple(column.name for column in constraint.columns)
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        self.assertEqual(uniques, {("tenant_id", "cycle_id", "quota_number")})
        self.assertFalse(bool(table.c.membership_id.unique))
        self.assertFalse(table.indexes)
        # Os numeros 1 e 2 podem referir o mesmo membro; nenhum UNIQUE o impede.
        sample = [
            ("tenant-a", "cycle-a", "member-a", 1),
            ("tenant-a", "cycle-a", "member-a", 2),
            ("tenant-b", "cycle-b", "member-a", 1),
        ]
        self.assertEqual(
            len({(tenant, cycle, number) for tenant, cycle, _, number in sample}),
            len(sample),
        )
        duplicate = ("tenant-a", "cycle-a", "member-b", 1)
        self.assertIn(
            (duplicate[0], duplicate[1], duplicate[3]),
            {(tenant, cycle, number) for tenant, cycle, _, number in sample},
        )

    def test_initial_status_cannot_activate_quota(self):
        status = Quota.__table__.c.status
        self.assertEqual(status.type.length, 32)
        self.assertFalse(status.nullable)
        self.assertEqual(status.default.arg, "PENDENTE_INATIVA")
        self.assertEqual(str(status.server_default.arg), "'PENDENTE_INATIVA'")
        self.assertEqual(
            self.checks()["ck_quotas_status_initial_only"],
            "status = 'PENDENTE_INATIVA'",
        )
        for state in ("ATIVA", "ENCERRADA", "CANCELADA", "", " "):
            with self.subTest(state=state):
                self.assertNotEqual(state, "PENDENTE_INATIVA")

    def test_inactive_effective_dates_are_null_and_timezone_aware(self):
        columns = Quota.__table__.c
        for field in ("effective_from", "effective_to"):
            with self.subTest(field=field):
                self.assertIsInstance(columns[field].type, DateTime)
                self.assertTrue(columns[field].type.timezone)
                self.assertTrue(columns[field].nullable)
                self.assertIsNone(columns[field].default)
                self.assertIsNone(columns[field].server_default)
        self.assertEqual(
            self.checks()["ck_quotas_inactive_dates_null"],
            "status <> 'PENDENTE_INATIVA' OR "
            "(effective_from IS NULL AND effective_to IS NULL)",
        )
        when = datetime(2027, 1, 1, tzinfo=timezone.utc)
        for beginning, end, valid in (
            (None, None, True),
            (when, None, False),
            (None, when, False),
            (when, when, False),
        ):
            with self.subTest(beginning=beginning, end=end):
                self.assertEqual(beginning is None and end is None, valid)

    def test_postgresql_ddl_compiles_without_database_connection(self):
        ddl = str(CreateTable(Quota.__table__).compile(dialect=dialect()))
        for fragment in (
            "id UUID NOT NULL",
            "tenant_id UUID NOT NULL",
            "cycle_id UUID NOT NULL",
            "membership_id UUID NOT NULL",
            "quota_number INTEGER NOT NULL",
            "status VARCHAR(32) DEFAULT 'PENDENTE_INATIVA' NOT NULL",
            "effective_from TIMESTAMP WITH TIME ZONE",
            "effective_to TIMESTAMP WITH TIME ZONE",
            "CONSTRAINT uq_quotas_tenant_id_cycle_id_quota_number "
            "UNIQUE (tenant_id, cycle_id, quota_number)",
            "FOREIGN KEY(tenant_id, cycle_id, membership_id) "
            "REFERENCES memberships (tenant_id, cycle_id, id)",
            "ON DELETE RESTRICT",
            "quota_number > 0",
            "status = 'PENDENTE_INATIVA'",
            "effective_from IS NULL AND effective_to IS NULL",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ddl)


if __name__ == "__main__":
    unittest.main()
