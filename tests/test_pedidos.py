# Testes unitarios para a API de pedidos Yfood

import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Base de dados em memoria para testes (isolada, rapida, sem ficheiros)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

engine_teste = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionLocalTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine_teste)


def override_get_db():
    """Fornece sessao de base de dados de teste."""
    db = SessionLocalTeste()
    try:
        yield db
    finally:
        db.close()


# Substitui a dependencia da BD pela de teste
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def preparar_bd():
    """Cria as tabelas antes de cada teste e limpa depois."""
    Base.metadata.create_all(bind=engine_teste)
    yield
    Base.metadata.drop_all(bind=engine_teste)


@pytest.fixture
def cliente():
    """Cliente HTTP de teste."""
    return TestClient(app)


# ---------------------------------------------------------------
# Testes: Criar pedido (POST /pedidos/)
# ---------------------------------------------------------------

def test_criar_pedido_sucesso(cliente):
    """Deve criar um pedido com dados validos e retornar 201."""
    payload = {
        "cliente_nome": "Joao Baptista",
        "items": [
            {"nome": "Muamba de Galinha", "quantidade": 2, "preco_unitario": 2500.0},
            {"nome": "Funje de Bomba", "quantidade": 1, "preco_unitario": 1000.0},
        ],
        "total": 6000.0,
    }

    resposta = cliente.post("/pedidos/", json=payload)

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["cliente_nome"] == "Joao Baptista"
    assert dados["status"] == "pendente"
    assert dados["total"] == 6000.0
    assert dados["id"] == 1


def test_criar_pedido_sem_items(cliente):
    """Deve rejeitar pedido sem items (validacao Pydantic)."""
    payload = {
        "cliente_nome": "Joao Baptista",
        "items": [],
        "total": 0.0,
    }

    resposta = cliente.post("/pedidos/", json=payload)

    assert resposta.status_code == 422


def test_criar_pedido_nome_curto(cliente):
    """Deve rejeitar pedido com nome de cliente muito curto."""
    payload = {
        "cliente_nome": "J",
        "items": [{"nome": "Prato", "quantidade": 1, "preco_unitario": 100.0}],
        "total": 100.0,
    }

    resposta = cliente.post("/pedidos/", json=payload)

    assert resposta.status_code == 422


# ---------------------------------------------------------------
# Testes: Listar pedidos (GET /pedidos/)
# ---------------------------------------------------------------

def test_listar_pedidos_vazio(cliente):
    """Deve retornar lista vazia quando nao ha pedidos."""
    resposta = cliente.get("/pedidos/")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_listar_pedidos_com_dados(cliente):
    """Deve listar todos os pedidos criados."""
    # Criar dois pedidos
    cliente.post(
        "/pedidos/",
        json={
            "cliente_nome": "Maria",
            "items": [{"nome": "Sopa", "quantidade": 1, "preco_unitario": 500.0}],
            "total": 500.0,
        },
    )
    cliente.post(
        "/pedidos/",
        json={
            "cliente_nome": "Pedro",
            "items": [{"nome": "Peixe Grelhado", "quantidade": 2, "preco_unitario": 3000.0}],
            "total": 6000.0,
        },
    )

    resposta = cliente.get("/pedidos/")

    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) == 2
    # Ordem descendente: o ultimo criado primeiro
    assert dados[0]["cliente_nome"] == "Pedro"
    assert dados[1]["cliente_nome"] == "Maria"


def test_listar_pedidos_filtro_status(cliente):
    """Deve filtrar pedidos por status."""
    cliente.post(
        "/pedidos/",
        json={
            "cliente_nome": "Maria",
            "items": [{"nome": "Sopa", "quantidade": 1, "preco_unitario": 500.0}],
            "total": 500.0,
        },
    )

    resposta = cliente.get("/pedidos/?filtro_status=pendente")

    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) == 1
    assert dados[0]["status"] == "pendente"


def test_listar_pedidos_status_invalido(cliente):
    """Deve rejeitar filtro com status invalido."""
    resposta = cliente.get("/pedidos/?filtro_status=inexistente")

    assert resposta.status_code == 400


# ---------------------------------------------------------------
# Testes: Obter pedido por ID (GET /pedidos/{id})
# ---------------------------------------------------------------

