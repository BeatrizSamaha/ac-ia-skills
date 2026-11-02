"""Atalhos para montar cenários pela API (a seam combinada)."""
from datetime import date, timedelta

HOJE = date(2026, 11, 2)


def cria_medicamento(client, admin, nome="Dipirona", apresentacao="500 mg comprimido",
                     classe="comum", estoque_minimo=10):
    r = client.post("/api/medicamentos", headers=admin, json={
        "nome": nome, "apresentacao": apresentacao, "classe": classe,
        "estoque_minimo": estoque_minimo})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def entrada(client, farm, medicamento_id, codigo, quantidade, dias_para_vencer=365):
    r = client.post("/api/movimentacoes/entradas", headers=farm, json={
        "medicamento_id": medicamento_id, "codigo_lote": codigo,
        "validade": (HOJE + timedelta(days=dias_para_vencer)).isoformat(),
        "quantidade": quantidade})
    assert r.status_code == 201, r.text
    return r.json()


def estoque(client, quem, medicamento_id):
    r = client.get(f"/api/medicamentos/{medicamento_id}", headers=quem)
    assert r.status_code == 200, r.text
    return r.json()


def lotes(client, quem, medicamento_id):
    return {l["codigo"]: l["quantidade"] for l in estoque(client, quem, medicamento_id)["lotes"]}


def retirada(client, quem, medicamento_id, quantidade, setor="UTI", paciente=None):
    dados = {"medicamento_id": medicamento_id, "quantidade": quantidade, "setor": setor}
    if paciente is not None:
        dados["paciente"] = paciente
    return client.post("/api/movimentacoes/retiradas", headers=quem, json=dados)


def devolucao(client, quem, retirada_id, quantidade):
    return client.post("/api/movimentacoes/devolucoes", headers=quem,
                       json={"retirada_id": retirada_id, "quantidade": quantidade})
