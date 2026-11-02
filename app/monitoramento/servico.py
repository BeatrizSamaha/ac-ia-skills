"""Módulo Monitoramento: alertas e trilha de auditoria (somente leitura)."""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.estoque.servico import estoque_disponivel, listar_medicamentos
from app.models import Lote, Movimentacao, TipoMovimentacao

JANELA_VALIDADE = timedelta(days=30)


@dataclass
class AlertaReposicao:
    medicamento_id: int
    medicamento: str
    estoque_disponivel: int
    estoque_minimo: int
    faltam: int


@dataclass
class AlertaValidade:
    lote_id: int
    codigo_lote: str
    medicamento_id: int
    medicamento: str
    validade: date
    quantidade: int
    dias_para_vencer: int
    vencido: bool


def alertas_de_reposicao(s: Session, hoje: date) -> list[AlertaReposicao]:
    alertas = []
    for m in listar_medicamentos(s):
        disponivel = estoque_disponivel(s, m.id, hoje)
        if disponivel < m.estoque_minimo:
            alertas.append(AlertaReposicao(m.id, f"{m.nome} {m.apresentacao}", disponivel,
                                           m.estoque_minimo, m.estoque_minimo - disponivel))
    return alertas


def alertas_de_validade(s: Session, hoje: date) -> list[AlertaValidade]:
    lotes = s.scalars(
        select(Lote)
        .where(Lote.quantidade > 0, Lote.validade <= hoje + JANELA_VALIDADE)
        .order_by(Lote.validade, Lote.id)
    )
    return [
        AlertaValidade(l.id, l.codigo, l.medicamento_id,
                       f"{l.medicamento.nome} {l.medicamento.apresentacao}", l.validade,
                       l.quantidade, (l.validade - hoje).days, l.validade < hoje)
        for l in lotes
    ]


def trilha_de_auditoria(
    s: Session, *, medicamento_id: int | None = None, funcionario_id: int | None = None,
    tipo: TipoMovimentacao | None = None, inicio: date | None = None, fim: date | None = None,
) -> list[Movimentacao]:
    q = select(Movimentacao)
    if medicamento_id is not None:
        q = q.where(Movimentacao.medicamento_id == medicamento_id)
    if funcionario_id is not None:
        q = q.where(Movimentacao.funcionario_id == funcionario_id)
    if tipo is not None:
        q = q.where(Movimentacao.tipo == tipo)
    if inicio is not None:
        q = q.where(Movimentacao.data_hora >= datetime.combine(inicio, time.min))
    if fim is not None:
        q = q.where(Movimentacao.data_hora < datetime.combine(fim + timedelta(days=1), time.min))
    return list(s.scalars(q.order_by(Movimentacao.data_hora.desc(), Movimentacao.id.desc())))
