"""
Database configuration con SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Configurazione database
BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR}/gestybrok.db"
)

# Engine con pool connections per SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
    echo=False  # Imposta True per debug SQL
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class per models
Base = declarative_base()


def get_db():
    """
    Dependency per ottenere sessione database
    Usa yield per garantire chiusura anche in caso di errore
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inizializza database creando tutte le tabelle"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def reset_db():
    """ATTENZIONE: Elimina e ricrea tutte le tabelle"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset completed")
