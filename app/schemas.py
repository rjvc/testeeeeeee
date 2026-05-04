# Schemas Pydantic para validacao e serializacao de dados da API

import datetime
from pydantic import BaseModel, Field


class ItemPedido(BaseModel):
    """Representa um item individual dentro de um pedido."""
    nome: str = Field(description="Nome do prato/produto")
    quantidade: int = Field(ge=1, description="Quantidade (minimo 1)")
    preco_unitario: float = Field(ge=0, description="Preco unitario em Kz")


class PedidoCriar(BaseModel):
    """Schema para criacao de um novo pedido."""
    cliente_nome: str = Field(
        min_length=2,
        max_length=200,
        description="Nome do cliente",
        examples=["Maria Silva"],
    )
    items: list[ItemPedido] = Field(
        min_length=1,
        max_length=50,
        description="Lista de items do pedido (minimo 1, maximo 50)",
    )
    total: float = Field(ge=0, description="Valor total do pedido")


class PedidoActualizarStatus(BaseModel):
    """Schema para actualizacao do status de um pedido."""
    status: str = Field(
        description="Novo status do pedido",
        examples=["em_preparacao"],
    )


class PedidoResposta(BaseModel):
    """Schema de resposta com os dados completos de um pedido."""
    id: int
    cliente_nome: str
    items: str
    status: str
    total: float
    criado_em: datetime.datetime
    actualizado_em: datetime.datetime

    model_config = {"from_attributes": True}


class PedidoLista(BaseModel):
    """Schema simplificado para listagem de pedidos."""
    id: int
    cliente_nome: str
    status: str
    total: float
    criado_em: datetime.datetime

    model_config = {"from_attributes": True}
