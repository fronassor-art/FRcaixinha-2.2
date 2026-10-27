"""API FastAPI isolada para demonstração de pré-cadastro PF.

Esta fábrica não é usada por ``app.main``. A aplicação retornada existe
somente para testes ou demonstração explícita, não persiste dados, não consulta
contas, não autentica e não concede qualquer acesso.
"""

from uuid import uuid4

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.identity_draft import IdentityDraftError, prepare_person_draft


class PfDemoInput(BaseModel):
    """Dados sintéticos aceitos apenas para validação formal preliminar."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)

    name: str = Field(min_length=1, max_length=200)
    cpf: str = Field(min_length=1, max_length=14)
    email: str = Field(min_length=1, max_length=254)
    phone: str = Field(min_length=1, max_length=15)


class PfDemoOutput(BaseModel):
    """Resposta sem dados pessoais e sem significado operacional."""

    case_ref: str
    status: str
    operational: bool
    identity_verified: bool
    access_granted: bool
    persisted: bool


def _generic_invalid_input(_: Request, __: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": "DEMO_INPUT_INVALID"})


def _generic_draft_error(_: Request, __: IdentityDraftError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": "DEMO_INPUT_INVALID"})


def create_demo_app() -> FastAPI:
    """Cria explicitamente uma app de demonstração sem efeitos externos."""
    application = FastAPI(title="FRcaixinha PF Demo", docs_url=None, redoc_url=None)
    router = APIRouter(prefix="/demo")

    @router.post("/pf/pre-registration", response_model=PfDemoOutput)
    async def pre_register_pf(payload: PfDemoInput) -> PfDemoOutput:
        # A validação produz uma representação transitória; nenhuma parte é
        # retornada ou persistida, e o resultado nunca significa identidade.
        prepare_person_draft(**payload.model_dump())
        return PfDemoOutput(
            case_ref=f"demo-{uuid4().hex}",
            status="PRELIMINARY_DEMO_ONLY",
            operational=False,
            identity_verified=False,
            access_granted=False,
            persisted=False,
        )

    application.add_exception_handler(RequestValidationError, _generic_invalid_input)
    application.add_exception_handler(IdentityDraftError, _generic_draft_error)
    application.include_router(router)
    return application
