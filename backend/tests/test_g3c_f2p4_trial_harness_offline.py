"""C16-R12.221 — testes negativos do manifesto G3-C F2P4, SEM banco."""

from dataclasses import FrozenInstanceError, replace
import unittest
from unittest.mock import patch

from app import g3c_f2p4_trial_harness_offline as harness_module

from app.g3c_f2p4_trial_harness_offline import (
    EXPECTED_MANIFEST, REQUIRED_FKS, SCHEMA, STAGES, TABLES,
    ForeignKeyBoundary, HarnessBlocked, OfflineHarnessManifest,
    Stage, build_offline_harness, run_physical_trial, validate_manifest,
)


class F2P4HarnessOfflineTests(unittest.TestCase):
    def denied(self, candidate):
        with self.assertRaisesRegex(
            HarnessBlocked, "^F2P4_221_OFFLINE_SCOPE_DENIED$"
        ) as raised:
            validate_manifest(candidate)
        self.assertIsNone(raised.exception.__cause__)

    def test_manifest_is_exact_and_offline_only(self):
        report = build_offline_harness()
        self.assertEqual(report.status, "OFFLINE_MANIFEST_ONLY")
        self.assertFalse(report.database_connected)
        self.assertFalse(report.migration_executed)
        self.assertFalse(report.two_connections_verified)
        self.assertFalse(report.schema_created)
        self.assertFalse(report.in05_tested)
        self.assertFalse(report.cleanup_performed)
        self.assertTrue(report.future_g2_required)

    def test_one_authoritative_database_and_pinned_sha(self):
        m = EXPECTED_MANIFEST
        self.assertEqual(m.database, "frcaixinha_2_2_dev")
        self.assertEqual(m.role, "frc22_trial_c16r12")
        self.assertEqual(m.schema, SCHEMA)
        self.assertEqual(m.authoritative_revision, "f2p4_20261022")
        self.assertEqual(m.repository_commit,
                         "12a1e3f25197b98442c225a5c1ef86044c2dd22f")
        self.assertEqual(m.trial_version_table, "alembic_version_trial")
        self.assertEqual(m.trial_version_schema, SCHEMA)

    def test_all_six_tables_exact_and_nonfinancial(self):
        self.assertEqual(len(TABLES), 6)
        self.assertEqual(len(set(TABLES)), 6)
        self.assertNotIn("payments", TABLES)
        self.assertNotIn("quotas", TABLES)
        self.assertNotIn("tenants", TABLES)
        self.assertEqual(EXPECTED_MANIFEST.tables, TABLES)

    def test_fks_nine_and_scoped_locally(self):
        self.assertEqual(len(REQUIRED_FKS), 9)
        for fk in REQUIRED_FKS:
            self.assertEqual((fk.source_schema, fk.target_schema),
                             (SCHEMA, SCHEMA))
            self.assertIn(fk.source_table, TABLES)
            self.assertIn(fk.target_table, TABLES)
        self.assertIn(
            ("party_id", "identity_id"),
            [fk.source_columns for fk in REQUIRED_FKS],
        )

    def test_all_scalar_boundary_changes_denied(self):
        changes = {
            "database": "frcaixinha_2_2_shadow",
            "role": "frc22_owner",
            "schema": "public",
            "authoritative_revision": "c16r5_20261020",
            "repository_commit": "0" * 40,
            "backup_sha256": "0" * 64,
            "trial_version_schema": "public",
            "trial_version_table": "alembic_version",
        }
        for field, invalid in changes.items():
            with self.subTest(field=field):
                self.denied(replace(EXPECTED_MANIFEST, **{field: invalid}))

    def test_all_scalar_boundary_permissive_objects_denied(self):
        class AlwaysEqual:
            def __eq__(self, _other):
                return True
        for field in ("database", "role", "schema", "authoritative_revision",
                      "repository_commit", "backup_sha256",
                      "trial_version_schema", "trial_version_table"):
            with self.subTest(field=field):
                self.denied(replace(EXPECTED_MANIFEST, **{field: AlwaysEqual()}))

    def test_dangerous_equality_never_invoked(self):
        class Bad:
            def __eq__(self, _other):
                raise AssertionError("must not run")
        self.denied(replace(EXPECTED_MANIFEST, schema=Bad()))
        self.denied(replace(EXPECTED_MANIFEST, tables=(Bad(),) + TABLES[1:]))
        self.denied(replace(EXPECTED_MANIFEST, foreign_keys=(Bad(),) + REQUIRED_FKS[1:]))

    def test_rejects_str_subclass_and_bool_as_scope_value(self):
        class Liar(str):
            def __eq__(self, _other):
                return True
        self.denied(replace(EXPECTED_MANIFEST, schema=Liar(SCHEMA)))
        self.denied(replace(EXPECTED_MANIFEST, role=True))

    def test_deny_unknown_schema_table_or_missing_table(self):
        self.denied(replace(EXPECTED_MANIFEST, tables=("public.user_identities",) + TABLES[1:]))
        self.denied(replace(EXPECTED_MANIFEST, tables=TABLES[:-1]))
        self.denied(replace(EXPECTED_MANIFEST, tables=TABLES + ("memberships",)))
        self.denied(replace(EXPECTED_MANIFEST, tables=list(TABLES)))

    def test_rejects_cross_schema_fk(self):
        first = REQUIRED_FKS[0]
        cross = replace(first, target_schema="public")
        self.denied(replace(EXPECTED_MANIFEST, foreign_keys=(cross,) + REQUIRED_FKS[1:]))

    def test_rejects_cross_schema_fk_even_if_source_is_same(self):
        first = REQUIRED_FKS[0]
        cross = replace(first, source_schema="public")
        self.denied(replace(EXPECTED_MANIFEST, foreign_keys=(cross,) + REQUIRED_FKS[1:]))

    def test_rejects_mutated_fk_columns_or_destination(self):
        first = REQUIRED_FKS[0]
        for changed in (
            replace(first, source_columns=("identity_id",)),
            replace(first, target_table="tenants"),
            replace(first, target_columns=("party_id",)),
            replace(first, source_columns=["pf_user_id"]),
        ):
            with self.subTest(case=repr(changed)):
                self.denied(replace(EXPECTED_MANIFEST,
                                    foreign_keys=(changed,) + REQUIRED_FKS[1:]))

    def test_fk_field_with_object_equality_is_denied(self):
        class Bad:
            def __eq__(self, _other):
                raise AssertionError("must not run")
        altered = replace(REQUIRED_FKS[0], target_schema=Bad())
        self.denied(replace(EXPECTED_MANIFEST, foreign_keys=(altered,) + REQUIRED_FKS[1:]))

    def test_missing_duplicate_and_fake_fk_denied(self):
        self.denied(replace(EXPECTED_MANIFEST, foreign_keys=REQUIRED_FKS[:-1]))
        self.denied(replace(EXPECTED_MANIFEST,
                            foreign_keys=(REQUIRED_FKS[0],) + REQUIRED_FKS[:-1]))
        self.denied(replace(EXPECTED_MANIFEST,
                            foreign_keys=list(REQUIRED_FKS)))

    def test_planned_commit_precedes_opening_two_connections(self):
        self.assertLess(STAGES.index(Stage.COMMIT_TRIAL_SCHEMA),
                        STAGES.index(Stage.OPEN_CONNECTION_A))
        self.assertLess(STAGES.index(Stage.COMMIT_SYNTHETIC_FIXTURES),
                        STAGES.index(Stage.OPEN_CONNECTION_B))
        self.assertLess(STAGES.index(Stage.OPEN_CONNECTION_A),
                        STAGES.index(Stage.VERIFY_DISTINCT_BACKEND_PIDS))
        self.assertLess(STAGES.index(Stage.OPEN_CONNECTION_B),
                        STAGES.index(Stage.VERIFY_DISTINCT_BACKEND_PIDS))

    def test_in05_remains_blocked(self):
        self.assertIn(Stage.STOP_BEFORE_IN05, STAGES)
        self.assertFalse(EXPECTED_MANIFEST.in05_triggers_enabled)
        self.denied(replace(EXPECTED_MANIFEST, in05_triggers_enabled=True))
        self.denied(replace(EXPECTED_MANIFEST, in05_triggers_enabled=0))

    def test_schedule_reordering_or_injection_denied(self):
        self.denied(replace(EXPECTED_MANIFEST, stages=STAGES[1:] + STAGES[:1]))
        self.denied(replace(EXPECTED_MANIFEST, stages=list(STAGES)))
        self.denied(replace(EXPECTED_MANIFEST, stages=("DROP PUBLIC",) + STAGES[1:]))
        self.denied(replace(EXPECTED_MANIFEST, stages=(True,) + STAGES[1:]))

    def test_physical_entrypoint_denies_fake_approval(self):
        for args, kwargs in (((), {}), ((), {"g2": "APPROVED"}),
                             ((EXPECTED_MANIFEST,), {})):
            with self.subTest(case=(args, kwargs)):
                with self.assertRaisesRegex(
                    HarnessBlocked,
                    "^F2P4_221_PHYSICAL_TRIAL_NOT_AUTHORIZED$",
                ):
                    run_physical_trial(*args, **kwargs)

    def test_immutable_objects_and_no_mutation_methods(self):
        report = build_offline_harness()
        with self.assertRaises(FrozenInstanceError):
            report.status = "PASS"
        with self.assertRaises(FrozenInstanceError):
            report.manifest.schema = "public"
        with self.assertRaises(FrozenInstanceError):
            REQUIRED_FKS[0].source_schema = "public"
        self.assertNotIn("execute", dir(report))
        self.assertNotIn("commit", dir(report))

    def test_global_expected_manifest_setattr_schema_cannot_bypass(self):
        original = EXPECTED_MANIFEST.schema
        try:
            object.__setattr__(EXPECTED_MANIFEST, "schema", "public")
            self.denied(EXPECTED_MANIFEST)
            with self.assertRaisesRegex(
                HarnessBlocked, "^F2P4_221_OFFLINE_SCOPE_DENIED$"
            ):
                build_offline_harness()
        finally:
            object.__setattr__(EXPECTED_MANIFEST, "schema", original)
        self.assertIsNone(validate_manifest(EXPECTED_MANIFEST))

    def test_global_required_fk_setattr_cannot_bypass(self):
        fk = REQUIRED_FKS[0]
        original = fk.target_schema
        try:
            object.__setattr__(fk, "target_schema", "public")
            self.denied(EXPECTED_MANIFEST)
            with self.assertRaisesRegex(
                HarnessBlocked, "^F2P4_221_OFFLINE_SCOPE_DENIED$"
            ):
                build_offline_harness()
        finally:
            object.__setattr__(fk, "target_schema", original)
        self.assertIsNone(validate_manifest(EXPECTED_MANIFEST))

    def test_public_tables_rebinding_plus_manifest_setattr_cannot_bypass(self):
        original = EXPECTED_MANIFEST.tables
        altered = ("public.user_identities",) + TABLES[1:]
        try:
            with patch.object(harness_module, "TABLES", altered):
                object.__setattr__(EXPECTED_MANIFEST, "tables", altered)
                self.denied(EXPECTED_MANIFEST)
                with self.assertRaisesRegex(
                    HarnessBlocked, "^F2P4_221_OFFLINE_SCOPE_DENIED$"
                ):
                    build_offline_harness()
        finally:
            object.__setattr__(EXPECTED_MANIFEST, "tables", original)
        self.assertIsNone(validate_manifest(EXPECTED_MANIFEST))

    def test_public_stages_rebinding_plus_manifest_setattr_cannot_bypass(self):
        original = EXPECTED_MANIFEST.stages
        altered = STAGES[1:] + STAGES[:1]
        try:
            with patch.object(harness_module, "STAGES", altered):
                object.__setattr__(EXPECTED_MANIFEST, "stages", altered)
                self.denied(EXPECTED_MANIFEST)
                with self.assertRaisesRegex(
                    HarnessBlocked, "^F2P4_221_OFFLINE_SCOPE_DENIED$"
                ):
                    build_offline_harness()
        finally:
            object.__setattr__(EXPECTED_MANIFEST, "stages", original)
        self.assertIsNone(validate_manifest(EXPECTED_MANIFEST))

    def test_incomplete_exact_manifest_denied_without_attributeerror(self):
        self.denied(object.__new__(OfflineHarnessManifest))
        incomplete = object.__new__(OfflineHarnessManifest)
        object.__setattr__(incomplete, "database", "frcaixinha_2_2_dev")
        self.denied(incomplete)

    def test_incomplete_exact_fk_denied_without_attributeerror(self):
        incomplete = object.__new__(ForeignKeyBoundary)
        self.denied(replace(EXPECTED_MANIFEST,
                            foreign_keys=(incomplete,) + REQUIRED_FKS[1:]))

    def test_nonmanifest_objects_denied_without_details(self):
        for bad in (None, object(), {}, "frcaixinha_2_2_dev"):
            with self.subTest(kind=type(bad).__name__):
                self.denied(bad)

    def test_build_and_block_do_not_touch_file_network_db_subprocess(self):
        with (patch("socket.create_connection") as connect,
              patch("socket.socket") as socket,
              patch("subprocess.run") as process,
              patch("builtins.open") as open_file):
            build_offline_harness()
            with self.assertRaises(HarnessBlocked):
                run_physical_trial(g2="YES")
        connect.assert_not_called()
        socket.assert_not_called()
        process.assert_not_called()
        open_file.assert_not_called()

    def test_direct_manifest_instantiation_same_values_passes(self):
        self.assertIsNone(validate_manifest(OfflineHarnessManifest()))
        self.assertIs(build_offline_harness().manifest, EXPECTED_MANIFEST)


if __name__ == "__main__":
    unittest.main()
