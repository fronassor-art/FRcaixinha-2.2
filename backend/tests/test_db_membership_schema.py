"""Verificacoes estruturais de Membership, sem conexao ao PostgreSQL."""

import unittest
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.schema import CreateIndex, CreateTable

from app.db.models import Base, Cycle, Membership


class MembershipSchemaTests(unittest.TestCase):
    @staticmethod
    def checks():
        return {
            constraint.name: str(constraint.sqltext)
            for constraint in Membership.__table__.constraints
            if isinstance(constraint, CheckConstraint)
        }

    def test_columns_uuid_and_timestamps(self):
        columns = Membership.__table__.c
        self.assertIn("memberships", Base.metadata.tables)
        self.assertEqual(
            set(columns.keys()),
            {"id", "tenant_id", "cycle_id", "user_id", "joined_at", "left_at",
             "status", "created_at", "updated_at"},
        )
        self.assertTrue(columns.id.primary_key)
        self.assertIsInstance(columns.id.type, PGUUID)
        self.assertTrue(columns.id.type.as_uuid)
        self.assertTrue(callable(columns.id.default.arg))
        for name in ("tenant_id", "cycle_id", "user_id"):
            with self.subTest(column=name):
                self.assertIsInstance(columns[name].type, PGUUID)
                self.assertFalse(columns[name].nullable)
        for name in ("created_at", "updated_at"):
            with self.subTest(column=name):
                self.assertFalse(columns[name].nullable)
                self.assertIsInstance(columns[name].type, DateTime)
                self.assertTrue(columns[name].type.timezone)
                self.assertIsNotNone(columns[name].server_default)

    def test_composite_fk_restricts_cycle_to_same_tenant(self):
        table = Membership.__table__
        composite = [
            fk for fk in table.foreign_key_constraints
            if isinstance(fk, ForeignKeyConstraint) and len(fk.elements) == 2
        ]
        self.assertEqual(len(composite), 1)
        fk = composite[0]
        self.assertEqual(
            tuple(element.parent.name for element in fk.elements),
            ("tenant_id", "cycle_id"),
        )
        self.assertEqual(
            tuple(element.target_fullname for element in fk.elements),
            ("cycles.tenant_id", "cycles.id"),
        )
        self.assertEqual(fk.ondelete, "RESTRICT")
        self.assertEqual(len(table.foreign_key_constraints), 2)
        self.assertTrue(
            any(
                isinstance(constraint, UniqueConstraint)
                and tuple(column.name for column in constraint.columns)
                == ("tenant_id", "id")
                for constraint in Cycle.__table__.constraints
            )
        )

    def test_user_identity_fk_is_required_and_restricted(self):
        user_id = Membership.__table__.c.user_id
        self.assertFalse(user_id.nullable)
        self.assertEqual(len(user_id.foreign_keys), 1)
        fk = next(iter(user_id.foreign_keys))
        self.assertEqual(fk.target_fullname, "user_identities.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_initial_status_default_and_domain(self):
        status = Membership.__table__.c.status
        self.assertFalse(status.nullable)
        self.assertEqual(status.type.length, 32)
        self.assertEqual(status.default.arg, "PENDENTE_INATIVO")
        self.assertEqual(str(status.server_default.arg), "'PENDENTE_INATIVO'")
        self.assertEqual(
            self.checks()["ck_memberships_status_initial_only"],
            "status = 'PENDENTE_INATIVO'",
        )
        for invalid in ("", " ", "ATIVA", "ENCERRADA", "PLANEJADO_INATIVO"):
            with self.subTest(status=invalid):
                self.assertNotEqual(invalid, "PENDENTE_INATIVO")

    def test_pending_dates_are_null_and_timezone_aware(self):
        columns = Membership.__table__.c
        for name in ("joined_at", "left_at"):
            with self.subTest(column=name):
                self.assertTrue(columns[name].nullable)
                self.assertIsInstance(columns[name].type, DateTime)
                self.assertTrue(columns[name].type.timezone)
                self.assertIsNone(columns[name].default)
                self.assertIsNone(columns[name].server_default)
        self.assertEqual(
            self.checks()["ck_memberships_pending_dates_null"],
            "status <> 'PENDENTE_INATIVO' OR "
            "(joined_at IS NULL AND left_at IS NULL)",
        )
        instant = datetime(2027, 1, 1, tzinfo=timezone.utc)
        for joined, left, valid in (
            (None, None, True),
            (instant, None, False),
            (None, instant, False),
            (instant, instant, False),
        ):
            with self.subTest(joined=joined, left=left):
                self.assertEqual(joined is None and left is None, valid)

    def test_partial_unique_index_preserves_history(self):
        table = Membership.__table__
        self.assertFalse(any(
            isinstance(constraint, UniqueConstraint)
            for constraint in table.constraints
        ))
        self.assertFalse(bool(table.c.user_id.unique))
        indexes = {index.name: index for index in table.indexes}
        self.assertEqual(set(indexes), {"uq_memberships_active_identity_cycle"})
        index = indexes["uq_memberships_active_identity_cycle"]
        self.assertTrue(index.unique)
        self.assertEqual(
            tuple(column.name for column in index.expressions),
            ("tenant_id", "cycle_id", "user_id"),
        )
        sql = str(CreateIndex(index).compile(dialect=dialect()))
        self.assertIn("CREATE UNIQUE INDEX uq_memberships_active_identity_cycle", sql)
        self.assertIn("WHERE status = 'ATIVA'", sql)
        self.assertNotIn("ATIVA", self.checks()["ck_memberships_status_initial_only"])

    def test_postgresql_table_and_index_ddl_compile_without_connection(self):
        ddl = str(CreateTable(Membership.__table__).compile(dialect=dialect()))
        index = next(iter(Membership.__table__.indexes))
        index_ddl = str(CreateIndex(index).compile(dialect=dialect()))
        for fragment in (
            "tenant_id UUID NOT NULL",
            "cycle_id UUID NOT NULL",
            "user_id UUID NOT NULL",
            "joined_at TIMESTAMP WITH TIME ZONE",
            "left_at TIMESTAMP WITH TIME ZONE",
            "status VARCHAR(32) DEFAULT 'PENDENTE_INATIVO' NOT NULL",
            "FOREIGN KEY(tenant_id, cycle_id) REFERENCES cycles (tenant_id, id)",
            "FOREIGN KEY(user_id) REFERENCES user_identities (id)",
            "ON DELETE RESTRICT",
            "status = 'PENDENTE_INATIVO'",
            "joined_at IS NULL AND left_at IS NULL",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ddl)
        self.assertIn(
            "ON memberships (tenant_id, cycle_id, user_id) WHERE status = 'ATIVA'",
            index_ddl,
        )


if __name__ == "__main__":
    unittest.main()
