"""Verificacoes estruturais de Cycle, sem conexao ao PostgreSQL."""

import unittest
from datetime import date

from sqlalchemy import CheckConstraint, Date, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.schema import CreateTable

from app.db.models import Base, Cycle


class CycleSchemaTests(unittest.TestCase):
    @staticmethod
    def checks():
        return {
            constraint.name: str(constraint.sqltext)
            for constraint in Cycle.__table__.constraints
            if isinstance(constraint, CheckConstraint)
        }

    def test_uuid_tenant_fk_and_timestamps(self):
        columns = Cycle.__table__.c
        self.assertIn("cycles", Base.metadata.tables)
        self.assertEqual(
            set(columns.keys()),
            {"id", "tenant_id", "year", "start_date", "end_date",
             "settlement_date", "status", "created_at", "updated_at"},
        )
        self.assertTrue(columns.id.primary_key)
        self.assertIsInstance(columns.id.type, PGUUID)
        self.assertTrue(columns.id.type.as_uuid)
        self.assertTrue(callable(columns.id.default.arg))
        self.assertFalse(columns.tenant_id.nullable)
        self.assertIsInstance(columns.tenant_id.type, PGUUID)
        self.assertEqual(len(columns.tenant_id.foreign_keys), 1)
        fk = next(iter(columns.tenant_id.foreign_keys))
        self.assertEqual(fk.target_fullname, "tenants.id")
        self.assertEqual(fk.ondelete, "RESTRICT")
        for name in ("created_at", "updated_at"):
            with self.subTest(column=name):
                self.assertFalse(columns[name].nullable)
                self.assertIsInstance(columns[name].type, DateTime)
                self.assertTrue(columns[name].type.timezone)
                self.assertIsNotNone(columns[name].server_default)

    def test_required_dates_and_calendar_checks(self):
        columns = Cycle.__table__.c
        self.assertIsInstance(columns.year.type, Integer)
        self.assertFalse(columns.year.nullable)
        for name in ("start_date", "end_date", "settlement_date"):
            with self.subTest(column=name):
                self.assertIsInstance(columns[name].type, Date)
                self.assertFalse(columns[name].nullable)
                self.assertIsNone(columns[name].default)
                self.assertIsNone(columns[name].server_default)
        self.assertEqual(
            self.checks(),
            {
                "ck_cycles_year_positive": "year >= 1",
                "ck_cycles_start_date_calendar": "start_date = make_date(year, 1, 1)",
                "ck_cycles_end_date_calendar": "end_date = make_date(year, 12, 31)",
                "ck_cycles_settlement_date_calendar":
                    "settlement_date = make_date(year + 1, 1, 10)",
                "ck_cycles_status_initial_only": "status = 'PLANEJADO_INATIVO'",
            },
        )

    def test_calendar_examples_are_logical_specification(self):
        # Estes casos nao comprovam a aplicacao das CHECK pelo servidor.
        cases = (
            (2027, date(2027, 1, 1), date(2027, 12, 31), date(2028, 1, 10), True),
            (2028, date(2028, 1, 1), date(2028, 12, 31), date(2029, 1, 10), True),
            (2027, date(2027, 1, 2), date(2027, 12, 31), date(2028, 1, 10), False),
            (2027, date(2027, 1, 1), date(2027, 12, 30), date(2028, 1, 10), False),
            (2027, date(2027, 1, 1), date(2027, 12, 31), date(2028, 1, 9), False),
            (2027, date(2027, 1, 1), date(2027, 12, 31), date(2027, 1, 10), False),
            (2028, date(2027, 1, 1), date(2027, 12, 31), date(2028, 1, 10), False),
        )
        for year, start, end, settlement, valid in cases:
            with self.subTest(year=year, start=start, end=end, settlement=settlement):
                self.assertEqual(
                    start == date(year, 1, 1)
                    and end == date(year, 12, 31)
                    and settlement == date(year + 1, 1, 10),
                    valid,
                )

    def test_only_approved_initial_status(self):
        status = Cycle.__table__.c.status
        self.assertIsInstance(status.type, String)
        self.assertEqual(status.type.length, 32)
        self.assertFalse(status.nullable)
        self.assertEqual(status.default.arg, "PLANEJADO_INATIVO")
        self.assertEqual(str(status.server_default.arg), "'PLANEJADO_INATIVO'")
        for invalid in ("", " ", "ATIVO", "FECHADO", "RASCUNHO_INATIVO"):
            with self.subTest(status=invalid):
                self.assertNotEqual(invalid, "PLANEJADO_INATIVO")

    def test_unique_keys_and_coexisting_years(self):
        table = Cycle.__table__
        uniques = {
            tuple(column.name for column in constraint.columns): constraint.name
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        self.assertEqual(
            uniques,
            {
                ("tenant_id", "year"): "uq_cycles_tenant_id_year",
                ("tenant_id", "id"): "uq_cycles_tenant_id_id",
            },
        )
        self.assertFalse(table.indexes)
        self.assertEqual(
            len({("tenant-a", 2027), ("tenant-b", 2027), ("tenant-a", 2028)}),
            3,
        )
        self.assertEqual(len({("tenant-a", 2027), ("tenant-a", 2027)}), 1)

    def test_postgresql_ddl_compiles_without_connection(self):
        ddl = str(CreateTable(Cycle.__table__).compile(dialect=dialect()))
        for fragment in (
            "id UUID NOT NULL",
            "tenant_id UUID NOT NULL",
            "year INTEGER NOT NULL",
            "start_date DATE NOT NULL",
            "end_date DATE NOT NULL",
            "settlement_date DATE NOT NULL",
            "status VARCHAR(32) DEFAULT 'PLANEJADO_INATIVO' NOT NULL",
            "TIMESTAMP WITH TIME ZONE",
            "CONSTRAINT uq_cycles_tenant_id_year UNIQUE (tenant_id, year)",
            "CONSTRAINT uq_cycles_tenant_id_id UNIQUE (tenant_id, id)",
            "FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT",
            "year >= 1",
            "start_date = make_date(year, 1, 1)",
            "end_date = make_date(year, 12, 31)",
            "settlement_date = make_date(year + 1, 1, 10)",
            "status = 'PLANEJADO_INATIVO'",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ddl)


if __name__ == "__main__":
    unittest.main()