def test_obter_pedido_existente(cliente):
    """Deve retornar o pedido com o ID especificado."""
    cliente.post(
        "/pedidos/",
        json={
            "cliente_nome": "Maria",
            "items": [{"nome": "Sopa", "quantidade": 1, "preco_unitario": 500.0}],
            "total": 500.0,
        },
    )

    resposta = cliente.get("/pedidos/1")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == 1
    assert resposta.json()["cliente_nome"] == "Maria"


def test_obter_pedido_inexistente(cliente):
    """Deve retornar 404 para pedido que nao existe."""
    resposta = cliente.get("/pedidos/999")

    assert resposta.status_code == 404


# ---------------------------------------------------------------
# Testes: Actualizar status (PATCH /pedidos/{id}/status)
# ---------------------------------------------------------------

def test_actualizar_status_sucesso(cliente):
    """Deve actualizar o status de um pedido existente."""
    cliente.post(
        "/pedidos/",
        json={
            "cliente_nome": "Maria",
            "items": [{"nome": "Sopa", "quantidade": 1, "preco_unitario": 500.0}],
            "total": 500.0,
        },
    )

    resposta = cliente.patch("/pedidos/1/status", json={"status": "em_preparacao"})

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "em_preparacao"


def test_actualizar_status_fluxo_completo(cliente):
    """Deve permitir o fluxo completo: pendente -> em_preparacao -> pronto -> entregue."""
    # Criar pedido
    cliente.post(
        "/pedidos/",
        json={
            "cliente_nome": "Maria",
            "items": [{"nome": "Sopa", "quantidade": 1, "preco_unitario": 500.0}],
            "total": 500.0,
        },
    )

    # Pendente -> Em preparacao
    r1 = cliente.patch("/pedidos/1/status", json={"status": "em_preparacao"})
    assert r1.json()["status"] == "em_preparacao"

    # Em preparacao -> Pronto
    r2 = cliente.patch("/pedidos/1/status", json={"status": "pronto"})
    assert r2.json()["status"] == "pronto"

    # Pronto -> Entregue
    r3 = cliente.patch("/pedidos/1/status", json={"status": "entregue"})
    assert r3.json()["status"] == "entregue"


def test_actualizar_status_pedido_inexistente(cliente):
    """Deve retornar 404 ao actualizar pedido que nao existe."""
    resposta = cliente.patch("/pedidos/999/status", json={"status": "pronto"})

    assert resposta.status_code == 404


def test_actualizar_status_invalido(cliente):
    """Deve rejeitar status que nao existe no enumerado."""
    cliente.post(
        "/pedidos/",
        json={
            "cliente_nome": "Maria",
            "items": [{"nome": "Sopa", "quantidade": 1, "preco_unitario": 500.0}],
            "total": 500.0,
        },
    )

    resposta = cliente.patch("/pedidos/1/status", json={"status": "status_falso"})

    assert resposta.status_code == 400


def test_actualizar_pedido_cancelado(cliente):
    """Deve impedir alteracao de pedido ja cancelado."""
    cliente.post(
        "/pedidos/",
        json={
            "cliente_nome": "Maria",
            "items": [{"nome": "Sopa", "quantidade": 1, "preco_unitario": 500.0}],
            "total": 500.0,
        },
    )
    cliente.patch("/pedidos/1/status", json={"status": "cancelado"})

    resposta = cliente.patch("/pedidos/1/status", json={"status": "em_preparacao"})

    assert resposta.status_code == 400
    assert "cancelado" in resposta.json()["detail"].lower()


def test_actualizar_pedido_entregue(cliente):
    """Deve impedir alteracao de pedido ja entregue."""
    cliente.post(
        "/pedidos/",
        json={
            "cliente_nome": "Maria",
            "items": [{"nome": "Sopa", "quantidade": 1, "preco_unitario": 500.0}],
            "total": 500.0,
        },
    )
    cliente.patch("/pedidos/1/status", json={"status": "em_preparacao"})
    cliente.patch("/pedidos/1/status", json={"status": "pronto"})
    cliente.patch("/pedidos/1/status", json={"status": "entregue"})

    resposta = cliente.patch("/pedidos/1/status", json={"status": "cancelado"})

    assert resposta.status_code == 400
    assert "entregue" in resposta.json()["detail"].lower()


# ---------------------------------------------------------------
# Testes: Endpoint raiz
# ---------------------------------------------------------------

def test_raiz(cliente):
    """Deve retornar informacao da API no endpoint raiz."""
    resposta = cliente.get("/")

    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["status"] == "operacional"
    assert dados["api"] == "Yfood - Gestao de Pedidos"
