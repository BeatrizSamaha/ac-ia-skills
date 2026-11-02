"""Composição da aplicação: cria a API e conecta os módulos."""
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.db import criar_sessionmaker
from app.erros import ErroDeNegocio

WEB_DIR = Path(__file__).parent / "web"


def create_app(
    database_url: str = "sqlite:///medicamentos.db",
    jwt_secret: str = "troque-este-segredo-em-producao",
    agora: Callable[[], datetime] = datetime.now,
) -> FastAPI:
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

    from app.acesso.rotas import router as acesso_router
    from app.estoque.rotas import router as estoque_router
    from app.monitoramento.rotas import router as monitoramento_router
    from app.movimentacoes.rotas import router as movimentacoes_router

    for router in (acesso_router, estoque_router, movimentacoes_router, monitoramento_router):
        app.include_router(router, prefix="/api")

    if WEB_DIR.exists():
        app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
    return app

