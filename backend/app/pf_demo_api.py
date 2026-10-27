"""API isolada para demonstrar o recebimento preliminar de dados PF sintéticos.

Esta fábrica não é usada por ``app.main``. Nenhuma resposta pública confirma
existência de identidade, registro, estado interno ou direito de acesso.
"""

from typing import Annotated

from fastapi import APIRouter, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.identity_draft import IdentityDraftError
from app.pf_preregistration import (
    PfPreRegistrationService,
    PreRegistrationError,
    TransientPreRegistrationStore,
)


class PfDemoInput(BaseModel):
    """Dados sintéticos aceitos apenas para validação preliminar."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)

    name: str = Field(min_length=1, max_length=200)
    cpf: str = Field(min_length=1, max_length=14)
    email: str = Field(min_length=1, max_length=254)
    phone: str = Field(min_length=1, max_length=15)


_NEUTRAL_BODY = {"detail": "DEMO_REQUEST_RECEIVED", "operational": False}
_NEUTRAL_ERRORS = frozenset({
    "IDEMPOTENCY_CONFLICT", "DUPLICATE_PRE_REGISTRATION",
    "PRE_REGISTRATION_CONFLICT",
})


def _neutral_ack() -> JSONResponse:
    """Mesmo status, corpo e cabeçalhos para novos, duplicados e replays."""
    return JSONResponse(status_code=202, content=_NEUTRAL_BODY)


def _generic_invalid_input(_: Request, __: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": "DEMO_INPUT_INVALID"})


def _generic_draft_error(_: Request, __: IdentityDraftError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": "DEMO_INPUT_INVALID"})


def _generic_pre_registration_error(_: Request, exc: PreRegistrationError) -> JSONResponse:
    code = exc.args[0] if exc.args else None
    if isinstance(code, str) and code in _NEUTRAL_ERRORS:
        return _neutral_ack()
    if code == "IDEMPOTENCY_KEY_MISSING":
        return JSONResponse(status_code=422, content={"detail": "DEMO_INPUT_INVALID"})
    if code == "IDEMPOTENCY_KEY_INVALID":
        return JSONResponse(status_code=422, content={"detail": "DEMO_REQUEST_REJECTED"})
    return JSONResponse(status_code=500, content={"detail": "DEMO_REQUEST_REJECTED"})


def create_demo_app(store: TransientPreRegistrationStore | None = None) -> FastAPI:
    """Cria explicitamente uma app de demonstração efêmera e sem efeitos reais."""
    application = FastAPI(title="FRcaixinha PF Demo", docs_url=None, redoc_url=None)
    service = PfPreRegistrationService(store if store is not None else TransientPreRegistrationStore())
    router = APIRouter(prefix="/demo")

    @router.post("/pf/pre-registration", status_code=202)
    async def pre_register_pf(
        payload: PfDemoInput,
        idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    ) -> JSONResponse:
        service.submit(**payload.model_dump(), idempotency_key=idempotency_key)
        return _neutral_ack()

    application.add_exception_handler(RequestValidationError, _generic_invalid_input)
    application.add_exception_handler(IdentityDraftError, _generic_draft_error)
    application.add_exception_handler(PreRegistrationError, _generic_pre_registration_error)
    application.include_router(router)
    return application
