"""Módulo Movimentações: toda alteração de quantidade de lote passa por aqui.

Cada operação grava a Movimentação imutável e atualiza o Lote na mesma transação (ADR 0003).
"""
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.erros import Conflito, NaoEncontrado, Proibido, RegraViolada
from app.estoque.servico import lotes_validos_fefo, obter_medicamento
from app.models import ClasseControle, Funcionario, ItemMovimentacao, Lote, Movimentacao, Perfil, TipoMovimentacao


def _quantidade_positiva(quantidade: int) -> None:
    if quantidade <= 0:
        raise RegraViolada("A quantidade deve ser maior que zero.")


def _registra(s: Session, mov: Movimentacao, itens: list[tuple[Lote, int]]) -> Movimentacao:
    for lote, delta in itens:
        lote.quantidade += delta
        mov.itens.append(ItemMovimentacao(lote=lote, quantidade=delta))
    s.add(mov)
    try:
        s.commit()
    except IntegrityError:
        s.rollback()
        raise Conflito("Conflito ao gravar a movimentação.")
    return mov


def registrar_entrada(
    s: Session, *, funcionario: Funcionario, agora: datetime, medicamento_id: int,
    codigo_lote: str, validade: date, quantidade: int,
) -> Movimentacao:
    medicamento = obter_medicamento(s, medicamento_id)
    _quantidade_positiva(quantidade)
    codigo_lote = codigo_lote.strip()
    if not codigo_lote:
        raise RegraViolada("O código do lote é obrigatório.")
    if validade < agora.date():
        raise RegraViolada("Não é possível dar entrada em lote vencido.")
    if s.scalar(select(Lote).where(Lote.medicamento_id == medicamento.id, Lote.codigo == codigo_lote)):
        raise Conflito("Este lote já foi registrado para este medicamento.")
    lote = Lote(medicamento=medicamento, codigo=codigo_lote, validade=validade, quantidade=0)
    s.add(lote)
    mov = Movimentacao(tipo=TipoMovimentacao.ENTRADA, medicamento=medicamento,
                       funcionario=funcionario, data_hora=agora)
    return _registra(s, mov, [(lote, quantidade)])


def registrar_retirada(
    s: Session, *, funcionario: Funcionario, agora: datetime, medicamento_id: int,
    quantidade: int, setor: str, paciente: str | None = None,
) -> Movimentacao:
    medicamento = obter_medicamento(s, medicamento_id)
    _quantidade_positiva(quantidade)
    setor = (setor or "").strip()
    if not setor:
        raise RegraViolada("Informe o setor de destino.")
    paciente = (paciente or "").strip() or None
    if medicamento.classe == ClasseControle.CONTROLADO:
        if funcionario.perfil != Perfil.FARMACEUTICO:
            raise Proibido("Medicamento controlado só pode ser retirado por farmacêutico.")
        if not paciente:
            raise RegraViolada("Retirada de medicamento controlado exige o paciente.")

    lotes = lotes_validos_fefo(s, medicamento.id, agora.date())
    disponivel = sum(l.quantidade for l in lotes)
    if quantidade > disponivel:
        raise RegraViolada(
            f"Estoque disponível insuficiente: pedido {quantidade}, disponível {disponivel}."
        )

    itens: list[tuple[Lote, int]] = []
    falta = quantidade
    for lote in lotes:  # FEFO (ADR 0002)
        usado = min(falta, lote.quantidade)
        itens.append((lote, -usado))
        falta -= usado
        if falta == 0:
            break

    mov = Movimentacao(tipo=TipoMovimentacao.RETIRADA, medicamento=medicamento,
                       funcionario=funcionario, data_hora=agora, setor=setor, paciente=paciente)
    return _registra(s, mov, itens)


def _obter_movimentacao(s: Session, movimentacao_id: int) -> Movimentacao:
    mov = s.get(Movimentacao, movimentacao_id)
    if not mov:
        raise NaoEncontrado("Movimentação não encontrada.")
    return mov


