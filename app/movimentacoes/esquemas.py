"""Interface pública de leitura de movimentações (usada também pelo Monitoramento)."""
from datetime import datetime

from pydantic import BaseModel

from app.models import Movimentacao, TipoMovimentacao


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


def para_resposta(m: Movimentacao) -> MovimentacaoOut:
    return MovimentacaoOut(
        id=m.id, tipo=m.tipo, medicamento_id=m.medicamento_id,
        medicamento=m.medicamento.descricao,
        funcionario_id=m.funcionario_id, funcionario=m.funcionario.nome,
        data_hora=m.data_hora, setor=m.setor, paciente=m.paciente, motivo=m.motivo,
        retirada_origem_id=m.retirada_origem_id,
        itens=[ItemOut(lote_id=i.lote_id, codigo_lote=i.lote.codigo, quantidade=abs(i.quantidade),
                       variacao=i.quantidade)
               for i in m.itens],
    )
