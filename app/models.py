"""Modelo de dados. Os nomes seguem o GLOSSARY.md."""
import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Perfil(str, enum.Enum):
    ADMINISTRADOR = "administrador"
    FARMACEUTICO = "farmaceutico"
    ENFERMEIRO = "enfermeiro"


class ClasseControle(str, enum.Enum):
    COMUM = "comum"
    CONTROLADO = "controlado"


class TipoMovimentacao(str, enum.Enum):
    ENTRADA = "entrada"
    RETIRADA = "retirada"
    DEVOLUCAO = "devolucao"
    DESCARTE = "descarte"
    AJUSTE = "ajuste"


class Funcionario(Base):
    __tablename__ = "funcionarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(100))
    perfil: Mapped[Perfil] = mapped_column(Enum(Perfil))
    ativo: Mapped[bool] = mapped_column(default=True)


class Medicamento(Base):
    __tablename__ = "medicamentos"
    __table_args__ = (UniqueConstraint("nome", "apresentacao"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    apresentacao: Mapped[str] = mapped_column(String(120))
    classe: Mapped[ClasseControle] = mapped_column(Enum(ClasseControle))
    estoque_minimo: Mapped[int] = mapped_column(default=0)

    lotes: Mapped[list["Lote"]] = relationship(back_populates="medicamento")

    @property
    def descricao(self) -> str:
        return f"{self.nome} {self.apresentacao}"


class Lote(Base):
    __tablename__ = "lotes"
    __table_args__ = (UniqueConstraint("medicamento_id", "codigo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    medicamento_id: Mapped[int] = mapped_column(ForeignKey("medicamentos.id"))
    codigo: Mapped[str] = mapped_column(String(60))
    validade: Mapped[date] = mapped_column(Date)
    quantidade: Mapped[int]

    medicamento: Mapped[Medicamento] = relationship(back_populates="lotes")


class Movimentacao(Base):
    """Registro imutável (ADR 0003). Não existe rota de edição ou exclusão."""

    __tablename__ = "movimentacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[TipoMovimentacao] = mapped_column(Enum(TipoMovimentacao))
    medicamento_id: Mapped[int] = mapped_column(ForeignKey("medicamentos.id"))
    funcionario_id: Mapped[int] = mapped_column(ForeignKey("funcionarios.id"))
    data_hora: Mapped[datetime] = mapped_column(DateTime)
    setor: Mapped[str | None] = mapped_column(String(80), default=None)
    paciente: Mapped[str | None] = mapped_column(String(120), default=None)
    motivo: Mapped[str | None] = mapped_column(String(200), default=None)
    retirada_origem_id: Mapped[int | None] = mapped_column(
        ForeignKey("movimentacoes.id"), default=None
    )

    medicamento: Mapped[Medicamento] = relationship()
    funcionario: Mapped[Funcionario] = relationship()
    itens: Mapped[list["ItemMovimentacao"]] = relationship(back_populates="movimentacao")


class ItemMovimentacao(Base):
    """Quantidade movida em um lote. `quantidade` é sempre com sinal:
    positiva aumenta o lote (entrada, devolução, ajuste para cima),
    negativa diminui (retirada, descarte, ajuste para baixo)."""

    __tablename__ = "itens_movimentacao"

    id: Mapped[int] = mapped_column(primary_key=True)
    movimentacao_id: Mapped[int] = mapped_column(ForeignKey("movimentacoes.id"))
    lote_id: Mapped[int] = mapped_column(ForeignKey("lotes.id"))
    quantidade: Mapped[int]

    movimentacao: Mapped[Movimentacao] = relationship(back_populates="itens")
    lote: Mapped[Lote] = relationship()
