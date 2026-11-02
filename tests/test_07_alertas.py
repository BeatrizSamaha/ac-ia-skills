"""Ticket 07 — Alertas de reposição e de validade."""
from datetime import timedelta

from tests.conftest import entrar
from tests.helpers import cria_medicamento, entrada, retirada


def test_alerta_de_reposicao_quando_disponivel_fica_abaixo_do_minimo(client, admin, farmaceutico, enfermeiro):
    mid = cria_medicamento(client, admin, estoque_minimo=10)
    cria_medicamento(client, admin, nome="Sem estoque", estoque_minimo=0)
    entrada(client, farmaceutico, mid, "L1", 12)
    assert client.get("/api/alertas/reposicao", headers=farmaceutico).json() == []

    retirada(client, enfermeiro, mid, 3)
    alertas = client.get("/api/alertas/reposicao", headers=farmaceutico).json()
    assert alertas == [{"medicamento_id": mid, "medicamento": "Dipirona 500 mg comprimido",
                        "estoque_disponivel": 9, "estoque_minimo": 10, "faltam": 1}]


def test_reposicao_ignora_lotes_vencidos(client, admin, farmaceutico, relogio):
    mid = cria_medicamento(client, admin, estoque_minimo=5)
    entrada(client, farmaceutico, mid, "CURTO", 50, dias_para_vencer=5)
    entrada(client, farmaceutico, mid, "LONGO", 3, dias_para_vencer=300)
    assert client.get("/api/alertas/reposicao", headers=farmaceutico).json() == []
    relogio.agora += timedelta(days=6)
    farmaceutico = entrar(client, "farm@hosp.br")
    [alerta] = client.get("/api/alertas/reposicao", headers=farmaceutico).json()
    assert alerta["estoque_disponivel"] == 3


def test_alerta_de_validade_lista_lotes_que_vencem_em_ate_30_dias(client, admin, farmaceutico, enfermeiro):
    mid = cria_medicamento(client, admin)
    entrada(client, farmaceutico, mid, "D30", 5, dias_para_vencer=30)
    entrada(client, farmaceutico, mid, "D10", 5, dias_para_vencer=10)
    entrada(client, farmaceutico, mid, "D31", 5, dias_para_vencer=31)
    entrada(client, farmaceutico, mid, "ZERADO", 2, dias_para_vencer=1)
    retirada(client, enfermeiro, mid, 2)  # consome o lote ZERADO (FEFO)
    alertas = client.get("/api/alertas/validade", headers=farmaceutico).json()
    assert [(a["codigo_lote"], a["dias_para_vencer"]) for a in alertas] == [("D10", 10), ("D30", 30)]


def test_alerta_de_validade_inclui_lotes_ja_vencidos_com_unidades(client, admin, farmaceutico, relogio):
    mid = cria_medicamento(client, admin)
    entrada(client, farmaceutico, mid, "V", 5, dias_para_vencer=2)
    relogio.agora += timedelta(days=3)
    farmaceutico = entrar(client, "farm@hosp.br")
    [a] = client.get("/api/alertas/validade", headers=farmaceutico).json()
    assert a["codigo_lote"] == "V" and a["vencido"] is True and a["dias_para_vencer"] == -1


def test_so_farmaceutico_ve_alertas(client, admin, enfermeiro):
    for quem in (admin, enfermeiro):
        assert client.get("/api/alertas/reposicao", headers=quem).status_code == 403
        assert client.get("/api/alertas/validade", headers=quem).status_code == 403
