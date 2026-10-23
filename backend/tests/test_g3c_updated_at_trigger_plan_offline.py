"""IN-05: contraexemplo ORM e DDL PostgreSQL proposta, SEM execução SQL."""
import ast
import inspect
import unittest

from app.db.models import ContractingParty, IdentityCredential, UserIdentity
from app.g3c_updated_at_trigger_plan_offline import (
    expected_timestamp_tables, proposed_timestamp_ddl,
)


class G3CUpdatedAtDraftOfflineTests(unittest.TestCase):
    def test_three_exact_tables_and_no_duplicate_triggers(self):
        expected = (
            "user_identities", "contracting_parties", "identity_credentials"
        )
        self.assertEqual(expected_timestamp_tables(), expected)
        ddl = proposed_timestamp_ddl()
        self.assertEqual(len(ddl), 4)
        self.assertEqual(len(set(ddl)), 4)
        for idx, table in enumerate(expected, start=1):
            self.assertIn("BEFORE UPDATE ON public." + table, ddl[idx])
            self.assertIn("FOR EACH ROW EXECUTE FUNCTION public.frc22_stamp_updated_at()", ddl[idx])

    def test_function_monotonic_and_uses_wall_clock_not_transaction_start(self):
        func = proposed_timestamp_ddl()[0]
        for phrase in (
            "CREATE FUNCTION public.frc22_stamp_updated_at()",
            "RETURNS trigger",
            "LANGUAGE plpgsql",
            "SET search_path = pg_catalog, pg_temp",
            "NEW.updated_at := GREATEST(",
            "clock_timestamp()",
            "OLD.updated_at + INTERVAL '1 microsecond'",
            "RETURN NEW",
        ):
            self.assertIn(phrase, func)
        self.assertNotIn("NEW.updated_at := now()", func)
        self.assertNotIn("transaction_timestamp()", func)
        self.assertNotIn("current_timestamp", func)

    def test_orm_onupdate_alone_does_not_implement_db_trigger(self):
        """Uma coluna ORM onupdate não obriga SQL UPDATE direto a alterar timestamp."""
        for model in (UserIdentity, ContractingParty, IdentityCredential):
            col = model.__table__.c.updated_at
            self.assertIsNotNone(col.onupdate)
            self.assertIsNone(col.server_onupdate)
            self.assertFalse(col.nullable)

    def test_draft_requires_future_ddl_and_does_not_execute(self):
        import app.g3c_updated_at_trigger_plan_offline as module
        source = inspect.getsource(module)
        for forbidden in (
            "create_engine(", "psycopg.connect(", "connection.execute(",
            "op.execute(", "alembic.command", "DROP TABLE", "DELETE FROM",
            "COMMIT;", "ALTER ROLE",
        ):
            self.assertNotIn(forbidden, source)
        tree = ast.parse(source)
        self.assertFalse(any(
            isinstance(node, (ast.AsyncFunctionDef, ast.ClassDef))
            for node in tree.body
        ))

    def test_schema_is_fixed_and_no_untrusted_input_in_ddl(self):
        ddl = proposed_timestamp_ddl()
        for statement in ddl[1:]:
            self.assertTrue(statement.startswith("CREATE TRIGGER"))
            self.assertTrue(statement.endswith(
                "EXECUTE FUNCTION public.frc22_stamp_updated_at();"
            ))
        self.assertNotIn("IF EXISTS", " ".join(ddl))
        self.assertNotIn("CASCADE", " ".join(ddl))


if __name__ == "__main__":
    unittest.main()
