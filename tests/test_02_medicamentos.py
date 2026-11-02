"""Ticket 02 — Cadastro de medicamentos e consulta de estoque."""
from tests.helpers import cria_medicamento, estoque


def test_admin_cadastra_medicamento(client, admin):
    mid = cria_medicamento(client, admin, classe="controlado", estoque_minimo=5)
    m = estoque(client, admin, mid)
    assert m["nome"] == "Dipirona" and m["classe"] == "controlado"
    assert m["estoque_minimo"] == 5 and m["estoque_disponivel"] == 0 and m["lotes"] == []


def test_medicamento_duplicado_e_recusado(client, admin):
    cria_medicamento(client, admin)
    r = client.post("/api/medicamentos", headers=admin, json={
        "nome": "dipirona ", "apresentacao": "500 mg comprimido", "classe": "comum",
        "estoque_minimo": 1})
    assert r.status_code == 409


def test_mesmo_nome_com_outra_apresentacao_e_permitido(client, admin):
    cria_medicamento(client, admin)
    cria_medicamento(client, admin, apresentacao="1 g/2 mL injetável")


def test_estoque_minimo_negativo_e_recusado(client, admin):
    r = client.post("/api/medicamentos", headers=admin, json={
        "nome": "X", "apresentacao": "Y", "classe": "comum", "estoque_minimo": -1})
    assert r.status_code == 422


def test_so_admin_cadastra_e_altera(client, admin, farmaceutico, enfermeiro):
    mid = cria_medicamento(client, admin)
    for quem in (farmaceutico, enfermeiro):
        r = client.post("/api/medicamentos", headers=quem, json={
            "nome": "X", "apresentacao": "Y", "classe": "comum", "estoque_minimo": 1})
        assert r.status_code == 403
        r = client.patch(f"/api/medicamentos/{mid}", headers=quem, json={"estoque_minimo": 3})
        assert r.status_code == 403


def test_admin_altera_estoque_minimo(client, admin):
    mid = cria_medicamento(client, admin)
    r = client.patch(f"/api/medicamentos/{mid}", headers=admin, json={"estoque_minimo": 42})
    assert r.status_code == 200 and r.json()["estoque_minimo"] == 42


def test_qualquer_funcionario_consulta_lista(client, admin, enfermeiro):
    cria_medicamento(client, admin)
    r = client.get("/api/medicamentos", headers=enfermeiro)
    assert r.status_code == 200 and [m["nome"] for m in r.json()] == ["Dipirona"]


def test_medicamento_inexistente_responde_404(client, enfermeiro):
    assert client.get("/api/medicamentos/999", headers=enfermeiro).status_code == 404
