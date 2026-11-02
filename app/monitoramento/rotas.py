from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.acesso.dependencias import exige
from app.db import get_session
from app.models import Funcionario, Perfil, TipoMovimentacao
from app.monitoramento import servico
from app.movimentacoes.rotas import MovimentacaoOut, saida
from app.relogio import hoje

router = APIRouter(tags=["Monitoramento"])
somente_farmaceutico = exige(Perfil.FARMACEUTICO)


@router.get("/alertas/reposicao", response_model=list[servico.AlertaReposicao])
def reposicao(_: Funcionario = Depends(somente_farmaceutico), s: Session = Depends(get_session),
              dia: date = Depends(hoje)):
    return servico.alertas_de_reposicao(s, dia)


@router.get("/alertas/validade", response_model=list[servico.AlertaValidade])
def validade(_: Funcionario = Depends(somente_farmaceutico), s: Session = Depends(get_session),
             dia: date = Depends(hoje)):
    return servico.alertas_de_validade(s, dia)


@router.get("/auditoria", response_model=list[MovimentacaoOut])
def auditoria(
    medicamento_id: int | None = None, funcionario_id: int | None = None,
    tipo: TipoMovimentacao | None = None, inicio: date | None = None, fim: date | None = None,
    _: Funcionario = Depends(somente_farmaceutico), s: Session = Depends(get_session),
):
    movs = servico.trilha_de_auditoria(s, medicamento_id=medicamento_id, funcionario_id=funcionario_id,
                                       tipo=tipo, inicio=inicio, fim=fim)
    return [saida(m) for m in movs]
