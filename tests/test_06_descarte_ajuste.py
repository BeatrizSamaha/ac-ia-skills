"""Ticket 06 — Descarte e ajuste."""
from tests.helpers import cria_medicamento, entrada, lotes


def _lote(client, admin, farm, qtd=10):
    mid = cria_medicamento(client, admin)
    ent = entrada(client, farm, mid, "L1", qtd)
    return mid, ent["itens"][0]["lote_id"]


def descarte(client, quem, lote_id, quantidade, motivo="Ampola quebrada"):
    return client.post("/api/movimentacoes/descartes", headers=quem,
                       json={"lote_id": lote_id, "quantidade": quantidade, "motivo": motivo})


def ajuste(client, quem, lote_id, nova, motivo="Conferência física"):
    return client.post("/api/movimentacoes/ajustes", headers=quem,
                       json={"lote_id": lote_id, "nova_quantidade": nova, "motivo": motivo})


def test_descarte_remove_unidades_com_motivo(client, admin, farmaceutico):
    mid, lid = _lote(client, admin, farmaceutico)
    r = descarte(client, farmaceutico, lid, 3)
    assert r.status_code == 201 and r.json()["motivo"] == "Ampola quebrada"
    assert lotes(client, farmaceutico, mid) == {"L1": 7}


def test_descarte_sem_motivo_ou_acima_do_lote_e_recusado(client, admin, farmaceutico):
    mid, lid = _lote(client, admin, farmaceutico)
    assert descarte(client, farmaceutico, lid, 1, motivo=" ").status_code == 422
    assert descarte(client, farmaceutico, lid, 11).status_code == 422
    assert descarte(client, farmaceutico, lid, 0).status_code == 422
    assert lotes(client, farmaceutico, mid) == {"L1": 10}


def test_ajuste_define_nova_quantidade_e_registra_diferenca(client, admin, farmaceutico):
    mid, lid = _lote(client, admin, farmaceutico)
    r = ajuste(client, farmaceutico, lid, 8)
    assert r.status_code == 201 and r.json()["itens"][0]["variacao"] == -2
    assert lotes(client, farmaceutico, mid) == {"L1": 8}
    r = ajuste(client, farmaceutico, lid, 12)
    assert r.status_code == 201 and r.json()["itens"][0]["variacao"] == 4
    assert lotes(client, farmaceutico, mid) == {"L1": 12}


def test_ajuste_invalido(client, admin, farmaceutico):
    _, lid = _lote(client, admin, farmaceutico)
    assert ajuste(client, farmaceutico, lid, -1).status_code == 422
    assert ajuste(client, farmaceutico, lid, 10).status_code == 422  # sem diferença
    assert ajuste(client, farmaceutico, lid, 5, motivo="").status_code == 422
    assert ajuste(client, farmaceutico, 999, 5).status_code == 404


def test_so_farmaceutico_descarta_e_ajusta(client, admin, farmaceutico, enfermeiro):
    _, lid = _lote(client, admin, farmaceutico)
    for quem in (admin, enfermeiro):
        assert descarte(client, quem, lid, 1).status_code == 403
        assert ajuste(client, quem, lid, 1).status_code == 403
