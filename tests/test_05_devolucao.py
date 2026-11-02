"""Ticket 05 — Devolução."""
from datetime import timedelta

from tests.conftest import entrar
from tests.helpers import cria_medicamento, devolucao, entrada, lotes, retirada


def _retirada_de_dois_lotes(client, admin, farm, enf):
    mid = cria_medicamento(client, admin)
    entrada(client, farm, mid, "A", 4, dias_para_vencer=10)
    entrada(client, farm, mid, "B", 20, dias_para_vencer=200)
    ret = retirada(client, enf, mid, 10).json()  # A:4, B:6
    return mid, ret["id"]


def test_devolucao_volta_ao_mesmo_lote(client, admin, farmaceutico, enfermeiro):
    mid, rid = _retirada_de_dois_lotes(client, admin, farmaceutico, enfermeiro)
    r = devolucao(client, enfermeiro, rid, 3)
    assert r.status_code == 201, r.text
    assert r.json()["tipo"] == "devolucao" and r.json()["retirada_origem_id"] == rid
    # devolve primeiro ao último lote consumido (B), que vence depois
    assert lotes(client, enfermeiro, mid) == {"A": 0, "B": 17}


def test_devolucao_pode_atravessar_lotes(client, admin, farmaceutico, enfermeiro):
    mid, rid = _retirada_de_dois_lotes(client, admin, farmaceutico, enfermeiro)
    assert devolucao(client, enfermeiro, rid, 8).status_code == 201
    assert lotes(client, enfermeiro, mid) == {"A": 2, "B": 20}


def test_nao_devolve_mais_que_o_retirado_somando_devolucoes_anteriores(client, admin, farmaceutico, enfermeiro):
    mid, rid = _retirada_de_dois_lotes(client, admin, farmaceutico, enfermeiro)
    assert devolucao(client, enfermeiro, rid, 11).status_code == 422
    assert devolucao(client, enfermeiro, rid, 7).status_code == 201
    assert devolucao(client, enfermeiro, rid, 4).status_code == 422
    assert devolucao(client, enfermeiro, rid, 3).status_code == 201
    assert lotes(client, enfermeiro, mid) == {"A": 4, "B": 20}


def test_nao_devolve_para_lote_vencido(client, admin, farmaceutico, enfermeiro, relogio):
    mid, rid = _retirada_de_dois_lotes(client, admin, farmaceutico, enfermeiro)
    relogio.agora += timedelta(days=11)  # lote A venceu
    enfermeiro = entrar(client, "enf@hosp.br")
    assert devolucao(client, enfermeiro, rid, 7).status_code == 422  # só cabem 6 em B
    assert devolucao(client, enfermeiro, rid, 6).status_code == 201
    assert lotes(client, enfermeiro, mid) == {"A": 0, "B": 20}


def test_enfermeiro_so_devolve_retirada_propria(client, admin, farmaceutico, enfermeiro, enfermeiro2):
    _, rid = _retirada_de_dois_lotes(client, admin, farmaceutico, enfermeiro)
    assert devolucao(client, enfermeiro2, rid, 1).status_code == 403
    assert devolucao(client, farmaceutico, rid, 1).status_code == 201


def test_so_retirada_pode_ser_devolvida(client, admin, farmaceutico, enfermeiro):
    mid = cria_medicamento(client, admin)
    ent = entrada(client, farmaceutico, mid, "A", 5)
    assert devolucao(client, farmaceutico, ent["id"], 1).status_code == 422
    assert devolucao(client, farmaceutico, 999, 1).status_code == 404


def test_quantidade_nao_positiva(client, admin, farmaceutico, enfermeiro):
    _, rid = _retirada_de_dois_lotes(client, admin, farmaceutico, enfermeiro)
    assert devolucao(client, enfermeiro, rid, 0).status_code == 422


def test_administrador_nao_devolve(client, admin, farmaceutico, enfermeiro):
    _, rid = _retirada_de_dois_lotes(client, admin, farmaceutico, enfermeiro)
    assert devolucao(client, admin, rid, 1).status_code == 403
