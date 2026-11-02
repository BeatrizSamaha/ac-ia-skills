"""Módulo Estoque: medicamentos, lotes e estoque disponível."""
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.erros import Conflito, NaoEncontrado, RegraViolada
from app.models import ClasseControle, Lote, Medicamento


def _valida_minimo(estoque_minimo: int) -> None:
    if estoque_minimo < 0:
        raise RegraViolada("O estoque mínimo não pode ser negativo.")


def criar_medicamento(
    s: Session, *, nome: str, apresentacao: str, classe: ClasseControle, estoque_minimo: int
) -> Medicamento:
    nome, apresentacao = nome.strip(), apresentacao.strip()
    if not nome or not apresentacao:
        raise RegraViolada("Nome e apresentação são obrigatórios.")
    _valida_minimo(estoque_minimo)
    existente = s.scalar(
        select(Medicamento).where(
            func.lower(Medicamento.nome) == nome.lower(),
            func.lower(Medicamento.apresentacao) == apresentacao.lower(),
        )
    )
    if existente:
        raise Conflito("Já existe medicamento com este nome e apresentação.")
    m = Medicamento(nome=nome, apresentacao=apresentacao, classe=classe, estoque_minimo=estoque_minimo)
    s.add(m)
    s.commit()
    return m


def obter_medicamento(s: Session, medicamento_id: int) -> Medicamento:
    m = s.get(Medicamento, medicamento_id)
    if not m:
        raise NaoEncontrado("Medicamento não encontrado.")
    return m


def alterar_estoque_minimo(s: Session, medicamento_id: int, estoque_minimo: int) -> Medicamento:
    _valida_minimo(estoque_minimo)
    m = obter_medicamento(s, medicamento_id)
    m.estoque_minimo = estoque_minimo
    s.commit()
    return m


def listar_medicamentos(s: Session) -> list[Medicamento]:
    return list(s.scalars(select(Medicamento).order_by(Medicamento.nome, Medicamento.apresentacao)))


def lote_vencido(lote: Lote, hoje: date) -> bool:
    return lote.validade < hoje


def lotes_validos_fefo(s: Session, medicamento_id: int, hoje: date) -> list[Lote]:
    """Lotes não vencidos com unidades, do que vence primeiro ao último (ADR 0002)."""
    return list(
        s.scalars(
            select(Lote)
            .where(Lote.medicamento_id == medicamento_id, Lote.validade >= hoje, Lote.quantidade > 0)
            .order_by(Lote.validade, Lote.id)
        )
    )


def estoque_disponivel(s: Session, medicamento_id: int, hoje: date) -> int:
    return sum(l.quantidade for l in lotes_validos_fefo(s, medicamento_id, hoje))


def lotes_do_medicamento(s: Session, medicamento_id: int) -> list[Lote]:
    return list(
        s.scalars(select(Lote).where(Lote.medicamento_id == medicamento_id).order_by(Lote.validade, Lote.id))
    )
