"""IN-07: auditoria OFFLINE do downgrade de F2P4; nenhuma SQL executada."""
import unittest
from unittest.mock import patch

from app.g3c_f2p4_rollback_audit_offline import (
    DowngradeRisk, audit_current_f2p4_downgrade,
    audit_downgrade_source, require_nondestructive_approval,
)
from migrations.versions import f2p4_20261022_auth_bootstrap_draft as revision


class F2P4RollbackAuditOfflineTests(unittest.TestCase):
    def test_f2p4_downgrade_reports_all_four_destructive_tables(self):
        risk = audit_current_f2p4_downgrade()
        self.assertEqual(risk.revision, "f2p4_20261022")
        self.assertEqual(risk.drop_tables, (
            "identity_sessions",
            "registration_idempotency",
            "email_confirmation_challenges",
            "identity_credentials",
        ))
        self.assertTrue(risk.destructive)
        self.assertFalse(risk.authorized_to_execute)

    def test_f2p4_downgrade_reports_three_indexes(self):
        risk = audit_current_f2p4_downgrade()
        self.assertEqual(risk.drop_indexes, (
            "ix_identity_sessions_identity_expires",
            "ix_registration_idempotency_expires",
            "ix_email_confirmation_challenges_identity_expires",
        ))
        self.assertEqual(risk.unknown_operations, ())

    def test_explicit_runtime_approval_gate_never_granted_here(self):
        for risk in (
            audit_current_f2p4_downgrade(),
            DowngradeRisk("f2p4_20261022", (), (), ()),
        ):
            with self.subTest(destructive=risk.destructive):
                with self.assertRaisesRegex(
                    RuntimeError, "^F2P4_DOWNGRADE_NOT_AUTHORIZED$",
                ):
                    require_nondestructive_approval(risk)

    def test_dynamic_or_unknown_alembic_call_blocks_approval(self):
        for operation in (
            'op.drop_table(target)',
            'op.execute("DROP TABLE anything")',
            'unknown_function()',
        ):
            with self.subTest(operation=operation):
                risk = audit_downgrade_source(
                    "def downgrade():\n    " + operation + "\n",
                    "synthetic",
                )
                self.assertTrue(risk.destructive)
                self.assertFalse(risk.authorized_to_execute)
                self.assertTrue(risk.unknown_operations)

    def test_empty_downgrade_is_not_automatic_authorization(self):
        risk = audit_downgrade_source(
            "def downgrade():\n    pass\n", "synthetic",
        )
        self.assertFalse(risk.destructive)
        self.assertFalse(risk.authorized_to_execute)

    def test_missing_function_or_invalid_input_is_denied(self):
        for source in (
            "", "x = 1", "def upgrade():\n    pass",
            "def downgrade():\n    pass\ndef downgrade():\n    pass",
        ):
            with self.subTest(code=source[:15]):
                with self.assertRaisesRegex(
                    ValueError, "^DOWNGRADE_AUDIT_INVALID$",
                ):
                    audit_downgrade_source(source, "f2p4")

    def test_source_inspection_does_not_connect_or_apply_migration(self):
        with (
            patch("psycopg.connect") as connect,
            patch.object(revision.op, "drop_table") as drop_table,
            patch.object(revision.op, "drop_index") as drop_index,
        ):
            risk = audit_current_f2p4_downgrade()
        self.assertEqual(len(risk.drop_tables), 4)
        connect.assert_not_called()
        drop_table.assert_not_called()
        drop_index.assert_not_called()


if __name__ == "__main__":
    unittest.main()
