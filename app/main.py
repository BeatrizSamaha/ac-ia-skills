"""Composição da aplicação: cria a API e conecta os módulos."""
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.db import criar_sessionmaker
from app.erros import ErroDeNegocio

WEB_DIR = Path(__file__).parent / "web"


def create_app(
    database_url: str = "sqlite:///medicamentos.db",
    jwt_secret: str = "",
    agora: Callable[[], datetime] = datetime.now,
) -> FastAPI:
    if len(jwt_secret) < 32:
        raise ValueError("Informe um segredo JWT com ao menos 32 caracteres.")
    app = FastAPI(
        title="Controle de Medicamentos Hospitalares",
        description="AC Métodos e Aplicações de IA — Ibmec BH",
        version="1.0.0",
    )
    app.state.SessionLocal = criar_sessionmaker(database_url)
    app.state.jwt_secret = jwt_secret
    app.state.agora = agora

    @app.exception_handler(ErroDeNegocio)
    async def _erro_de_negocio(_: Request, exc: ErroDeNegocio) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensagem})

    @app.exception_handler(RequestValidationError)
    async def _validacao(_: Request, exc: RequestValidationError) -> JSONResponse:
        campos = sorted({str(e["loc"][-1]) for e in exc.errors() if e.get("loc")})
        return JSONResponse(status_code=422, content={
            "detail": "Dados inválidos ou ausentes: " + ", ".join(campos) + "."})

    from app.acesso.rotas import router as acesso_router
    from app.estoque.rotas import router as estoque_router
    from app.monitoramento.rotas import router as monitoramento_router
    from app.movimentacoes.rotas import router as movimentacoes_router

    for router in (acesso_router, estoque_router, movimentacoes_router, monitoramento_router):
        app.include_router(router, prefix="/api")

    if WEB_DIR.exists():
        app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
    return app

