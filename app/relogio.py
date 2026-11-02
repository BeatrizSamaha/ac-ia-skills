"""Data de referência ("hoje") vinda do relógio injetável da aplicação."""
from datetime import date, datetime

from fastapi import Request


def hoje(request: Request) -> date:
    return request.app.state.agora().date()


def agora(request: Request) -> datetime:
    return request.app.state.agora()
