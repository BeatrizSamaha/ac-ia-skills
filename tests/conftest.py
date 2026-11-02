from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.acesso import servico as acesso_servico
from app.acesso.servico import criar_funcionario
from app.main import create_app
from app.models import Perfil

AGORA = datetime(2026, 11, 2, 10, 0)

SENHA = "Senha-forte-123"

acesso_servico.BCRYPT_ROUNDS = 4  # acelera os testes; produção usa 12


class Relogio:
    """Relógio controlável para testar regras de validade."""

    def __init__(self, agora: datetime):
        self.agora = agora

    def __call__(self) -> datetime:
        return self.agora


@pytest.fixture
def relogio():
    return Relogio(AGORA)


@pytest.fixture
def app(relogio):
    app = create_app(database_url="sqlite://", jwt_secret="segredo-de-teste-com-32-bytes-ou-mais!", agora=relogio)
    yield app
    app.state.SessionLocal.kw["bind"].dispose()


@pytest.fixture
def client(app):
    return TestClient(app)


def _cria(app, nome, email, perfil):
    with app.state.SessionLocal() as s:
        criar_funcionario(s, nome=nome, email=email, senha=SENHA, perfil=perfil)


def entrar(client, email, senha=SENHA):
    r = client.post("/api/login", json={"email": email, "senha": senha})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def admin(app, client):
    _cria(app, "Ana Admin", "admin@hosp.br", Perfil.ADMINISTRADOR)
    return entrar(client, "admin@hosp.br")


@pytest.fixture
def farmaceutico(app, client):
    _cria(app, "Fábio Farmacêutico", "farm@hosp.br", Perfil.FARMACEUTICO)
    return entrar(client, "farm@hosp.br")


@pytest.fixture
def enfermeiro(app, client):
    _cria(app, "Elisa Enfermeira", "enf@hosp.br", Perfil.ENFERMEIRO)
    return entrar(client, "enf@hosp.br")


@pytest.fixture
def enfermeiro2(app, client):
    _cria(app, "Eduardo Enfermeiro", "enf2@hosp.br", Perfil.ENFERMEIRO)
    return entrar(client, "enf2@hosp.br")
