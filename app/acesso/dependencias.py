"""Dependências FastAPI de autenticação e autorização por perfil."""
from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.acesso.servico import funcionario_do_token
from app.db import get_session
from app.erros import NaoAutorizado, Proibido
from app.models import Funcionario, Perfil

_bearer = HTTPBearer(auto_error=False)


def funcionario_logado(
    request: Request,
    cred: HTTPAuthorizationCredentials | None = Depends(_bearer),
    s: Session = Depends(get_session),
) -> Funcionario:
    if cred is None:
        raise NaoAutorizado("Autenticação necessária.")
    return funcionario_do_token(
        s, cred.credentials, request.app.state.jwt_secret, request.app.state.agora()
    )


def exige(*perfis: Perfil) -> Callable[..., Funcionario]:
    def _dep(f: Funcionario = Depends(funcionario_logado)) -> Funcionario:
        if f.perfil not in perfis:
            raise Proibido("Seu perfil não tem permissão para esta operação.")
        return f

    return _dep
