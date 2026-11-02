from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.acesso import servico
from app.acesso.dependencias import exige, funcionario_logado
from app.db import get_session
from app.models import Funcionario, Perfil

router = APIRouter(tags=["Acesso"])


class LoginIn(BaseModel):
    email: str
    senha: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FuncionarioIn(BaseModel):
    nome: str
    email: str
    senha: str
    perfil: Perfil


class FuncionarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str
    perfil: Perfil
    ativo: bool


@router.post("/login", response_model=TokenOut)
def login(dados: LoginIn, request: Request, s: Session = Depends(get_session)):
    token = servico.autenticar(
        s, dados.email, dados.senha, request.app.state.jwt_secret, request.app.state.agora()
    )
    return TokenOut(access_token=token)


@router.get("/eu", response_model=FuncionarioOut)
def eu(f: Funcionario = Depends(funcionario_logado)):
    return f


@router.get("/funcionarios", response_model=list[FuncionarioOut])
def listar(_: Funcionario = Depends(exige(Perfil.ADMINISTRADOR)), s: Session = Depends(get_session)):
    return servico.listar_funcionarios(s)


@router.post("/funcionarios", response_model=FuncionarioOut, status_code=201)
def criar(
    dados: FuncionarioIn,
    _: Funcionario = Depends(exige(Perfil.ADMINISTRADOR)),
    s: Session = Depends(get_session),
):
    return servico.criar_funcionario(
        s, nome=dados.nome, email=dados.email, senha=dados.senha, perfil=dados.perfil
    )


@router.post("/funcionarios/{funcionario_id}/desativar", response_model=FuncionarioOut)
def desativar(
    funcionario_id: int,
    admin: Funcionario = Depends(exige(Perfil.ADMINISTRADOR)),
    s: Session = Depends(get_session),
):
    return servico.desativar_funcionario(s, funcionario_id, por=admin)
