"""Guarda física para adaptadores PostgreSQL G3-C ainda não ativados.

O chamador conserva a posse da conexão e da transação externa durante toda a
ação protegida. Esta inspeção não impede um commit prematuro após o retorno.
Não abre conexão, altera isolamento, nem executa commit ou rollback.
"""

from collections.abc import Mapping

from psycopg import Connection as PsycopgConnection
from psycopg.pq import TransactionStatus
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.g3c_transaction_guards_offline import TransactionGateError


def require_pg_transaction(connection: Connection, *, denial: str) -> None:
    """Exige transação lógica e física antes de SQL protegido.

    Uma transação lógica SQLAlchemy pode coexistir com DBAPI AUTOCOMMIT. Se a
    transação psycopg ainda estiver IDLE, SELECT 1 a inicia na MESMA conexão,
    mas somente depois de comprovar driver e autocommit=False. O estado é
    revalidado antes de devolver controle ao adaptador.
    """
    try:
        if (
            not isinstance(connection, Connection)
            or connection.closed is not False
            or connection.invalidated is not False
            or connection.in_transaction() is not True
        ):
            raise ValueError

        transaction = connection.get_transaction()
        if transaction is None or transaction.is_active is not True:
            raise ValueError
        if (connection.dialect.name != "postgresql"
                or connection.dialect.driver != "psycopg"):
            raise ValueError

        engine_options = connection.engine.get_execution_options()
        connection_options = connection.get_execution_options()
        for options in (engine_options, connection_options):
            if not isinstance(options, Mapping):
                raise ValueError
            isolation = options.get("isolation_level")
            if isolation is not None and (
                type(isolation) is not str
                or isolation.strip().upper() == "AUTOCOMMIT"
            ):
                raise ValueError

        driver = connection.connection.driver_connection
        if (not isinstance(driver, PsycopgConnection)
                or driver.autocommit is not False):
            raise ValueError

        status = driver.info.transaction_status
        if status is TransactionStatus.IDLE:
            result = connection.execute(text("SELECT 1")).scalar_one()
            if type(result) is not int or result != 1:
                raise ValueError
        elif status is not TransactionStatus.INTRANS:
            raise ValueError

        if (
            connection.closed is not False
            or connection.invalidated is not False
            or connection.in_transaction() is not True
            or connection.get_transaction() is not transaction
            or transaction.is_active is not True
            or connection.connection.driver_connection is not driver
            or driver.autocommit is not False
            or driver.info.transaction_status is not TransactionStatus.INTRANS
        ):
            raise ValueError
    except Exception:
        raise TransactionGateError(denial) from None
