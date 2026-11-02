"""Ticket 08 — Trilha de auditoria."""
from tests.helpers import cria_medicamento, devolucao, entrada, retirada


def _historico(client, admin, farm, enf):
    dip = cria_medicamento(client, admin)
    par = cria_medicamento(client, admin, nome="Paracetamol")
    entrada(client, farm, dip, "D1", 20)
    entrada(client, farm, par, "P1", 20)
    rid = retirada(client, enf, dip, 5).json()["id"]
    retirada(client, farm, par, 2)
    devolucao(client, enf, rid, 1)
    return dip, par


def test_auditoria_lista_todas_as_movimentacoes_mais_recentes_primeiro(client, admin, farmaceutico, enfermeiro):
    _historico(client, admin, farmaceutico, enfermeiro)
    movs = client.get("/api/auditoria", headers=farmaceutico).json()
    assert [m["tipo"] for m in movs] == ["devolucao", "retirada", "retirada", "entrada", "entrada"]
    assert all(m["funcionario"] and m["data_hora"] and m["itens"] for m in movs)


def test_filtros_combinaveis(client, admin, farmaceutico, enfermeiro):
    dip, _ = _historico(client, admin, farmaceutico, enfermeiro)
    enf_id = client.get("/api/eu", headers=enfermeiro).json()["id"]
    r = client.get("/api/auditoria", headers=farmaceutico,
                   params={"medicamento_id": dip, "funcionario_id": enf_id, "tipo": "retirada"})
    assert [(m["tipo"], m["funcionario"]) for m in r.json()] == [("retirada", "Elisa Enfermeira")]


def test_filtro_por_periodo(client, admin, farmaceutico, enfermeiro):
    _historico(client, admin, farmaceutico, enfermeiro)
    dentro = client.get("/api/auditoria", headers=farmaceutico,
                        params={"inicio": "2026-11-02", "fim": "2026-11-02"}).json()
    fora = client.get("/api/auditoria", headers=farmaceutico,
                      params={"inicio": "2026-11-03"}).json()
    assert len(dentro) == 5 and fora == []


def test_movimentacoes_nao_podem_ser_editadas_nem_apagadas(client, app):
    rotas = {(m, r.path) for r in app.routes for m in getattr(r, "methods", set())}
    assert not any(p.startswith(("/api/movimentacoes", "/api/auditoria"))
                   for m, p in rotas if m in {"PUT", "PATCH", "DELETE"})


def test_so_farmaceutico_consulta_auditoria(client, admin, enfermeiro):
    assert client.get("/api/auditoria", headers=enfermeiro).status_code == 403
    assert client.get("/api/auditoria", headers=admin).status_code == 403
