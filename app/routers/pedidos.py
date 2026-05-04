# Router de pedidos - endpoints REST para gestao de pedidos Yfood

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Pedido, StatusPedido
from ..schemas import (
    PedidoCriar,
    PedidoActualizarStatus,
    PedidoResposta,
    PedidoLista,
)

router = APIRouter(
    prefix="/pedidos",
    tags=["pedidos"],
    responses={404: {"description": "Pedido nao encontrado"}},
)


@router.post(
    "/",
    response_model=PedidoResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo pedido",
    description="Regista um novo pedido no sistema com os items e dados do cliente.",
)
def criar_pedido(pedido_in: PedidoCriar, db: Session = Depends(get_db)):
    # Converte items (lista de ItemPedido) para JSON string
    items_json = json.dumps(
        [item.model_dump() for item in pedido_in.items], ensure_ascii=False
    )

    # Cria o registo na base de dados
    novo_pedido = Pedido(
        cliente_nome=pedido_in.cliente_nome.strip(),
        items=items_json,
        status=StatusPedido.PENDENTE,
        total=pedido_in.total,
    )

    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    return novo_pedido


@router.get(
    "/",
    response_model=list[PedidoLista],
    summary="Listar todos os pedidos",
    description="Lista os pedidos registados. Pode filtrar por status.",
)
def listar_pedidos(
    filtro_status: Optional[str] = Query(
        None,
        description="Filtrar por status (pendente, em_preparacao, pronto, entregue, cancelado)",
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Pedido)

    if filtro_status is not None:
        # Validar o status fornecido
        status_valido = filtro_status.lower().strip()
        if status_valido not in [s.value for s in StatusPedido]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status invalido. Valores permitidos: {[s.value for s in StatusPedido]}",
            )
        query = query.filter(Pedido.status == status_valido)

    # Ordenar do mais recente para o mais antigo
    pedidos = query.order_by(Pedido.criado_em.desc()).all()
    return pedidos


@router.get(
    "/{pedido_id}",
    response_model=PedidoResposta,
    summary="Obter pedido por ID",
    description="Retorna os dados completos de um pedido especifico.",
)
def obter_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if pedido is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido com id {pedido_id} nao encontrado.",
        )

    return pedido


@router.patch(
    "/{pedido_id}/status",
    response_model=PedidoResposta,
    summary="Actualizar status de um pedido",
    description="Altera o status de um pedido existente. Segue o fluxo normal do restaurante.",
)
def actualizar_status(
    pedido_id: int,
    status_in: PedidoActualizarStatus,
    db: Session = Depends(get_db),
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if pedido is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido com id {pedido_id} nao encontrado.",
        )

    # Validar o status
    novo_status = status_in.status.lower().strip()
    if novo_status not in [s.value for s in StatusPedido]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status invalido. Valores permitidos: {[s.value for s in StatusPedido]}",
        )

    # Impedir transicoes invalidas
    if pedido.status.value == StatusPedido.CANCELADO.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao e possivel alterar status de um pedido cancelado.",
        )

    if pedido.status.value == StatusPedido.ENTREGUE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao e possivel alterar status de um pedido ja entregue.",
        )

    pedido.status = novo_status
    db.commit()
    db.refresh(pedido)

    return pedido
