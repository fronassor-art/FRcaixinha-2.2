"""C16-R12.210 — garantias do executor de plano F2P4, só offline."""

from dataclasses import FrozenInstanceError, replace
import unittest
from unittest.mock import patch

from app.g3c_f2p4_two_connection_plan_offline import (
    EXPECTED_SCOPE, PLAN_STAGES, OfflineTrialBlocked, TrialScope,
    TrialStage, build_offline_plan, run_physical_trial, validate_scope,
)


class F2P4TwoConnectionPlanOfflineTests(unittest.TestCase):
    def test_build_plan_never_claims_any_physical_execution(self):
        result = build_offline_plan()
        self.assertEqual(result.status, "OFFLINE_PLAN_ONLY")
        self.assertFalse(result.connected_to_database)
        self.assertFalse(result.ddl_executed)
        self.assertFalse(result.physical_concurrency_verified)
        self.assertFalse(result.in05_revocation_verified)
        self.assertTrue(result.future_g2_required)

    def test_exact_authoritative_boundary_is_pinned(self):
        scope = build_offline_plan().scope
        self.assertEqual(scope.database, "frcaixinha_2_2_dev")
        self.assertEqual(scope.role, "frc22_trial_c16r12")
        self.assertEqual(scope.schema, "frc22_c16_trial_c16r12")
        self.assertEqual(scope.alembic_version, "f2p4_20261022")
        self.assertEqual(
            scope.repository_commit,
            "1685d987e60ade2a7b2373614bd18fa52064b9f8",
        )
        self.assertEqual(
            scope.backup_sha256,
            "a10fb867ef77d2a13994cb3e2c253003ced814b28f35026a42c58e78fee17337",
        )

    def test_rejects_any_unapproved_database_role_schema_revision(self):
        changes = {
            "database": "frcaixinha_2_2_other",
            "role": "frc22_owner",
            "schema": "public",
            "alembic_version": "c16r5_20261020",
            "repository_commit": "0" * 40,
            "backup_sha256": "0" * 64,
        }
        for key, wrong in changes.items():
            with self.subTest(key=key):
                scope = replace(EXPECTED_SCOPE, **{key: wrong})
                with self.assertRaisesRegex(
                    OfflineTrialBlocked, "^F2P4_OFFLINE_SCOPE_DENIED$"
                ):
                    build_offline_plan(scope)

    def test_all_six_scope_fields_reject_permissive_equality_objects(self):
        class AlwaysEqual:
            def __eq__(self, _other):
                return True

        for field in TrialScope.__dataclass_fields__:
            with self.subTest(field=field):
                forged = replace(EXPECTED_SCOPE, **{field: AlwaysEqual()})
                with self.assertRaisesRegex(
                    OfflineTrialBlocked, "^F2P4_OFFLINE_SCOPE_DENIED$"
                ):
                    build_offline_plan(forged)

    def test_scope_validation_never_calls_untrusted_equality(self):
        class DangerousEquality:
            def __eq__(self, _other):
                raise AssertionError("untrusted __eq__ was called")

        forged = replace(EXPECTED_SCOPE, role=DangerousEquality())
        with self.assertRaisesRegex(
            OfflineTrialBlocked, "^F2P4_OFFLINE_SCOPE_DENIED$"
        ):
            validate_scope(forged)

    def test_scope_rejects_string_subclass_with_custom_equality(self):
        class PermissiveString(str):
            def __eq__(self, _other):
                return True

        forged = replace(
            EXPECTED_SCOPE,
            backup_sha256=PermissiveString(EXPECTED_SCOPE.backup_sha256),
        )
        with self.assertRaisesRegex(
            OfflineTrialBlocked, "^F2P4_OFFLINE_SCOPE_DENIED$"
        ):
            build_offline_plan(forged)

    def test_denies_non_scope_objects_without_leaking_detail(self):
        for invalid in (None, {}, "public", object()):
            with self.subTest(kind=type(invalid).__name__):
                with self.assertRaisesRegex(
                    OfflineTrialBlocked, "^F2P4_OFFLINE_SCOPE_DENIED$"
                ) as raised:
                    validate_scope(invalid)
                self.assertIsNone(raised.exception.__cause__)

    def test_plan_immutable_and_has_no_mutation_methods(self):
        report = build_offline_plan()
        with self.assertRaises(FrozenInstanceError):
            report.status = "PASS"
        with self.assertRaises(FrozenInstanceError):
            report.scope.database = "public"
        self.assertIsInstance(report.stages, tuple)
        self.assertNotIn("commit", dir(report))
        self.assertNotIn("execute", dir(report))

    def test_shared_schema_and_fixtures_commit_before_two_sessions(self):
        stages = build_offline_plan().stages
        self.assertLess(stages.index(TrialStage.ALEMBIC_PREPARE_TRIAL_SCHEMA),
                        stages.index(TrialStage.COMMIT_SHARED_SCHEMA))
        self.assertLess(stages.index(TrialStage.COMMIT_SHARED_SCHEMA),
                        stages.index(TrialStage.VERIFY_TWO_DISTINCT_SESSIONS))
        self.assertLess(stages.index(TrialStage.COMMIT_SHARED_FIXTURES),
                        stages.index(TrialStage.VERIFY_TWO_DISTINCT_SESSIONS))

    def test_required_adversarial_cases_are_planned(self):
        stages = build_offline_plan().stages
        for requirement in (
            TrialStage.TEST_UNIQUE_IDEMPOTENCY,
            TrialStage.TEST_FINGERPRINT_CONFLICT,
            TrialStage.TEST_SAVEPOINT_AND_ROLLBACK,
            TrialStage.TEST_LOCK_ORDER_AND_TIMEOUT,
        ):
            self.assertIn(requirement, stages)
        self.assertEqual(len(stages), len(set(stages)))

    def test_in05_revocation_requires_distinct_approval(self):
        report = build_offline_plan()
        self.assertIn(TrialStage.STOP_BEFORE_IN05_REVOCATION, report.stages)
        self.assertFalse(report.in05_revocation_verified)

    def test_teardown_and_public_integrity_are_mandatory_last(self):
        stages = build_offline_plan().stages
        self.assertEqual(stages[-3:], (
            TrialStage.CLOSE_ALL_SESSIONS,
            TrialStage.ALEMBIC_CLEANUP_TRIAL_SCHEMA,
            TrialStage.FINAL_READ_ONLY_INTEGRITY,
        ))

    def test_entrypoint_rejects_even_fake_authorization(self):
        for args, kwargs in (((), {}), ((), {"g2": "AUTORIZADO"}),
                             ((EXPECTED_SCOPE,), {})):
            with self.subTest(case=(args, kwargs)):
                with self.assertRaisesRegex(
                    OfflineTrialBlocked,
                    "^F2P4_PHYSICAL_TRIAL_NOT_AUTHORIZED$",
                ):
                    run_physical_trial(*args, **kwargs)

    def test_plan_and_denied_execution_do_not_touch_db_network_files(self):
        with (patch("socket.create_connection") as connect,
              patch("subprocess.run") as process,
              patch("socket.socket") as socket,
              patch("builtins.open") as open_file):
            build_offline_plan()
            with self.assertRaises(OfflineTrialBlocked):
                run_physical_trial()
        connect.assert_not_called()
        process.assert_not_called()
        socket.assert_not_called()
        open_file.assert_not_called()

    def test_scope_accepts_exact_value_without_calling_database(self):
        self.assertIsNone(validate_scope(TrialScope()))
        self.assertEqual(PLAN_STAGES, build_offline_plan().stages)


if __name__ == "__main__":
    unittest.main()
