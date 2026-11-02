from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.acesso.dependencias import exige, funcionario_logado
from app.db import get_session
from app.estoque import servico
from app.relogio import hoje
from app.models import ClasseControle, Funcionario, Medicamento, Perfil

router = APIRouter(tags=["Estoque"])


class MedicamentoIn(BaseModel):
    nome: str
    apresentacao: str
    classe: ClasseControle
    estoque_minimo: int = 0


class MedicamentoPatch(BaseModel):
    estoque_minimo: int


class LoteOut(BaseModel):
    id: int
    codigo: str
    validade: date
    quantidade: int
    vencido: bool


class MedicamentoOut(BaseModel):
    id: int
    nome: str
    apresentacao: str
    classe: ClasseControle
    estoque_minimo: int
    estoque_disponivel: int
    lotes: list[LoteOut]


def _saida(s: Session, m: Medicamento, dia: date) -> MedicamentoOut:
    lotes = servico.lotes_do_medicamento(s, m.id)
    return MedicamentoOut(
        id=m.id,
        nome=m.nome,
        apresentacao=m.apresentacao,
        classe=m.classe,
        estoque_minimo=m.estoque_minimo,
        estoque_disponivel=servico.estoque_disponivel(s, m.id, dia),
        lotes=[
            LoteOut(id=l.id, codigo=l.codigo, validade=l.validade, quantidade=l.quantidade,
                    vencido=servico.lote_vencido(l, dia))
            for l in lotes
        ],
    )


@router.get("/medicamentos", response_model=list[MedicamentoOut])
def listar(_: Funcionario = Depends(funcionario_logado), s: Session = Depends(get_session),
           dia: date = Depends(hoje)):
    return [_saida(s, m, dia) for m in servico.listar_medicamentos(s)]


@router.get("/medicamentos/{medicamento_id}", response_model=MedicamentoOut)
def obter(medicamento_id: int, _: Funcionario = Depends(funcionario_logado),
          s: Session = Depends(get_session), dia: date = Depends(hoje)):
    return _saida(s, servico.obter_medicamento(s, medicamento_id), dia)


@router.post("/medicamentos", response_model=MedicamentoOut, status_code=201)
def criar(dados: MedicamentoIn, _: Funcionario = Depends(exige(Perfil.ADMINISTRADOR)),
          s: Session = Depends(get_session), dia: date = Depends(hoje)):
    m = servico.criar_medicamento(s, nome=dados.nome, apresentacao=dados.apresentacao,
                                  classe=dados.classe, estoque_minimo=dados.estoque_minimo)
    return _saida(s, m, dia)


@router.patch("/medicamentos/{medicamento_id}", response_model=MedicamentoOut)
def alterar(medicamento_id: int, dados: MedicamentoPatch,
            _: Funcionario = Depends(exige(Perfil.ADMINISTRADOR)),
            s: Session = Depends(get_session), dia: date = Depends(hoje)):
    return _saida(s, servico.alterar_estoque_minimo(s, medicamento_id, dados.estoque_minimo), dia)
