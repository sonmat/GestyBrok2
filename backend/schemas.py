"""
Pydantic schemas per validazione e serializzazione
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import date, datetime


# ==================== ARTICOLI ====================
class ArticoloBase(BaseModel):
    nome: str
    codice: Optional[str] = None
    unita_misura: Optional[str] = None
    tipo_id: Optional[int] = None
    famiglia_id: Optional[int] = None
    descrizione: Optional[str] = None
    attivo: bool = True


class ArticoloCreate(ArticoloBase):
    pass


class ArticoloResponse(ArticoloBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== VENDITORI ====================
class VenditoreBase(BaseModel):
    codice: Optional[str] = None
    azienda: str
    partita_iva: Optional[str] = None
    indirizzo: Optional[str] = None
    cap: Optional[str] = None
    citta: Optional[str] = None
    telefono: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[EmailStr] = None
    italiano: bool = True
    iva_id: Optional[int] = None
    pagamento_id: Optional[int] = None
    banca_id: Optional[int] = None
    attivo: bool = True


class VenditoreCreate(VenditoreBase):
    pass


class VenditoreResponse(VenditoreBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== COMPRATORI ====================
class CompratoreBase(BaseModel):
    codice: Optional[str] = None
    azienda: str
    partita_iva: Optional[str] = None
    indirizzo: Optional[str] = None
    cap: Optional[str] = None
    citta: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    attivo: bool = True


class CompratoreCreate(CompratoreBase):
    pass


class CompratoreResponse(CompratoreBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== CONFERME ORDINE ====================
class ConfermaOrdineBase(BaseModel):
    numero_conferma: Optional[str] = None
    data_conferma: date
    venditore_id: int
    compratore_id: int
    articolo_id: int
    quantita: float
    prezzo: float
    provvigione: Optional[float] = None
    tipologia: Optional[str] = None
    note: Optional[str] = None
    
    @validator('quantita', 'prezzo')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Deve essere maggiore di zero')
        return v


class ConfermaOrdineCreate(ConfermaOrdineBase):
    pass


class ConfermaOrdineResponse(ConfermaOrdineBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== DATE CONSEGNA ====================
class DataConsegnaBase(BaseModel):
    conferma_ordine_id: int
    data_consegna: date
    quantita_consegnata: Optional[float] = None
    note: Optional[str] = None


class DataConsegnaCreate(DataConsegnaBase):
    pass


class DataConsegnaResponse(DataConsegnaBase):
    id: int
    
    class Config:
        from_attributes = True


# ==================== FATTURE ====================
class FatturaBase(BaseModel):
    numero_fattura: str
    data_fattura: date
    cliente_id: int
    conferma_ordine_id: Optional[int] = None
    importo_netto: Optional[float] = None
    importo_iva: Optional[float] = None
    importo_totale: Optional[float] = None
    pagata: bool = False
    data_pagamento: Optional[date] = None
    note: Optional[str] = None


class FatturaCreate(FatturaBase):
    pass


class FatturaResponse(FatturaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== OFFERTE E RICHIESTE ====================
class VenditoreOffreBase(BaseModel):
    venditore_id: int
    articolo_id: int
    prezzo: float
    provvigione: Optional[float] = None
    tipologia: Optional[str] = None
    note: Optional[str] = None
    valido_da: Optional[date] = None
    valido_a: Optional[date] = None


class VenditoreOffreCreate(VenditoreOffreBase):
    pass


class VenditoreOffreResponse(VenditoreOffreBase):
    id: int
    
    class Config:
        from_attributes = True


class CompratoreCercaBase(BaseModel):
    compratore_id: int
    articolo_id: int
    quantita_richiesta: Optional[float] = None
    note: Optional[str] = None
    data_richiesta: Optional[date] = None


class CompratoreCercaCreate(CompratoreCercaBase):
    pass


class CompratoreCercaResponse(CompratoreCercaBase):
    id: int
    
    class Config:
        from_attributes = True


# ==================== ANAGRAFICHE SUPPORTO ====================
class IvaBase(BaseModel):
    percentuale: float
    descrizione: Optional[str] = None


class IvaCreate(IvaBase):
    pass


class IvaResponse(IvaBase):
    id: int
    
    class Config:
        from_attributes = True


class PagamentoBase(BaseModel):
    tipo: str
    giorni: Optional[int] = None
    descrizione: Optional[str] = None


class PagamentoCreate(PagamentoBase):
    pass


class PagamentoResponse(PagamentoBase):
    id: int
    
    class Config:
        from_attributes = True


class BancaBase(BaseModel):
    nome: str
    iban: Optional[str] = None
    swift: Optional[str] = None
    indirizzo: Optional[str] = None


class BancaCreate(BancaBase):
    pass


class BancaResponse(BancaBase):
    id: int
    
    class Config:
        from_attributes = True
