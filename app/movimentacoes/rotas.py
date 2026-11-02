from datetime import date, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.acesso.dependencias import exige
from app.db import get_session
from app.models import Funcionario, Movimentacao, Perfil, TipoMovimentacao
from app.movimentacoes import servico
from app.relogio import agora

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])


class EntradaIn(BaseModel):
    medicamento_id: int
    codigo_lote: str
    validade: date
    quantidade: int


class ItemOut(BaseModel):
    lote_id: int
    codigo_lote: str
    quantidade: int  # unidades movidas (sempre positiva)
    variacao: int  # efeito no lote: + aumentou, - diminuiu


class MovimentacaoOut(BaseModel):
    id: int
    tipo: TipoMovimentacao
    medicamento_id: int
    medicamento: str
    funcionario_id: int
    funcionario: str
    data_hora: datetime
    setor: str | None
    paciente: str | None
    motivo: str | None
    retirada_origem_id: int | None
    itens: list[ItemOut]


def saida(m: Movimentacao) -> MovimentacaoOut:
    return MovimentacaoOut(
        id=m.id, tipo=m.tipo, medicamento_id=m.medicamento_id,
        medicamento=f"{m.medicamento.nome} {m.medicamento.apresentacao}",
        funcionario_id=m.funcionario_id, funcionario=m.funcionario.nome,
        data_hora=m.data_hora, setor=m.setor, paciente=m.paciente, motivo=m.motivo,
        retirada_origem_id=m.retirada_origem_id,
        itens=[ItemOut(lote_id=i.lote_id, codigo_lote=i.lote.codigo, quantidade=abs(i.quantidade),
                       variacao=i.quantidade)
               for i in m.itens],
    )


@router.post("/entradas", response_model=MovimentacaoOut, status_code=201)
def entrada(dados: EntradaIn, f: Funcionario = Depends(exige(Perfil.FARMACEUTICO)),
            s: Session = Depends(get_session), momento: datetime = Depends(agora)):
    return saida(servico.registrar_entrada(
        s, funcionario=f, agora=momento, medicamento_id=dados.medicamento_id,
        codigo_lote=dados.codigo_lote, validade=dados.validade, quantidade=dados.quantidade))


class RetiradaIn(BaseModel):
    medicamento_id: int
    quantidade: int
    setor: str
    paciente: str | None = None


@router.post("/retiradas", response_model=MovimentacaoOut, status_code=201)
def retirada(dados: RetiradaIn,
             f: Funcionario = Depends(exige(Perfil.FARMACEUTICO, Perfil.ENFERMEIRO)),
             s: Session = Depends(get_session), momento: datetime = Depends(agora)):
    return saida(servico.registrar_retirada(
        s, funcionario=f, agora=momento, medicamento_id=dados.medicamento_id,
        quantidade=dados.quantidade, setor=dados.setor, paciente=dados.paciente))


class DevolucaoIn(BaseModel):
    retirada_id: int
    quantidade: int


@router.post("/devolucoes", response_model=MovimentacaoOut, status_code=201)
def devolucao(dados: DevolucaoIn,
              f: Funcionario = Depends(exige(Perfil.FARMACEUTICO, Perfil.ENFERMEIRO)),
              s: Session = Depends(get_session), momento: datetime = Depends(agora)):
    return saida(servico.registrar_devolucao(
        s, funcionario=f, agora=momento, retirada_id=dados.retirada_id, quantidade=dados.quantidade))


class DescarteIn(BaseModel):
    lote_id: int
    quantidade: int
    motivo: str


class AjusteIn(BaseModel):
    lote_id: int
    nova_quantidade: int
    motivo: str


@router.post("/descartes", response_model=MovimentacaoOut, status_code=201)
def descarte(dados: DescarteIn, f: Funcionario = Depends(exige(Perfil.FARMACEUTICO)),
             s: Session = Depends(get_session), momento: datetime = Depends(agora)):
    return saida(servico.registrar_descarte(
        s, funcionario=f, agora=momento, lote_id=dados.lote_id, quantidade=dados.quantidade,
        motivo=dados.motivo))


@router.post("/ajustes", response_model=MovimentacaoOut, status_code=201)
def ajuste(dados: AjusteIn, f: Funcionario = Depends(exige(Perfil.FARMACEUTICO)),
           s: Session = Depends(get_session), momento: datetime = Depends(agora)):
    return saida(servico.registrar_ajuste(
        s, funcionario=f, agora=momento, lote_id=dados.lote_id,
        nova_quantidade=dados.nova_quantidade, motivo=dados.motivo))


class RetiradaResumo(MovimentacaoOut):
    quantidade: int
    devolvivel: int


@router.get("/retiradas", response_model=list[RetiradaResumo])
def listar_retiradas(f: Funcionario = Depends(exige(Perfil.FARMACEUTICO, Perfil.ENFERMEIRO)),
                     s: Session = Depends(get_session)):
    return [RetiradaResumo(**saida(m).model_dump(), quantidade=q, devolvivel=d)
            for m, q, d in servico.retiradas_visiveis(s, f)]
