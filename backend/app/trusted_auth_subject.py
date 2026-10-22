"""Contrato offline para resolver sujeito autenticado por verificador confiável.

O chamador NÃO pode construir esses fatos a partir de headers, CPF ou e-mail.
Não há login, emissão de sessão ou consulta a provedor neste módulo.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.offline_credentials import SessionFacts, session_is_current


_ISSUER = re.compile(r"[a-z][a-z0-9_-]{0,31}", re.ASCII)
_AUDIENCE = "frcaixinha-api"


def issuer_is_valid(value: object) -> bool:
    """Mesma política de emissor para resolução e contratos derivados."""
    return isinstance(value, str) and _ISSUER.fullmatch(value) is not None


class AuthTrustError(ValueError):
    """Falha estável sem assertion, credencial ou identificador de pessoa."""


@dataclass(frozen=True, slots=True, repr=False)
class VerifiedAuthAssertion:
    issuer: str
    audience: str
    subject_id: UUID
    session: SessionFacts

    def __repr__(self) -> str:
        return "VerifiedAuthAssertion(<redacted>)"


class AuthAssertionVerifier(Protocol):
    """Porta implementada futuramente por serviço autenticador aprovado."""

    def verify_assertion(self, assertion: bytes) -> VerifiedAuthAssertion: ...


@dataclass(frozen=True, slots=True, repr=False)
class ResolvedAuthSubject:
    value: str
    subject_id: UUID
    issuer: str
    session: SessionFacts

    def __repr__(self) -> str:
        return "ResolvedAuthSubject(<redacted>)"


def resolve_auth_subject(
    *, assertion: bytes, verifier: AuthAssertionVerifier,
    expected_issuer: str, now: datetime,
) -> ResolvedAuthSubject:
    """Valida fatos retornados pela porta, mantendo sujeito separado de PII."""
    if not issuer_is_valid(expected_issuer):
        raise AuthTrustError("AUTH_POLICY_INVALID")
    if not isinstance(assertion, bytes) or not 16 <= len(assertion) <= 4096:
        raise AuthTrustError("AUTH_ASSERTION_REJECTED")
    try:
        fact = verifier.verify_assertion(assertion)
        if (not isinstance(fact, VerifiedAuthAssertion)
                or fact.issuer != expected_issuer
                or fact.audience != _AUDIENCE
                or not isinstance(fact.subject_id, UUID)
                or fact.subject_id.int == 0
                or not isinstance(fact.session, SessionFacts)
                or not session_is_current(fact.session,
                                          subject_id=fact.subject_id, now=now)):
            raise ValueError
        return ResolvedAuthSubject(
            value=f"{fact.issuer}:{fact.subject_id}",
            subject_id=fact.subject_id, issuer=fact.issuer,
            session=fact.session,
        )
    except Exception:
        raise AuthTrustError("AUTH_ASSERTION_REJECTED") from None
