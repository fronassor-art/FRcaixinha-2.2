"""IN03/04/05 — prova offline dos limites do relógio e plano de revogação."""
import inspect
import re
import unittest
from datetime import datetime, timedelta, timezone

from app.g3c_artifact_invalidation_plan_offline import (
    proposed_artifact_invalidation_ddl,
)
from app.g3c_updated_at_trigger_plan_offline import proposed_timestamp_ddl


class ArtifactInvalidationPlanOfflineTests(unittest.TestCase):
    def test_identity_and_credential_updates_use_one_lock_order(self):
        expected = ["email_confirmation_challenges", "identity_sessions"]
        for statement in proposed_artifact_invalidation_ddl()[::2]:
            with self.subTest(function=statement.splitlines()[0]):
                updates = re.findall(
                    r"(?m)^ *UPDATE public[.]([a-z_]+)[ ]*$",
                    statement,
                )
                self.assertEqual(updates, expected)

    def test_clock_rollback_counterexample_demonstrates_timestamp_only_gap(self):
        """Um relógio que retrocede pode deixar updated_at < issued_at."""
        issued = datetime(2026, 10, 23, 13, 0, tzinfo=timezone.utc)
        old_updated = issued - timedelta(minutes=2)
        backwards_wall_clock = issued - timedelta(minutes=5)
        naive_monotonic = max(
            backwards_wall_clock, old_updated + timedelta(microseconds=1)
        )
        self.assertLess(naive_monotonic, issued)
        # Verde AQUI prova o risco, NAO a segurança do timestamp isolado.
        self.assertIn("clock_timestamp()", proposed_timestamp_ddl()[0])

    def test_identity_change_revokes_old_challenges_and_sessions(self):
        ddl = proposed_artifact_invalidation_ddl()
        self.assertEqual(len(ddl), 4)
        self.assertIn("OLD.email IS DISTINCT FROM NEW.email", ddl[0])
        self.assertIn("OLD.status IS DISTINCT FROM NEW.status", ddl[0])
        self.assertIn("UPDATE public.email_confirmation_challenges", ddl[0])
        self.assertIn("UPDATE public.identity_sessions", ddl[0])
        self.assertIn("consumed_at IS NULL", ddl[0])
        self.assertIn("revoked_at IS NULL", ddl[0])
        self.assertIn("identity_id = NEW.id", ddl[0])
        self.assertIn(
            "AFTER UPDATE OF email, status ON public.user_identities",
            ddl[1],
        )

    def test_credential_change_revokes_sessions_and_challenges(self):
        ddl = proposed_artifact_invalidation_ddl()
        self.assertIn(
            "OLD.password_digest IS DISTINCT FROM NEW.password_digest",
            ddl[2],
        )
        self.assertIn("OLD.status IS DISTINCT FROM NEW.status", ddl[2])
        self.assertIn("UPDATE public.identity_sessions", ddl[2])
        self.assertIn("UPDATE public.email_confirmation_challenges", ddl[2])
        self.assertIn("identity_id = NEW.identity_id", ddl[2])
        self.assertIn(
            "AFTER UPDATE OF password_digest, status ON public.identity_credentials",
            ddl[3],
        )

    def test_trigger_plan_is_static_not_executed_or_in_place_migration(self):
        import app.g3c_artifact_invalidation_plan_offline as module
        src = inspect.getsource(module)
        for fragment in (
            "create_engine(", "psycopg.connect(", "op.execute(",
            "connection.execute(", "alembic.command", "DROP TABLE",
            "DELETE FROM", "CASCADE", "COMMIT;",
        ):
            self.assertNotIn(fragment, src)
        for stmt in proposed_artifact_invalidation_ddl():
            self.assertNotIn("DROP ", stmt)
            self.assertNotIn("CASCADE", stmt)

    def test_revocation_preserves_consumed_evidence_and_no_ttl_cleanup(self):
        ddl = proposed_artifact_invalidation_ddl()
        for statement in (ddl[0], ddl[2]):
            self.assertIn("consumed_at IS NULL", statement)
            self.assertIn("revoked_at IS NULL", statement)
            self.assertNotIn("DELETE", statement)
        # Não se pressupõe prazo legal de expurgo nem exclusão automática.
        self.assertNotIn("expires_at <", " ".join(ddl))


if __name__ == "__main__":
    unittest.main()
