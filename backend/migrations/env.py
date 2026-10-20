"""Alembic protegido para a base autoritativa do FRcaixinha 2.2."""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool, text
from sqlalchemy.engine import make_url

from app.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

EXPECTED_DATABASE = "frcaixinha_2_2_dev"
EXPECTED_USERNAME = "frc22_owner"
EXPECTED_HOST = "127.0.0.1"
EXPECTED_PORT = 5432

WRITE_GATE = "AUTORIZADO_MIGRATION_CONTROLADA"


def validated_database_url():
    """Valida o destino antes de construir qualquer conexao."""

    raw = os.environ.get("FRCAIXINHA_DATABASE_URL")

    if not raw:
        raise RuntimeError(
            "ALEMBIC_BLOCKED: URL de banco nao configurada"
        )

    try:
        url = make_url(raw)
    except Exception:
        raise RuntimeError(
            "ALEMBIC_BLOCKED: URL de banco invalida"
        ) from None

    if (
        url.drivername != "postgresql+psycopg"
        or url.database != EXPECTED_DATABASE
        or url.username != EXPECTED_USERNAME
        or url.host != EXPECTED_HOST
        or url.port != EXPECTED_PORT
        or bool(url.query)
    ):
        raise RuntimeError(
            "ALEMBIC_BLOCKED: destino PostgreSQL nao autorizado"
        )

    return url


def run_migrations_offline():
    raise RuntimeError(
        "ALEMBIC_BLOCKED: execucao offline nao autorizada"
    )


def run_migrations_online():
    if (
        os.environ.get("FRCAIXINHA_ALEMBIC_WRITE_GATE")
        != WRITE_GATE
    ):
        raise RuntimeError(
            "ALEMBIC_BLOCKED: autorizacao explicita ausente"
        )

    url = validated_database_url()

    engine = create_engine(
        url,
        poolclass=pool.NullPool,
        connect_args={"connect_timeout": 5},
    )

    try:
        with engine.connect() as connection:
            identity = connection.execute(
                text(
                    "SELECT current_database(), current_user, "
                    "host(inet_server_addr()), inet_server_port(), "
                    "current_setting('server_version_num')"
                )
            ).one()

            valid_identity = (
                identity[0] == EXPECTED_DATABASE
                and identity[1] == EXPECTED_USERNAME
                and identity[2] == EXPECTED_HOST
                and identity[3] == EXPECTED_PORT
                and 180000 <= int(identity[4]) < 190000
            )

            if not valid_identity:
                raise RuntimeError(
                    "ALEMBIC_BLOCKED: identidade do servidor divergente"
                )

            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
