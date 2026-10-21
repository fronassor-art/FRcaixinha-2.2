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


if __name__ == "__main__":
    unittest.main()
