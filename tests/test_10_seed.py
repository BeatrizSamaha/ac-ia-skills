"""Ticket 10 — Dados de demonstração."""
from app.seed import SENHA_DEMO, popular
from tests.conftest import entrar


def test_seed_cria_um_funcionario_por_perfil_e_estoque_de_exemplo(app, client):
    popular(app.state.SessionLocal, app.state.agora().date())
    for email in ("admin@hospital.demo", "farmaceutico@hospital.demo", "enfermeiro@hospital.demo"):
        entrar(client, email, SENHA_DEMO)
    farm = entrar(client, "farmaceutico@hospital.demo", SENHA_DEMO)
    meds = client.get("/api/medicamentos", headers=farm).json()
    assert len(meds) >= 5 and any(m["classe"] == "controlado" for m in meds)
    assert client.get("/api/alertas/reposicao", headers=farm).json()
    assert client.get("/api/alertas/validade", headers=farm).json()


def test_seed_e_idempotente(app, client):
    popular(app.state.SessionLocal, app.state.agora().date())
    popular(app.state.SessionLocal, app.state.agora().date())
    admin = entrar(client, "admin@hospital.demo", SENHA_DEMO)
    assert len(client.get("/api/funcionarios", headers=admin).json()) == 3
