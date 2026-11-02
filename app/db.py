"""Infraestrutura de banco: engine, sessão e base declarativa."""
import importlib
from collections.abc import Iterator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def criar_sessionmaker(url: str) -> sessionmaker[Session]:
    kwargs: dict = {"connect_args": {"check_same_thread": False}}
    if url in ("sqlite://", "sqlite:///:memory:"):
        kwargs["poolclass"] = StaticPool
    engine = create_engine(url, **kwargs)
    importlib.import_module("app.models")  # registra as tabelas no Base

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def get_session(request: Request) -> Iterator[Session]:
    session: Session = request.app.state.SessionLocal()
    try:
        yield session
    finally:
        session.close()
