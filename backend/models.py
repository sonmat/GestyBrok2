"""
SQLAlchemy Models per GestyBrok
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, ForeignKey, Text, DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class TipoArticolo(Base):
    __tablename__ = "tipi_articolo"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)
    descrizione = Column(Text)
    
    articoli = relationship("Articolo", back_populates="tipo")


class FamigliaArticolo(Base):
    __tablename__ = "famiglie_articolo"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)
    descrizione = Column(Text)
    
    articoli = relationship("Articolo", back_populates="famiglia")


class Articolo(Base):
    __tablename__ = "articoli"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    codice = Column(String(50), unique=True)
    unita_misura = Column(String(20))
    tipo_id = Column(Integer, ForeignKey("tipi_articolo.id"))
    famiglia_id = Column(Integer, ForeignKey("famiglie_articolo.id"))
    descrizione = Column(Text)
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tipo = relationship("TipoArticolo", back_populates="articoli")
    famiglia = relationship("FamigliaArticolo", back_populates="articoli")
    offerte = relationship("VenditoreOffre", back_populates="articolo")
    richieste = relationship("CompratoreCerca", back_populates="articolo")


class Venditore(Base):
    __tablename__ = "venditori"
    
    id = Column(Integer, primary_key=True, index=True)
    codice = Column(String(50), unique=True)
    azienda = Column(String(200), nullable=False, index=True)
    partita_iva = Column(String(20))
    indirizzo = Column(String(200))
    cap = Column(String(10))
    citta = Column(String(100))
    telefono = Column(String(30))
    fax = Column(String(30))
    email = Column(String(100))
    italiano = Column(Boolean, default=True)
    iva_id = Column(Integer, ForeignKey("iva.id"))
    pagamento_id = Column(Integer, ForeignKey("pagamenti.id"))
    banca_id = Column(Integer, ForeignKey("banche.id"))
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    offerte = relationship("VenditoreOffre", back_populates="venditore")
    conferme_ordine = relationship("ConfermaOrdine", back_populates="venditore")
    iva = relationship("Iva")
    pagamento = relationship("Pagamento")
    banca = relationship("Banca")


class Compratore(Base):
    __tablename__ = "compratori"
    
    id = Column(Integer, primary_key=True, index=True)
    codice = Column(String(50), unique=True)
    azienda = Column(String(200), nullable=False, index=True)
    partita_iva = Column(String(20))
    indirizzo = Column(String(200))
    cap = Column(String(10))
    citta = Column(String(100))
    telefono = Column(String(30))
    email = Column(String(100))
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    richieste = relationship("CompratoreCerca", back_populates="compratore")
    conferme_ordine = relationship("ConfermaOrdine", back_populates="compratore")


class VenditoreOffre(Base):
    __tablename__ = "venditore_offre"
    
    id = Column(Integer, primary_key=True, index=True)
    venditore_id = Column(Integer, ForeignKey("venditori.id"), nullable=False)
    articolo_id = Column(Integer, ForeignKey("articoli.id"), nullable=False)
    prezzo = Column(Float, nullable=False)
    provvigione = Column(Float)
    tipologia = Column(String(100))
    note = Column(Text)
    valido_da = Column(Date)
    valido_a = Column(Date)
    
    venditore = relationship("Venditore", back_populates="offerte")
    articolo = relationship("Articolo", back_populates="offerte")


class CompratoreCerca(Base):
    __tablename__ = "compratore_cerca"
    
    id = Column(Integer, primary_key=True, index=True)
    compratore_id = Column(Integer, ForeignKey("compratori.id"), nullable=False)
    articolo_id = Column(Integer, ForeignKey("articoli.id"), nullable=False)
    quantita_richiesta = Column(Float)
    note = Column(Text)
    data_richiesta = Column(Date, default=datetime.utcnow)
    
    compratore = relationship("Compratore", back_populates="richieste")
    articolo = relationship("Articolo", back_populates="richieste")


class ConfermaOrdine(Base):
    __tablename__ = "conferme_ordine"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_conferma = Column(String(50), unique=True)
    data_conferma = Column(Date, nullable=False)
    venditore_id = Column(Integer, ForeignKey("venditori.id"), nullable=False)
    compratore_id = Column(Integer, ForeignKey("compratori.id"), nullable=False)
    articolo_id = Column(Integer, ForeignKey("articoli.id"), nullable=False)
    quantita = Column(Float, nullable=False)
    prezzo = Column(Float, nullable=False)
    provvigione = Column(Float)
    tipologia = Column(String(100))
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    venditore = relationship("Venditore", back_populates="conferme_ordine")
    compratore = relationship("Compratore", back_populates="conferme_ordine")
    date_consegna = relationship("DataConsegna", back_populates="conferma_ordine", cascade="all, delete-orphan")
    fatture = relationship("Fattura", back_populates="conferma_ordine")


class DataConsegna(Base):
    __tablename__ = "date_consegna"
    
    id = Column(Integer, primary_key=True, index=True)
    conferma_ordine_id = Column(Integer, ForeignKey("conferme_ordine.id"), nullable=False)
    data_consegna = Column(Date, nullable=False)
    quantita_consegnata = Column(Float)
    note = Column(Text)
    
    conferma_ordine = relationship("ConfermaOrdine", back_populates="date_consegna")


class Fattura(Base):
    __tablename__ = "fatture"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_fattura = Column(String(50), unique=True, nullable=False)
    data_fattura = Column(Date, nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("venditori.id"), nullable=False)
    conferma_ordine_id = Column(Integer, ForeignKey("conferme_ordine.id"))
    importo_netto = Column(Float)
    importo_iva = Column(Float)
    importo_totale = Column(Float)
    pagata = Column(Boolean, default=False)
    data_pagamento = Column(Date)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conferma_ordine = relationship("ConfermaOrdine", back_populates="fatture")


class Iva(Base):
    __tablename__ = "iva"
    
    id = Column(Integer, primary_key=True, index=True)
    percentuale = Column(Float, nullable=False)
    descrizione = Column(String(100))


class Pagamento(Base):
    __tablename__ = "pagamenti"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(100), nullable=False)
    giorni = Column(Integer)
    descrizione = Column(Text)


class Banca(Base):
    __tablename__ = "banche"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    iban = Column(String(50))
    swift = Column(String(20))
    indirizzo = Column(String(200))
