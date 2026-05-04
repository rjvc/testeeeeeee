# Configuracao da base de dados SQLite com SQLAlchemy
# Utilizamos SQLite por simplicidade e para evitar dependencias externas
# Ideal para ambientes com conectividade variavel (TCO Angola)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Ficheiro SQLite local - respeita soberania de dados
SQLALCHEMY_DATABASE_URL = "sqlite:///./yfood.db"

# connect_args necessarios apenas para SQLite (multithreading seguro)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base declarativa para modelos SQLAlchemy."""
    pass


# Dependencia FastAPI para obter sessao de base de dados por pedido
def get_db():
    """
    Fornece uma sessao de base de dados por pedido HTTP.
    A sessao e fechada automaticamente apos o pedido.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
