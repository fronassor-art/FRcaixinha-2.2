"""Transacoes do env.py com SQLAlchemy/Alembic reais e DBAPI em memoria.

Nenhum servidor, socket ou banco e criado. O cursor apenas registra comandos.
"""
import os
from pathlib import Path
import runpy
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from alembic import context
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import text
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.pool import NullPool


ENV = Path(__file__).resolve().parents[1] / "migrations" / "env.py"
URL = "postgresql+psycopg://frc22_owner@127.0.0.1:5432/frcaixinha_2_2_dev"
IDENTITY = ("frcaixinha_2_2_dev", "frc22_owner", "127.0.0.1", 5432, "180002")


class RecordingCursor:
    def __init__(self, dbapi):
        self.dbapi = dbapi
        self.description = None
        self.rowcount = -1
        self.rows = []

    def execute(self, statement, parameters=None):
        self.dbapi.events.append(("execute", statement))
        if statement.startswith("SELECT current_database()"):
            self.rows = [self.dbapi.identity]
            self.description = [
                (name, None, None, None, None, None, None)
                for name in ("database", "user", "host", "port", "version")
            ]

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None

    def fetchall(self):
        rows, self.rows = self.rows, []
        return rows

    def close(self):
        pass


class RecordingDBAPI:
    def __init__(self, identity=IDENTITY):
        self.identity = identity
        self.events = []

    def cursor(self):
        return RecordingCursor(self)

    def commit(self):
        self.events.append(("commit",))

    def rollback(self):
        self.events.append(("rollback",))

    def close(self):
        self.events.append(("close",))


class AlembicEnvTransactionOfflineTests(unittest.TestCase):
    def run_env(self, *, identity=IDENTITY, failure=None, gate=True, offline=False,
                url=URL, source=None):
        dbapi = RecordingDBAPI(identity)
        dialect = PGDialect()
        dialect.dbapi = SimpleNamespace(Error=Exception)
        engine = Engine(NullPool(creator=lambda: dbapi), dialect, make_url(URL))
        configured = []

        def configure(**kwargs):
            configured.append(MigrationContext.configure(
                connection=kwargs["connection"],
                opts={"target_metadata": kwargs["target_metadata"]},
            ))

        def run_migrations():
            connection = configured[-1].connection
            connection.execute(text("CREATE TABLE offline_marker (id integer)"))
            if failure is not None:
                raise failure
            connection.execute(text("INSERT INTO alembic_version VALUES ('offline')"))

        env = {"FRCAIXINHA_DATABASE_URL": url}
        if gate:
            env["FRCAIXINHA_ALEMBIC_WRITE_GATE"] = "AUTORIZADO_MIGRATION_CONTROLADA"
        self.dbapi = dbapi
        self.configured = configured
        with patch.dict(os.environ, env, clear=True), \
             patch.object(context, "config", Config(), create=True), \
             patch.object(context, "is_offline_mode", return_value=offline), \
             patch.object(context, "configure", side_effect=configure), \
             patch.object(context, "begin_transaction",
                          side_effect=lambda: configured[-1].begin_transaction()), \
             patch.object(context, "run_migrations", side_effect=run_migrations), \
             patch("sqlalchemy.create_engine", return_value=engine) as factory, \
             patch.object(engine, "dispose", wraps=engine.dispose) as dispose:
            self.factory = factory
            self.dispose = dispose
            if source is None:
                runpy.run_path(str(ENV), run_name="alembic_env_offline_test")
            else:
                exec(compile(source, str(ENV), "exec"), {"__name__": "alembic_env_offline_test"})
        return dbapi.events

    def test_success_commits_ddl_and_version_together_before_close(self):
        events = self.run_env()
        self.assertEqual(sum(e[0] == "commit" for e in events), 1)
        commit = events.index(("commit",))
        self.assertEqual(
            [e[1] for e in events[:commit] if e[0] == "execute"],
            ["SELECT current_database(), current_user, "
             "host(inet_server_addr()), inet_server_port(), "
             "current_setting('server_version_num')",
             "CREATE TABLE offline_marker (id integer)",
             "INSERT INTO alembic_version VALUES ('offline')"],
        )
        self.assertFalse(any(e[0] == "rollback" for e in events[:commit]))
        self.assertGreater(events.index(("close",)), commit)
        self.dispose.assert_called_once_with()

    def test_previous_connect_flow_reproduces_missing_commit(self):
        source = ENV.read_text().replace("with engine.begin() as connection:",
                                         "with engine.connect() as connection:")
        self.assertNotEqual(source, ENV.read_text())
        events = self.run_env(source=source)
        self.assertNotIn(("commit",), events)
        self.assertIn(("rollback",), events)
        self.assertEqual(len([e for e in events if e[0] == "execute"]), 3)

    def test_migration_failure_rolls_back_and_never_commits(self):
        failure = RuntimeError("offline migration failed")
        with self.assertRaises(RuntimeError) as raised:
            self.run_env(failure=failure)
        self.assertIs(raised.exception, failure)
        self.assertNotIn(("commit",), self.dbapi.events)
        self.assertIn(("rollback",), self.dbapi.events)
        self.assertIn(("close",), self.dbapi.events)
        self.dispose.assert_called_once_with()

    def test_identity_mismatch_rolls_back_before_ddl(self):
        with self.assertRaisesRegex(RuntimeError, "identidade"):
            self.run_env(identity=("wrong",) + IDENTITY[1:])
        self.assertEqual(len([e for e in self.dbapi.events if e[0] == "execute"]), 1)
        self.assertFalse(self.configured)
        self.assertNotIn(("commit",), self.dbapi.events)
        self.assertIn(("rollback",), self.dbapi.events)
        self.dispose.assert_called_once_with()

    def test_missing_gate_never_builds_engine(self):
        with self.assertRaisesRegex(RuntimeError, "autorizacao explicita"):
            self.run_env(gate=False)
        self.factory.assert_not_called()
        self.assertEqual(self.dbapi.events, [])

    def test_invalid_destination_never_builds_engine(self):
        with self.assertRaisesRegex(RuntimeError, "destino PostgreSQL"):
            self.run_env(url=URL.replace("frc22_owner@", "frc22_trial_c16r12@"))
        self.factory.assert_not_called()
        self.assertEqual(self.dbapi.events, [])

    def test_offline_mode_remains_blocked(self):
        with self.assertRaisesRegex(RuntimeError, "execucao offline"):
            self.run_env(offline=True)
        self.factory.assert_not_called()
        self.assertEqual(self.dbapi.events, [])


if __name__ == "__main__":
    unittest.main()
