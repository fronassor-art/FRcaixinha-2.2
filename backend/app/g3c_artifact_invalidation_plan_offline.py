"""IN-03/04/05 — DDL proposta de invalidação em mudança de identidade.

APENAS strings para revisão futura de migration; não cria trigger ou toca DB.
Motivo: updated_at é um detector insuficiente quando o relógio retrocede,
quando há caminho SQL sem trigger, ou quando a identidade A→B→A no intervalo.
Mesmo com triggers de invalidação, lock order/races precisam de prova SQL
real (IN03-T2/IN04-T2), ainda não autorizada.

Estas regras só podem ser instaladas APÓS as quatro tabelas F2P4 e sob
migration nova e aprovação independente. Nenhum serviço vivo usa o módulo.
"""

_IDENTITY_INVALIDATION_FUNCTION = """
CREATE FUNCTION public.frc22_invalidate_identity_artifacts()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, pg_temp
AS $frc22_identity$
BEGIN
    IF OLD.email IS DISTINCT FROM NEW.email
       OR OLD.status IS DISTINCT FROM NEW.status THEN
        UPDATE public.email_confirmation_challenges
        SET revoked_at = clock_timestamp()
        WHERE identity_id = NEW.id
          AND consumed_at IS NULL
          AND revoked_at IS NULL;

        UPDATE public.identity_sessions
        SET revoked_at = clock_timestamp()
        WHERE identity_id = NEW.id
          AND revoked_at IS NULL;
    END IF;
    RETURN NEW;
END;
$frc22_identity$;
""".strip()

_CREDENTIAL_INVALIDATION_FUNCTION = """
CREATE FUNCTION public.frc22_invalidate_credential_artifacts()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, pg_temp
AS $frc22_credential$
BEGIN
    IF OLD.password_digest IS DISTINCT FROM NEW.password_digest
       OR OLD.status IS DISTINCT FROM NEW.status THEN
        UPDATE public.email_confirmation_challenges
        SET revoked_at = clock_timestamp()
        WHERE identity_id = NEW.identity_id
          AND consumed_at IS NULL
          AND revoked_at IS NULL;

        UPDATE public.identity_sessions
        SET revoked_at = clock_timestamp()
        WHERE identity_id = NEW.identity_id
          AND revoked_at IS NULL;
    END IF;
    RETURN NEW;
END;
$frc22_credential$;
""".strip()


def proposed_artifact_invalidation_ddl() -> tuple[str, ...]:
    """Somente proposta, NÃO aplicar no banco principal."""
    return (
        _IDENTITY_INVALIDATION_FUNCTION,
        """CREATE TRIGGER frc22_invalidate_identity_artifacts
AFTER UPDATE OF email, status ON public.user_identities
FOR EACH ROW EXECUTE FUNCTION public.frc22_invalidate_identity_artifacts();""",
        _CREDENTIAL_INVALIDATION_FUNCTION,
        """CREATE TRIGGER frc22_invalidate_credential_artifacts
AFTER UPDATE OF password_digest, status ON public.identity_credentials
FOR EACH ROW EXECUTE FUNCTION public.frc22_invalidate_credential_artifacts();""",
    )