def registrar_devolucao(
    s: Session, *, funcionario: Funcionario, agora: datetime, retirada_id: int, quantidade: int,
) -> Movimentacao:
    ret = _obter_movimentacao(s, retirada_id)
    if ret.tipo != TipoMovimentacao.RETIRADA:
        raise RegraViolada("Só é possível devolver uma retirada.")
    if funcionario.perfil == Perfil.ENFERMEIRO and ret.funcionario_id != funcionario.id:
        raise Proibido("Enfermeiro só pode devolver as próprias retiradas.")
    _quantidade_positiva(quantidade)

    devolvido: dict[int, int] = {}
    for dev in s.scalars(select(Movimentacao).where(Movimentacao.retirada_origem_id == ret.id)):
        for item in dev.itens:
            devolvido[item.lote_id] = devolvido.get(item.lote_id, 0) + item.quantidade

    # Devolve primeiro ao último lote consumido (o que vence depois), nunca a lote vencido.
    hoje = agora.date()
    capacidade: list[tuple[Lote, int]] = []
    for item in reversed(ret.itens):
        resta = -item.quantidade - devolvido.get(item.lote_id, 0)
        if resta > 0 and not item.lote.validade < hoje:
            capacidade.append((item.lote, resta))
    cabe = sum(c for _, c in capacidade)
    if quantidade > cabe:
        raise RegraViolada(
            f"Quantidade acima do que pode ser devolvido desta retirada: máximo {cabe} "
            "(descontadas devoluções anteriores e lotes vencidos)."
        )

    itens: list[tuple[Lote, int]] = []
    falta = quantidade
    for lote, c in capacidade:
        usado = min(falta, c)
        itens.append((lote, usado))
        falta -= usado
        if falta == 0:
            break
    mov = Movimentacao(tipo=TipoMovimentacao.DEVOLUCAO, medicamento_id=ret.medicamento_id,
                       funcionario=funcionario, data_hora=agora, setor=ret.setor,
                       paciente=ret.paciente, retirada_origem_id=ret.id)
    return _registra(s, mov, itens)


def _obter_lote(s: Session, lote_id: int) -> Lote:
    lote = s.get(Lote, lote_id)
    if not lote:
        raise NaoEncontrado("Lote não encontrado.")
    return lote


def _motivo(motivo: str) -> str:
    motivo = (motivo or "").strip()
    if not motivo:
        raise RegraViolada("Informe o motivo.")
    return motivo


def registrar_descarte(
    s: Session, *, funcionario: Funcionario, agora: datetime, lote_id: int, quantidade: int, motivo: str,
) -> Movimentacao:
    lote = _obter_lote(s, lote_id)
    motivo = _motivo(motivo)
    _quantidade_positiva(quantidade)
    if quantidade > lote.quantidade:
        raise RegraViolada(f"O lote tem apenas {lote.quantidade} unidade(s).")
    mov = Movimentacao(tipo=TipoMovimentacao.DESCARTE, medicamento_id=lote.medicamento_id,
                       funcionario=funcionario, data_hora=agora, motivo=motivo)
    return _registra(s, mov, [(lote, -quantidade)])


def registrar_ajuste(
    s: Session, *, funcionario: Funcionario, agora: datetime, lote_id: int, nova_quantidade: int, motivo: str,
) -> Movimentacao:
    lote = _obter_lote(s, lote_id)
    motivo = _motivo(motivo)
    if nova_quantidade < 0:
        raise RegraViolada("A quantidade não pode ser negativa.")
    delta = nova_quantidade - lote.quantidade
    if delta == 0:
        raise RegraViolada("A nova quantidade é igual à atual; nada a ajustar.")
    mov = Movimentacao(tipo=TipoMovimentacao.AJUSTE, medicamento_id=lote.medicamento_id,
                       funcionario=funcionario, data_hora=agora, motivo=motivo)
    return _registra(s, mov, [(lote, delta)])
