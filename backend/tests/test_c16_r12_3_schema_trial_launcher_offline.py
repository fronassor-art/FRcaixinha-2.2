"""Testes offline do acionador C16-R12.3. Sem conexao real ao banco."""

import sys
import unittest
from unittest.mock import patch

import c16_r12_3_schema_trial_launcher as launcher


class SchemaTrialLauncherOfflineTests(unittest.TestCase):

    def setUp(self):
        self.trial = launcher.trial
        self.assertIsNone(
            self.trial.APPROVED_SCHEMA_TRIAL_TARGET
        )
        self.assertIsNone(
            self.trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT
        )

    def tearDown(self):
        self.assertIsNone(
            self.trial.APPROVED_SCHEMA_TRIAL_TARGET
        )
        self.assertIsNone(
            self.trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT
        )

    def test_disabled_by_default(self):
        with (
            patch.object(sys, "argv", ["launcher"]),
            patch.object(
                self.trial.sqlalchemy, "create_engine"
            ) as engine,
        ):
            self.assertEqual(launcher.main(), 2)
            engine.assert_not_called()


    def test_execute_without_internal_approval_is_blocked(self):
        with (
            patch.object(sys, "argv", ["launcher", "--execute"]),
            patch("builtins.input") as confirmation,
            patch.object(self.trial, "run_schema_trial") as runner,
            patch.object(launcher, "getpass") as password,
            patch.object(
                self.trial.sqlalchemy, "create_engine"
            ) as engine,
        ):
            self.assertEqual(launcher.main(), 2)
            confirmation.assert_not_called()
            password.assert_not_called()
            runner.assert_not_called()
            engine.assert_not_called()

    def test_wrong_checkpoint_is_blocked(self):
        with (
            patch.object(
                self.trial,
                "APPROVED_SCHEMA_TRIAL_TARGET",
                launcher.TARGET,
            ),
            patch.object(
                self.trial,
                "APPROVED_SCHEMA_TRIAL_CHECKPOINT",
                launcher.CHECKPOINT,
            ),
            patch.object(
                sys, "argv", ["launcher", "--execute"]
            ),
            patch("builtins.input", return_value="INVALIDO"),
            patch.object(launcher, "getpass") as password,
            patch.object(
                self.trial.sqlalchemy, "create_engine"
            ) as engine,
        ):
            self.assertEqual(launcher.main(), 2)
            password.assert_not_called()
            engine.assert_not_called()

    def test_empty_password_is_blocked(self):
        with (
            patch.object(
                self.trial,
                "APPROVED_SCHEMA_TRIAL_TARGET",
                launcher.TARGET,
            ),
            patch.object(
                self.trial,
                "APPROVED_SCHEMA_TRIAL_CHECKPOINT",
                launcher.CHECKPOINT,
            ),
            patch.object(
                sys, "argv", ["launcher", "--execute"]
            ),
            patch(
                "builtins.input",
                return_value=launcher.CHECKPOINT,
            ),
            patch.object(
                launcher, "getpass", return_value=""
            ),
            patch.object(
                self.trial.sqlalchemy, "create_engine"
            ) as engine,
        ):
            self.assertEqual(launcher.main(), 2)
            engine.assert_not_called()

    def test_approved_mock_restores_gates(self):
        fake_password = "OFFLINE-ONLY"

        def fake_trial(*, target, authorization, trial_password):
            self.assertEqual(target, launcher.TARGET)
            self.assertEqual(
                authorization.checkpoint, launcher.CHECKPOINT
            )
            self.assertEqual(authorization.target, target)
            self.assertEqual(trial_password, fake_password)
            self.assertEqual(
                self.trial.APPROVED_SCHEMA_TRIAL_TARGET, target
            )
            self.assertEqual(
                self.trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT,
                launcher.CHECKPOINT,
            )
            return self.trial.TrialResult(
                upgrades=(
                    self.trial.C15_REVISION,
                    self.trial.C16_REVISION,
                ),
                downgrades=(
                    self.trial.C16_REVISION,
                    self.trial.C15_REVISION,
                ),
                rolled_back=True,
            )

        with (
            patch.object(
                self.trial,
                "APPROVED_SCHEMA_TRIAL_TARGET",
                launcher.TARGET,
            ),
            patch.object(
                self.trial,
                "APPROVED_SCHEMA_TRIAL_CHECKPOINT",
                launcher.CHECKPOINT,
            ),
            patch.object(
                sys, "argv", ["launcher", "--execute"]
            ),
            patch(
                "builtins.input",
                return_value=launcher.CHECKPOINT,
            ),
            patch.object(
                launcher, "getpass",
                return_value=fake_password,
            ),
            patch.object(
                self.trial, "run_schema_trial",
                side_effect=fake_trial
            ) as runner,
            patch.object(
                self.trial.sqlalchemy, "create_engine"
            ) as engine,
        ):
            self.assertEqual(launcher.main(), 0)
            runner.assert_called_once()
            engine.assert_not_called()

    def test_failure_restores_gates(self):
        with (
            patch.object(
                self.trial,
                "APPROVED_SCHEMA_TRIAL_TARGET",
                launcher.TARGET,
            ),
            patch.object(
                self.trial,
                "APPROVED_SCHEMA_TRIAL_CHECKPOINT",
                launcher.CHECKPOINT,
            ),
            patch.object(
                sys, "argv", ["launcher", "--execute"]
            ),
            patch(
                "builtins.input",
                return_value=launcher.CHECKPOINT,
            ),
            patch.object(
                launcher, "getpass",
                return_value="OFFLINE-ONLY",
            ),
            patch.object(
                self.trial, "run_schema_trial",
                side_effect=RuntimeError("simulated failure")
            ),
            patch.object(
                self.trial.sqlalchemy, "create_engine"
            ) as engine,
        ):
            with self.assertRaisesRegex(
                RuntimeError, "simulated failure"
            ):
                launcher.main()
            engine.assert_not_called()


