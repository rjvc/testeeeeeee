# Ponto de entrada principal da API REST Yfood

import uvicorn
from fastapi import FastAPI

from .database import engine, Base
from .routers.pedidos import router as pedidos_router

# Criar todas as tabelas na base de dados ao iniciar
Base.metadata.create_all(bind=engine)

# Inicializar a aplicacao FastAPI
app = FastAPI(
    title="API Yfood - Gestao de Pedidos",
    description="API REST para gestao de pedidos do Restaurante Yfood.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Registar routers
app.include_router(pedidos_router)


@app.get(
    "/",
    summary="Raiz da API",
    description="Endpoint de verificacao de saude da API.",
)
def raiz():
    return {
        "api": "Yfood - Gestao de Pedidos",
        "versao": "1.0.0",
        "status": "operacional",
        "documentacao": "/docs",
    }


# Permite execucao directa: python main.py
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
