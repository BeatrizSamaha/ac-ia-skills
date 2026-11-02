"""Ticket 01 — Login e gestão de funcionários."""
from tests.conftest import SENHA, entrar


def test_login_valido_devolve_token(client, admin):
    assert admin["Authorization"].startswith("Bearer ")


def test_login_com_senha_errada_e_recusado(client, admin):
    r = client.post("/api/login", json={"email": "admin@hosp.br", "senha": "errada"})
    assert r.status_code == 401


def test_login_de_email_inexistente_e_recusado(client):
    r = client.post("/api/login", json={"email": "ninguem@hosp.br", "senha": SENHA})
    assert r.status_code == 401


def test_rota_protegida_sem_token_responde_401(client):
    assert client.get("/api/funcionarios").status_code == 401


def test_token_invalido_responde_401(client):
    r = client.get("/api/funcionarios", headers={"Authorization": "Bearer lixo"})
    assert r.status_code == 401


def test_admin_cadastra_funcionario_que_consegue_entrar(client, admin):
    r = client.post(
        "/api/funcionarios",
        headers=admin,
        json={"nome": "Nina", "email": "nina@hosp.br", "senha": SENHA, "perfil": "enfermeiro"},
    )
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["perfil"] == "enfermeiro" and corpo["ativo"] is True
    assert "senha" not in corpo and "senha_hash" not in corpo
    entrar(client, "nina@hosp.br")


def test_email_duplicado_e_recusado(client, admin):
    dados = {"nome": "X", "email": "admin@hosp.br", "senha": SENHA, "perfil": "enfermeiro"}
    assert client.post("/api/funcionarios", headers=admin, json=dados).status_code == 409


def test_senha_curta_e_recusada(client, admin):
    dados = {"nome": "X", "email": "x@hosp.br", "senha": "123", "perfil": "enfermeiro"}
    assert client.post("/api/funcionarios", headers=admin, json=dados).status_code == 422


def test_admin_lista_funcionarios(client, admin, enfermeiro):
    r = client.get("/api/funcionarios", headers=admin)
    assert r.status_code == 200
    assert {f["email"] for f in r.json()} == {"admin@hosp.br", "enf@hosp.br"}


def test_nao_admin_nao_gerencia_funcionarios(client, admin, enfermeiro, farmaceutico):
    for quem in (enfermeiro, farmaceutico):
        assert client.get("/api/funcionarios", headers=quem).status_code == 403
        dados = {"nome": "X", "email": "y@hosp.br", "senha": SENHA, "perfil": "administrador"}
        assert client.post("/api/funcionarios", headers=quem, json=dados).status_code == 403


def test_funcionario_desativado_nao_entra_nem_usa_token_antigo(client, admin, enfermeiro):
    lista = client.get("/api/funcionarios", headers=admin).json()
    enf_id = next(f["id"] for f in lista if f["email"] == "enf@hosp.br")
    r = client.post(f"/api/funcionarios/{enf_id}/desativar", headers=admin)
    assert r.status_code == 200 and r.json()["ativo"] is False

    r = client.post("/api/login", json={"email": "enf@hosp.br", "senha": SENHA})
    assert r.status_code == 401
    assert client.get("/api/eu", headers=enfermeiro).status_code == 401


def test_desativar_inexistente_responde_404(client, admin):
    assert client.post("/api/funcionarios/999/desativar", headers=admin).status_code == 404


def test_eu_mostra_o_funcionario_logado(client, enfermeiro):
    r = client.get("/api/eu", headers=enfermeiro)
    assert r.status_code == 200
    assert r.json()["email"] == "enf@hosp.br" and r.json()["perfil"] == "enfermeiro"


def test_token_expirado_responde_401(client, enfermeiro, relogio):
    from datetime import timedelta

    relogio.agora = relogio.agora + timedelta(hours=9)
    assert client.get("/api/eu", headers=enfermeiro).status_code == 401
