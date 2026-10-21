"""Acionador C16-R12.5; execução real exige autorização operacional separada."""

from __future__ import annotations

import argparse
from getpass import getpass
from threading import Lock

import pg_migration_trial_executor as trial


TARGET = trial.SchemaTrialTarget(
    host="127.0.0.1",
    port=5432,
    database="frcaixinha_2_2_dev",
    role="frc22_trial_c16r12",
    schema="frc22_c16_trial_c16r12",
)

CHECKPOINT = "C16-R12.3-SCHEMA-20261021"
_AUTHORIZATION_LOCK = Lock()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ensaio controlado C15/C16 com rollback."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Solicitar execução após autorização separada.",
    )
    parser.add_argument(
        "--authorize-checkpoint",
        help="Checkpoint exato, somente após autorização operacional separada.",
    )
    args = parser.parse_args()

    if not args.execute:
        print("BLOCKED: execução desabilitada por padrão.")
        return 2

    scoped = args.authorize_checkpoint is not None
    if scoped:
        if args.authorize_checkpoint != CHECKPOINT:
            print("BLOCKED: argumento de autorização divergente.")
            return 2
        if (
            trial.APPROVED_SCHEMA_TRIAL_TARGET is not None
            or trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT is not None
        ):
            print("BLOCKED: autorização interna já configurada.")
            return 2
    elif (
        trial.APPROVED_SCHEMA_TRIAL_TARGET != TARGET
        or trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT != CHECKPOINT
    ):
        print("BLOCKED: autorização interna não aprovada.")
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

    if not scoped:
        return _invoke_trial(password)

    # Standalone CLI only: never install permanent approvals or read credentials
    # from the environment. No approval is installed while prompting the user.
    if not _AUTHORIZATION_LOCK.acquire(blocking=False):
        print("BLOCKED: autorização de ensaio já em uso.")
        return 2
    try:
        if (
            trial.APPROVED_SCHEMA_TRIAL_TARGET is not None
            or trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT is not None
        ):
            print("BLOCKED: autorização interna mudou durante a confirmação.")
            return 2
        try:
            trial.APPROVED_SCHEMA_TRIAL_TARGET = TARGET
            trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT = CHECKPOINT
            return _invoke_trial(password)
        finally:
            trial.APPROVED_SCHEMA_TRIAL_TARGET = None
            trial.APPROVED_SCHEMA_TRIAL_CHECKPOINT = None
    finally:
        _AUTHORIZATION_LOCK.release()


def _invoke_trial(password: str) -> int:
    authorization = trial.SchemaTrialAuthorization(
        checkpoint=CHECKPOINT,
        target=TARGET,
    )
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
