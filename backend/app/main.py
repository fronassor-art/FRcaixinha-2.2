"""Criação da aplicação ASGI mínima."""

from fastapi import FastAPI

from app.health import router


def create_app() -> FastAPI:
    """Cria uma aplicação independente, sem recursos externos."""
    application = FastAPI()
    application.include_router(router)
    return application


app = create_app()
