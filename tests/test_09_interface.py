"""Ticket 09 — Interface web e rota de apoio (retiradas visíveis para devolução)."""
from tests.helpers import cria_medicamento, devolucao, entrada, retirada


def test_pagina_inicial_e_servida(client):
    r = client.get("/")
    assert r.status_code == 200 and "Controle de Medicamentos" in r.text


def test_enfermeiro_ve_so_as_proprias_retiradas_e_quanto_pode_devolver(
        client, admin, farmaceutico, enfermeiro, enfermeiro2):
    mid = cria_medicamento(client, admin)
    entrada(client, farmaceutico, mid, "L1", 50)
    r1 = retirada(client, enfermeiro, mid, 5).json()["id"]
    retirada(client, enfermeiro2, mid, 2)
    devolucao(client, enfermeiro, r1, 2)

    minhas = client.get("/api/movimentacoes/retiradas", headers=enfermeiro).json()
    assert [(m["id"], m["quantidade"], m["devolvivel"]) for m in minhas] == [(r1, 5, 3)]
    todas = client.get("/api/movimentacoes/retiradas", headers=farmaceutico).json()
    assert len(todas) == 2


def test_admin_nao_lista_retiradas(client, admin):
    assert client.get("/api/movimentacoes/retiradas", headers=admin).status_code == 403
