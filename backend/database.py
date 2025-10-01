"""
Configurazione database per db_gesty.db esistente
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Path al tuo database - la cartella backend
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = f"{BASE_DIR}/db_gesty.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Crea engine con settings per evitare cache
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "isolation_level": None  # IMPORTANTE: disabilita transazioni implicite
    },
    pool_pre_ping=True,  # Verifica connessione prima di usarla
    pool_recycle=3600,   # Ricrea connessioni dopo 1 ora
    echo=False
)

# Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=True,  # IMPORTANTE: flush automatico
    bind=engine,
    expire_on_commit=False  # Non scadere gli oggetti dopo commit
)

# Base per models
Base = declarative_base()


def get_db():
    """Ottiene sessione database"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Connette al database esistente SENZA modificarlo"""
    print(f"✓ Database connesso: {DATABASE_PATH}")