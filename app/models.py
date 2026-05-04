# Modelos SQLAlchemy para a API de pedidos do Restaurante Yfood

import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum
from .database import Base

# Funcoes auxiliares para timestamps (substituem utcnow, que esta deprecated em Python 3.13+)
_agora_utc = lambda: datetime.datetime.now(datetime.UTC)


class StatusPedido(str, enum.Enum):
    """Estados possiveis de um pedido no fluxo do restaurante."""
    PENDENTE = "pendente"
    EM_PREPARACAO = "em_preparacao"
    PRONTO = "pronto"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class Pedido(Base):
    """
    Modelo que representa um pedido no restaurante Yfood.

    Campos:
    - id: Identificador unico auto-incrementado
    - cliente_nome: Nome do cliente que fez o pedido
    - items: Lista de items em formato JSON (string)
    - status: Estado actual do pedido (pendente -> em_preparacao -> pronto -> entregue)
    - total: Valor total do pedido em Kz (ou outra moeda)
    - criado_em: Data/hora de criacao do pedido
    - actualizado_em: Data/hora da ultima actualizacao
    """
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_nome: Mapped[str] = mapped_column(String(200), nullable=False)
    items: Mapped[str] = mapped_column(String(2000), nullable=False, default="[]")
    status: Mapped[StatusPedido] = mapped_column(
        SAEnum(StatusPedido, name="status_pedido_enum"),
        nullable=False,
        default=StatusPedido.PENDENTE,
    )
    total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    criado_em: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=_agora_utc
    )
    actualizado_em: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=_agora_utc,
        onupdate=_agora_utc,
    )

    def __repr__(self) -> str:
        return f"<Pedido(id={self.id}, cliente='{self.cliente_nome}', status='{self.status.value}')>"
