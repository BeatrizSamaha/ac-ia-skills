"""Módulo Acesso: funcionários, senhas e tokens."""
from datetime import datetime, timedelta

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.erros import Conflito, NaoAutorizado, NaoEncontrado, RegraViolada
from app.models import Funcionario, Perfil

DURACAO_TOKEN = timedelta(hours=8)
TAMANHO_MINIMO_SENHA = 8
BCRYPT_ROUNDS = 12  # os testes reduzem para acelerar


def _hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt(BCRYPT_ROUNDS)).decode()


def _confere(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())


def criar_funcionario(
    s: Session, *, nome: str, email: str, senha: str, perfil: Perfil
) -> Funcionario:
    email = email.strip().lower()
    if len(senha) < TAMANHO_MINIMO_SENHA:
        raise RegraViolada(f"A senha precisa ter ao menos {TAMANHO_MINIMO_SENHA} caracteres.")
    if s.scalar(select(Funcionario).where(Funcionario.email == email)):
        raise Conflito("Já existe funcionário com este e-mail.")
    f = Funcionario(nome=nome.strip(), email=email, senha_hash=_hash(senha), perfil=perfil)
    s.add(f)
    s.commit()
    return f


def listar_funcionarios(s: Session) -> list[Funcionario]:
    return list(s.scalars(select(Funcionario).order_by(Funcionario.nome)))


def desativar_funcionario(s: Session, funcionario_id: int) -> Funcionario:
    f = s.get(Funcionario, funcionario_id)
    if not f:
        raise NaoEncontrado("Funcionário não encontrado.")
    f.ativo = False
    s.commit()
    return f


def autenticar(s: Session, email: str, senha: str, segredo: str, agora: datetime) -> str:
    f = s.scalar(select(Funcionario).where(Funcionario.email == email.strip().lower()))
    if not f or not f.ativo or not _confere(senha, f.senha_hash):
        raise NaoAutorizado("E-mail ou senha inválidos.")
    payload = {"sub": str(f.id), "perfil": f.perfil.value, "exp": int((agora + DURACAO_TOKEN).timestamp())}
    return jwt.encode(payload, segredo, algorithm="HS256")


def funcionario_do_token(s: Session, token: str, segredo: str, agora: datetime) -> Funcionario:
    try:
        # A expiração é conferida com o relógio da aplicação (testável), não com o do sistema.
        payload = jwt.decode(token, segredo, algorithms=["HS256"], options={"verify_exp": False})
        expira = int(payload["exp"])
        funcionario_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
        raise NaoAutorizado("Token inválido.")
    if agora.timestamp() >= expira:
        raise NaoAutorizado("Sessão expirada. Entre novamente.")
    f = s.get(Funcionario, funcionario_id)
    if not f or not f.ativo:
        raise NaoAutorizado("Funcionário inativo ou inexistente.")
    return f
