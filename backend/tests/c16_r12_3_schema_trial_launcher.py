"""Acionador C16-R12.3: exige autorização separada para execução real."""

from __future__ import annotations

import argparse
from getpass import getpass
from unittest.mock import patch

import pg_migration_trial_executor as trial


TARGET = trial.SchemaTrialTarget(
    host="127.0.0.1",
    port=5432,
    database="frcaixinha_2_2_dev",
    role="frc22_trial_c16r12",
    schema="frc22_c16_trial_c16r12",
)

CHECKPOINT = "C16-R12.3-SCHEMA-20261021"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ensaio controlado C15/C16 com rollback."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Solicitar execução após autorização separada.",
    )
    args = parser.parse_args()

    if not args.execute:
        print("BLOCKED: execução desabilitada por padrão.")
        return 2

    if (
        trial.APPROVED_SCHEMA_TRIAL_TARGET is not None
        or trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT is not None
    ):
        print("BLOCKED: executor original não está desabilitado.")
        return 2

    print("ATENÇÃO: ensaio real no PostgreSQL autoritativo.")
    print(f"Banco: {TARGET.database}")
    print(f"Usuário: {TARGET.role}")
    print(f"Schema transacional: {TARGET.schema}")

    confirmation = input("Digite o checkpoint autorizado: ")
    if confirmation != CHECKPOINT:
        print("BLOCKED: checkpoint não confirmado.")
        return 2

    password = getpass("Senha do usuário restrito: ")
    if not password:
        print("BLOCKED: senha de ensaio ausente.")
        return 2

    authorization = trial.SchemaTrialAuthorization(
        checkpoint=CHECKPOINT,
        target=TARGET,
    )

    # Autorização limitada à chamada, neste processo independente.
    with (
        patch.object(
            trial, "APPROVED_SCHEMA_TRIAL_TARGET", TARGET
        ),
        patch.object(
            trial, "APPROVED_SCHEMA_TRIAL_CHECKPOINT",
            CHECKPOINT,
        ),
    ):
        result = trial.run_schema_trial(
            target=TARGET,
            authorization=authorization,
            trial_password=password,
        )

    expected = trial.TrialResult(
        upgrades=(trial.C15_REVISION, trial.C16_REVISION),
        downgrades=(trial.C16_REVISION, trial.C15_REVISION),
        rolled_back=True,
    )

    if result != expected:
        raise RuntimeError("Resultado do ensaio divergente.")

    print("C16_R12_3_SCHEMA_TRIAL=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
