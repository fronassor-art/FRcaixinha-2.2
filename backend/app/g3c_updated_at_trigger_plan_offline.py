"""IN-05 — proposta de DDL para atualização monotônica de updated_at, OFFLINE.

Este módulo contém APENAS strings para revisão de uma migration FUTURA,
distinta das migrations congeladas. Não abre conexões, não aplica DDL,
não atualiza dados e NÃO concede o gate F2P4.

Cuidado: updated_at somente será evidência de revogação/contato mutado
se TODAS as vias de escrita respeitarem o trigger e se o issued_at dos
desafios e sessões vier de relógio confiável PostgreSQL. Nem o trigger
nem os testes de strings comprovam essa política por si mesmos.
"""

from app.db.models import ContractingParty, IdentityCredential, UserIdentity

# A função não aceita argumentos dinâmicos nem esquema vindo do cliente.
# clock_timestamp (tempo de parede, pós-lock), e avanço >= 1 microssegundo
# para evitar igualdade após duas mudanças rápidas no mesmo registro.
_UPDATED_AT_FUNCTION_SQL = """
CREATE FUNCTION public.frc22_stamp_updated_at()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, pg_temp
AS $frc22_stamp$
BEGIN
    IF OLD.updated_at IS NULL THEN
        RAISE EXCEPTION 'FRC22_TIMESTAMP_INVARIANT';
    END IF;
    NEW.updated_at := GREATEST(
        clock_timestamp(),
        OLD.updated_at + INTERVAL '1 microsecond'
    );
    RETURN NEW;
END;
$frc22_stamp$;
""".strip()

_TRIGGER_TABLES = (
    UserIdentity.__tablename__,
    ContractingParty.__tablename__,
    IdentityCredential.__tablename__,
)


def proposed_timestamp_ddl() -> tuple[str, ...]:
    """Somente proposta para auditoria; não executa os comandos SQL."""
    ddl = [_UPDATED_AT_FUNCTION_SQL]
    for table in _TRIGGER_TABLES:
        ddl.append(
            f"CREATE TRIGGER frc22_stamp_updated_at "
            f"BEFORE UPDATE ON public.{table} "
            "FOR EACH ROW EXECUTE FUNCTION public.frc22_stamp_updated_at();"
        )
    return tuple(ddl)


def expected_timestamp_tables() -> tuple[str, ...]:
    """Escopo fixo: identidade, parte contratante e credencial."""
    return _TRIGGER_TABLES