class ScopedAuthorizationOfflineTests(unittest.TestCase):
    """Exercise the CLI authorization scope without a PostgreSQL connection."""

    def setUp(self):
        self.trial = launcher.trial
        self.assert_gates_closed()

    def tearDown(self):
        self.assert_gates_closed()

    def assert_gates_closed(self):
        self.assertIsNone(self.trial.APPROVED_SCHEMA_TRIAL_TARGET)
        self.assertIsNone(self.trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT)

    def argv(self, checkpoint=None):
        return [
            "launcher", "--execute", "--authorize-checkpoint",
            launcher.CHECKPOINT if checkpoint is None else checkpoint,
        ]

    def result(self):
        return self.trial.TrialResult(
            upgrades=(self.trial.C15_REVISION, self.trial.C16_REVISION),
            downgrades=(self.trial.C16_REVISION, self.trial.C15_REVISION),
            rolled_back=True,
        )

    def test_authorization_argument_without_execute_does_not_prompt(self):
        with (
            patch.object(sys, "argv", [
                "launcher", "--authorize-checkpoint", launcher.CHECKPOINT,
            ]),
            patch("builtins.input") as confirmation,
            patch.object(launcher, "getpass") as password,
            patch.object(self.trial, "run_schema_trial") as runner,
            patch.object(self.trial.sqlalchemy, "create_engine") as engine,
        ):
            self.assertEqual(launcher.main(), 2)
            confirmation.assert_not_called()
            password.assert_not_called()
            runner.assert_not_called()
            engine.assert_not_called()

    def test_wrong_authorization_argument_blocks_before_any_prompt(self):
        with (
            patch.object(sys, "argv", self.argv("INVALIDO")),
            patch("builtins.input") as confirmation,
            patch.object(launcher, "getpass") as password,
            patch.object(self.trial, "run_schema_trial") as runner,
            patch.object(self.trial.sqlalchemy, "create_engine") as engine,
        ):
            self.assertEqual(launcher.main(), 2)
            confirmation.assert_not_called()
            password.assert_not_called()
            runner.assert_not_called()
            engine.assert_not_called()

    def test_scoped_confirmation_and_password_rejections_leave_gates_closed(self):
        for confirmation_value, password_value in (
            ("INVALIDO", "OFFLINE-ONLY"),
            (launcher.CHECKPOINT, ""),
        ):
            with self.subTest(confirmation=confirmation_value):
                with (
                    patch.object(sys, "argv", self.argv()),
                    patch("builtins.input", return_value=confirmation_value),
                    patch.object(launcher, "getpass", return_value=password_value),
                    patch.object(self.trial, "run_schema_trial") as runner,
                    patch.object(self.trial.sqlalchemy, "create_engine") as engine,
                ):
                    self.assertEqual(launcher.main(), 2)
                    runner.assert_not_called()
                    engine.assert_not_called()
                self.assert_gates_closed()

    def test_scoped_success_authorizes_only_runner_and_restores_defaults(self):
        def confirmation(prompt):
            self.assert_gates_closed()
            return launcher.CHECKPOINT

        def password(prompt):
            self.assert_gates_closed()
            return "OFFLINE-ONLY"

        def runner(**kwargs):
            self.assertEqual(kwargs["target"], launcher.TARGET)
            self.assertEqual(kwargs["authorization"].target, launcher.TARGET)
            self.assertEqual(kwargs["authorization"].checkpoint, launcher.CHECKPOINT)
            self.assertEqual(kwargs["trial_password"], "OFFLINE-ONLY")
            self.assertEqual(self.trial.APPROVED_SCHEMA_TRIAL_TARGET, launcher.TARGET)
            self.assertEqual(
                self.trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT, launcher.CHECKPOINT,
            )
            self.assertIsNone(self.trial.APPROVED_TRIAL_TARGET)
            self.assertIsNone(self.trial.APPROVED_TRIAL_CHECKPOINT)
            return self.result()

        with (
            patch.object(sys, "argv", self.argv()),
            patch("builtins.input", side_effect=confirmation),
            patch.object(launcher, "getpass", side_effect=password),
            patch.object(self.trial, "run_schema_trial", side_effect=runner) as run,
            patch.object(self.trial.sqlalchemy, "create_engine") as engine,
        ):
            self.assertEqual(launcher.main(), 0)
            run.assert_called_once()
            engine.assert_not_called()
        self.assert_gates_closed()

    def test_scoped_failure_and_interrupt_restore_gates_and_release_lock(self):
        for error in (RuntimeError("simulated failure"), KeyboardInterrupt()):
            with self.subTest(error=type(error).__name__):
                with (
                    patch.object(sys, "argv", self.argv()),
                    patch("builtins.input", return_value=launcher.CHECKPOINT),
                    patch.object(launcher, "getpass", return_value="OFFLINE-ONLY"),
                    patch.object(self.trial, "run_schema_trial", side_effect=error),
                    patch.object(self.trial.sqlalchemy, "create_engine") as engine,
                ):
                    with self.assertRaises(type(error)) as raised:
                        launcher.main()
                    self.assertIs(raised.exception, error)
                    engine.assert_not_called()
                self.assert_gates_closed()
                self.assertTrue(launcher._AUTHORIZATION_LOCK.acquire(blocking=False))
                launcher._AUTHORIZATION_LOCK.release()

    def test_divergent_result_restores_gates(self):
        with (
            patch.object(sys, "argv", self.argv()),
            patch("builtins.input", return_value=launcher.CHECKPOINT),
            patch.object(launcher, "getpass", return_value="OFFLINE-ONLY"),
            patch.object(self.trial, "run_schema_trial", return_value=None),
            patch.object(self.trial.sqlalchemy, "create_engine") as engine,
        ):
            with self.assertRaisesRegex(RuntimeError, "divergente"):
                launcher.main()
            engine.assert_not_called()
        self.assert_gates_closed()

    def test_preexisting_approval_is_never_overwritten(self):
        with (
            patch.object(self.trial, "APPROVED_SCHEMA_TRIAL_TARGET", launcher.TARGET),
            patch.object(sys, "argv", self.argv()),
            patch("builtins.input") as confirmation,
            patch.object(launcher, "getpass") as password,
            patch.object(self.trial, "run_schema_trial") as runner,
        ):
            self.assertEqual(launcher.main(), 2)
            confirmation.assert_not_called()
            password.assert_not_called()
            runner.assert_not_called()
            self.assertEqual(self.trial.APPROVED_SCHEMA_TRIAL_TARGET, launcher.TARGET)
        self.assert_gates_closed()

    def test_busy_authorization_lock_blocks_runner(self):
        self.assertTrue(launcher._AUTHORIZATION_LOCK.acquire(blocking=False))
        try:
            with (
                patch.object(sys, "argv", self.argv()),
                patch("builtins.input", return_value=launcher.CHECKPOINT),
                patch.object(launcher, "getpass", return_value="OFFLINE-ONLY"),
                patch.object(self.trial, "run_schema_trial") as runner,
            ):
                self.assertEqual(launcher.main(), 2)
                runner.assert_not_called()
        finally:
            launcher._AUTHORIZATION_LOCK.release()
        self.assert_gates_closed()



if __name__ == "__main__":
    unittest.main()
