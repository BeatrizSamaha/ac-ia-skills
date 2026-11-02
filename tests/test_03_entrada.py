"""Ticket 03 — Entrada de lote."""
from tests.helpers import HOJE, cria_medicamento, entrada, estoque, lotes


def _post(client, quem, **dados):
    base = {"medicamento_id": 1, "codigo_lote": "L1", "validade": "2027-01-01", "quantidade": 10}
    base.update(dados)
    return client.post("/api/movimentacoes/entradas", headers=quem, json=base)


def test_entrada_cria_lote_e_soma_ao_estoque(client, admin, farmaceutico):
    mid = cria_medicamento(client, admin)
    mov = entrada(client, farmaceutico, mid, "L1", 50)
    assert mov["tipo"] == "entrada" and mov["funcionario"] == "Fábio Farmacêutico"
    assert mov["itens"] == [{"lote_id": mov["itens"][0]["lote_id"], "codigo_lote": "L1", "quantidade": 50}]
    entrada(client, farmaceutico, mid, "L2", 30)
    assert estoque(client, farmaceutico, mid)["estoque_disponivel"] == 80
    assert lotes(client, farmaceutico, mid) == {"L1": 50, "L2": 30}


def test_lote_vencido_e_recusado(client, admin, farmaceutico):
    cria_medicamento(client, admin)
    assert _post(client, farmaceutico, validade="2026-11-01").status_code == 422


def test_lote_que_vence_hoje_e_aceito(client, admin, farmaceutico):
    cria_medicamento(client, admin)
    assert _post(client, farmaceutico, validade=HOJE.isoformat()).status_code == 201


def test_quantidade_nao_positiva_e_recusada(client, admin, farmaceutico):
    cria_medicamento(client, admin)
    assert _post(client, farmaceutico, quantidade=0).status_code == 422
    assert _post(client, farmaceutico, quantidade=-5).status_code == 422


def test_codigo_de_lote_repetido_no_mesmo_medicamento_e_recusado(client, admin, farmaceutico):
    mid = cria_medicamento(client, admin)
    outro = cria_medicamento(client, admin, nome="Paracetamol")
    entrada(client, farmaceutico, mid, "L1", 10)
    assert _post(client, farmaceutico, medicamento_id=mid, codigo_lote="L1").status_code == 409
    assert _post(client, farmaceutico, medicamento_id=outro, codigo_lote="L1").status_code == 201


def test_medicamento_inexistente(client, farmaceutico):
    assert _post(client, farmaceutico, medicamento_id=999).status_code == 404


def test_so_farmaceutico_registra_entrada(client, admin, enfermeiro):
    cria_medicamento(client, admin)
    assert _post(client, admin).status_code == 403
    assert _post(client, enfermeiro).status_code == 403
