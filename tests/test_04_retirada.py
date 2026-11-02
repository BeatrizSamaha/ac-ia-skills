"""Ticket 04 — Retirada FEFO com regras de medicamentos controlados."""
from tests.conftest import entrar
from tests.helpers import cria_medicamento, entrada, estoque, lotes, retirada


def _cenario_dois_lotes(client, admin, farm):
    mid = cria_medicamento(client, admin)
    entrada(client, farm, mid, "VENCE-DEPOIS", 20, dias_para_vencer=200)
    entrada(client, farm, mid, "VENCE-ANTES", 4, dias_para_vencer=30)
    return mid


def test_retirada_consome_primeiro_o_lote_que_vence_primeiro(client, admin, farmaceutico, enfermeiro):
    mid = _cenario_dois_lotes(client, admin, farmaceutico)
    r = retirada(client, enfermeiro, mid, 3)
    assert r.status_code == 201, r.text
    assert lotes(client, enfermeiro, mid) == {"VENCE-ANTES": 1, "VENCE-DEPOIS": 20}


def test_retirada_atravessa_varios_lotes(client, admin, farmaceutico, enfermeiro):
    mid = _cenario_dois_lotes(client, admin, farmaceutico)
    r = retirada(client, enfermeiro, mid, 10)
    assert r.status_code == 201
    itens = {i["codigo_lote"]: i["quantidade"] for i in r.json()["itens"]}
    assert itens == {"VENCE-ANTES": 4, "VENCE-DEPOIS": 6}
    assert lotes(client, enfermeiro, mid) == {"VENCE-ANTES": 0, "VENCE-DEPOIS": 14}


def test_retirada_registra_quem_quando_e_setor(client, admin, farmaceutico, enfermeiro):
    mid = _cenario_dois_lotes(client, admin, farmaceutico)
    mov = retirada(client, enfermeiro, mid, 2, setor="Pronto-Socorro").json()
    assert mov["tipo"] == "retirada" and mov["funcionario"] == "Elisa Enfermeira"
    assert mov["setor"] == "Pronto-Socorro" and mov["data_hora"].startswith("2026-11-02")


def test_quantidade_maior_que_o_disponivel_e_recusada_sem_alterar_nada(client, admin, farmaceutico, enfermeiro):
    mid = _cenario_dois_lotes(client, admin, farmaceutico)
    r = retirada(client, enfermeiro, mid, 25)
    assert r.status_code == 422
    assert "24" in r.json()["detail"]
    assert lotes(client, enfermeiro, mid) == {"VENCE-ANTES": 4, "VENCE-DEPOIS": 20}


def test_lote_vencido_nunca_e_usado(client, admin, farmaceutico, enfermeiro, relogio):
    from datetime import timedelta

    mid = _cenario_dois_lotes(client, admin, farmaceutico)
    relogio.agora += timedelta(days=31)  # VENCE-ANTES venceu
    enfermeiro = entrar(client, "enf@hosp.br")  # o token antigo expirou
    assert estoque(client, enfermeiro, mid)["estoque_disponivel"] == 20
    assert retirada(client, enfermeiro, mid, 21).status_code == 422
    assert retirada(client, enfermeiro, mid, 5).status_code == 201
    assert lotes(client, enfermeiro, mid) == {"VENCE-ANTES": 4, "VENCE-DEPOIS": 15}


def test_quantidade_nao_positiva_e_setor_obrigatorio(client, admin, farmaceutico, enfermeiro):
    mid = _cenario_dois_lotes(client, admin, farmaceutico)
    assert retirada(client, enfermeiro, mid, 0).status_code == 422
    assert retirada(client, enfermeiro, mid, 1, setor="  ").status_code == 422


def test_enfermeiro_nao_retira_controlado(client, admin, farmaceutico, enfermeiro):
    mid = cria_medicamento(client, admin, nome="Morfina", apresentacao="10 mg/mL", classe="controlado")
    entrada(client, farmaceutico, mid, "M1", 10)
    assert retirada(client, enfermeiro, mid, 1, paciente="Paciente 123").status_code == 403


def test_controlado_exige_paciente(client, admin, farmaceutico):
    mid = cria_medicamento(client, admin, nome="Morfina", apresentacao="10 mg/mL", classe="controlado")
    entrada(client, farmaceutico, mid, "M1", 10)
    assert retirada(client, farmaceutico, mid, 1).status_code == 422
    r = retirada(client, farmaceutico, mid, 1, paciente="Paciente 123")
    assert r.status_code == 201 and r.json()["paciente"] == "Paciente 123"


def test_paciente_e_opcional_para_comum(client, admin, farmaceutico, enfermeiro):
    mid = _cenario_dois_lotes(client, admin, farmaceutico)
    assert retirada(client, enfermeiro, mid, 1).json()["paciente"] is None
    assert retirada(client, enfermeiro, mid, 1, paciente="P9").json()["paciente"] == "P9"


def test_administrador_nao_movimenta_estoque(client, admin, farmaceutico):
    mid = _cenario_dois_lotes(client, admin, farmaceutico)
    assert retirada(client, admin, mid, 1).status_code == 403


def test_medicamento_inexistente(client, enfermeiro):
    assert retirada(client, enfermeiro, 999, 1).status_code == 404
