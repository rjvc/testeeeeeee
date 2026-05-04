# API Yfood - Gestao de Pedidos

API REST para gestao de pedidos do Restaurante Yfood.

## Stack

- **Python 3.10+**
- **FastAPI** — framework web assincrono
- **SQLAlchemy** — ORM para base de dados
- **SQLite** — base de dados local (sem dependencias externas)
- **Pydantic** — validacao de dados
- **Pytest** — testes unitarios

## Estrutura do Projecto

```
yfood-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # Ponto de entrada da aplicacao
│   ├── database.py       # Configuracao SQLite/SQLAlchemy
│   ├── models.py         # Modelos SQLAlchemy
│   ├── schemas.py        # Schemas Pydantic
│   └── routers/
│       ├── __init__.py
│       └── pedidos.py    # Endpoints REST de pedidos
├── tests/
│   ├── __init__.py
│   └── test_pedidos.py   # Testes unitarios
├── requirements.txt      # Dependencias Python
└── README.md
```

## Instalacao e Execucao

### 1. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Executar o servidor

```bash
# A partir da raiz do projecto yfood-api/
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

A API fica disponivel em `http://localhost:8000`.

### 4. Documentacao Interactiva

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Endpoints

| Metodo  | Rota                      | Descricao                |
| ------- | ------------------------- | ------------------------ |
| `GET`   | `/`                       | Verificacao de saude     |
| `POST`  | `/pedidos/`               | Criar novo pedido        |
| `GET`   | `/pedidos/`               | Listar pedidos           |
| `GET`   | `/pedidos/{id}`           | Obter pedido por ID      |
| `PATCH` | `/pedidos/{id}/status`    | Actualizar status        |

### Filtro de status (query parameter)

`GET /pedidos/?filtro_status=pendente`

Valores validos: `pendente`, `em_preparacao`, `pronto`, `entregue`, `cancelado`

## Exemplos de Uso

### Criar um pedido

```bash
curl -X POST http://localhost:8000/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "Joao Baptista",
    "items": [
      {"nome": "Muamba de Galinha", "quantidade": 2, "preco_unitario": 2500.0},
      {"nome": "Funje de Bomba", "quantidade": 1, "preco_unitario": 1000.0}
    ],
    "total": 6000.0
  }'
```

### Listar pedidos

```bash
curl http://localhost:8000/pedidos/
```

### Actualizar status

```bash
curl -X PATCH http://localhost:8000/pedidos/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "em_preparacao"}'
```

## Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Com cobertura (opcional: pip install pytest-cov)
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Fluxo de Estados

```
pendente → em_preparacao → pronto → entregue
                ↘ cancelado ↙
```

- Um pedido cancelado ou entregue nao pode ter o status alterado novamente.
- O pedido comeca sempre como `pendente`.

## Consideracoes Tecnicas

- **Base de dados**: SQLite local. Para producao, migrar para PostgreSQL.
- **Soberania de dados**: Dados armazenados localmente (yfood.db).
- **Conectividade**: API autonoma, nao depende de servicos externos.
- **Ambiente**: Projecto pensado para ambientes com conectividade variavel (TCO Angola).
