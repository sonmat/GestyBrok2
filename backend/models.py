"""
SQLAlchemy Models mappati sul database esistente
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


# ==================== TABELLE LEGACY ====================

class TBanca(Base):
    __tablename__ = "t_banche"
    
    id_banca = Column(Integer, primary_key=True)
    nome_banca = Column(Text)
    bic = Column(Text)
    iban = Column(Text)
    n_account = Column(Text)


class TIva(Base):
    __tablename__ = "t_iva"
    
    id_iva = Column(Integer, primary_key=True)
    descrizione = Column(Text)
    iva = Column(Text)


class TPagamento(Base):
    __tablename__ = "t_pagamenti"
    
    id_pagamento = Column(Integer, primary_key=True)
    tipo_pagamento = Column(Text)


class TFamigliaArticolo(Base):
    __tablename__ = "t_famiglie_articoli"
    
    famiglia = Column(Text, primary_key=True)


class TTipoArticolo(Base):
    __tablename__ = "t_tipo_articoli"
    
    tipologia = Column(Text, primary_key=True)


class TArticolo(Base):
    __tablename__ = "t_articoli"
    
    id_articolo = Column(Integer, primary_key=True)
    nome_articolo = Column(Text)
    unita_misura = Column(Text)
    famiglia = Column(Text, ForeignKey("t_famiglie_articoli.famiglia"))
    tipologia = Column(Text, ForeignKey("t_tipo_articoli.tipologia"))


class TVenditore(Base):
    __tablename__ = "t_venditori"
    
    id_venditore = Column(Integer, primary_key=True)
    azienda = Column(Text)
    indirizzo = Column(Text)
    cap = Column(Text)
    citta = Column(Text)
    stato = Column(Text)
    fax = Column(Text)
    telefono = Column(Text)
    piva = Column(Text)
    italiano = Column(Text)
    tipo_pagamento = Column(Text)
    iva = Column(Text)


class TCompratore(Base):
    __tablename__ = "t_compratori"
    
    id_compratore = Column(Integer, primary_key=True)
    azienda = Column(Text)
    indirizzo = Column(Text)
    cap = Column(Text)
    citta = Column(Text)
    stato = Column(Text)
    fax = Column(Text)
    telefono = Column(Text)
    piva = Column(Text)
    italiano = Column(Text)
    tipo_pagamento = Column(Text)
    iva = Column(Text)


class TVenditoreOffre(Base):
    __tablename__ = "t_venditore_offre"
    
    id_offre = Column(Integer, primary_key=True)
    venditore = Column(Integer, ForeignKey("t_venditori.id_venditore"))
    articolo = Column(Integer, ForeignKey("t_articoli.id_articolo"))
    prezzo = Column(Text)
    provvigione = Column(Text)
    tipologia = Column(Text)


class TCompratoreCerca(Base):
    __tablename__ = "t_compratore_cerca"
    
    id_cerca = Column(Integer, primary_key=True)
    compratore = Column(Integer, ForeignKey("t_compratori.id_compratore"))
    articolo = Column(Integer, ForeignKey("t_articoli.id_articolo"))
    note = Column(Text)


class TDatiVenditore(Base):
    __tablename__ = "t_dati_venditori"
    
    id_dati_venditore = Column(Integer, primary_key=True)
    id_venditore = Column(Integer, ForeignKey("t_venditori.id_venditore"))
    mail = Column(Text)
    fax = Column(Text)
    telefono = Column(Text)
    ntel_tipologia = Column(Text)
    contatto = Column(Text)


class TDatiCompratore(Base):
    __tablename__ = "t_dati_compratori"
    
    id_dati_compratore = Column(Integer, primary_key=True)
    id_compratore = Column(Integer, ForeignKey("t_compratori.id_compratore"))
    mail = Column(Text)
    fax = Column(Text)
    telefono = Column(Text)
    ntel_tipologia = Column(Text)
    contatto = Column(Text)


class TConferma(Base):
    __tablename__ = "t_conferme"
    
    id_conferma = Column(Integer, primary_key=True)
    compratore = Column(Integer, ForeignKey("t_compratori.id_compratore"))
    venditore = Column(Integer, ForeignKey("t_venditori.id_venditore"))
    qta = Column(Text)
    prezzo = Column(Text)
    articolo = Column(Integer, ForeignKey("t_articoli.id_articolo"))
    n_conf = Column(Text)
    data_conf = Column(Text)
    provvigione = Column(Text)
    tipologia = Column(Text)
    luogo_consegna = Column(Text)
    condizioni_pag = Column(Text)
    note = Column(Text)
    carico = Column(Text)
    arrivo = Column(Text)
    emailv = Column(Text)
    emailc = Column(Text)


class TDataConsegna(Base):
    __tablename__ = "t_date_consegna"
    
    id_data_consegna = Column(Integer, primary_key=True)
    id_conferma = Column(Integer, ForeignKey("t_conferme.id_conferma"))
    data_consegna = Column(Text)
    qta_consegna = Column(Text)


class TFattura(Base):
    __tablename__ = "t_fatture"
    
    id_fattura = Column(Integer, primary_key=True)
    confermaordine = Column(Integer, ForeignKey("t_conferme.id_conferma"))
    n_fat = Column(Integer)
    data_fat = Column(Integer)
    nota_acr = Column(Integer)
    articolo = Column(Integer)
    qta = Column(Integer)
    prezzo = Column(Integer)
    iva_perc = Column(Integer)
    data_consegna = Column(Integer)
    compilato = Column(Integer)
    fatturata = Column(Integer)


class TFatturaStudio(Base):
    __tablename__ = "t_fatture_studio"
    
    id_fatt_studio = Column(Integer, primary_key=True)
    n_fat = Column(Integer)
    data_fat = Column(Integer)
    nota_acr = Column(Integer)
    cliente = Column(Integer, ForeignKey("t_venditori.id_venditore"))
    t_iva = Column(Integer, ForeignKey("t_iva.id_iva"))
    t_pagamento = Column(Integer, ForeignKey("t_pagamenti.id_pagamento"))
    note = Column(Integer)
    id_banca = Column(Integer, ForeignKey("t_banche.id_banca"))


class TFatturaStudioDet(Base):
    __tablename__ = "t_fat_studio_det"
    
    id_fat_studio_det = Column(Integer, primary_key=True)
    id_fat_studio = Column(Integer, ForeignKey("t_fatture_studio.id_fatt_studio"))
    compratore = Column(Integer, ForeignKey("t_compratori.id_compratore"))
    qta = Column(Integer)
    prezzo = Column(Integer)
    provvigione = Column(Integer)
    tipologia = Column(Integer)
    data_consegna = Column(Integer)


# ==================== TABELLE TRADING ====================

class TConfermaTrading(Base):
    __tablename__ = "t_conferme_trading"
    
    id_conferma = Column(Integer, primary_key=True)
    compratore = Column(Integer, ForeignKey("t_compratori.id_compratore"))
    venditore = Column(Integer, ForeignKey("t_venditori.id_venditore"))
    qta = Column(Text)
    prezzo = Column(Text)
    articolo = Column(Integer, ForeignKey("t_articoli.id_articolo"))
    n_conf = Column(Text)
    data_conf = Column(Text)
    provvigione = Column(Text)
    tipologia = Column(Text)
    luogo_consegna = Column(Text)
    condizioni_pag = Column(Text)
    note = Column(Text)
    carico = Column(Text)
    arrivo = Column(Text)
    emailv = Column(Text)
    emailc = Column(Text)


class TDataConsegnaTrading(Base):
    __tablename__ = "t_date_consegna_trading"
    
    id_data_consegna = Column(Integer, primary_key=True)
    id_conferma = Column(Integer, ForeignKey("t_conferme_trading.id_conferma"))
    data_consegna = Column(Text)
    qta_consegna = Column(Text)
    fatturata = Column(Integer)
    data_pagamento_uscita = Column(Text)
    data_pagamento_entrata = Column(Text)


class TFatturaTrading(Base):
    __tablename__ = "t_fatture_trading"
    
    id_fattura = Column(Integer, primary_key=True)
    confermaordine = Column(Integer, ForeignKey("t_conferme_trading.id_conferma"))
    n_fat = Column(Integer)
    data_fat = Column(Integer)
    nota_acr = Column(Integer)
    articolo = Column(Integer)
    qta = Column(Integer)
    prezzo = Column(Integer)
    iva_perc = Column(Integer)
    data_consegna = Column(Integer)
    compilato = Column(Integer)
    fatturata = Column(Integer)


class TFatturaStudioTrading(Base):
    __tablename__ = "t_fatture_studio_trading"
    
    id_fatt_studio = Column(Integer, primary_key=True)
    n_fat = Column(Integer)
    data_fat = Column(Integer)
    nota_acr = Column(Integer)
    cliente = Column(Integer, ForeignKey("t_compratori.id_compratore"))
    t_iva = Column(Integer, ForeignKey("t_iva.id_iva"))
    t_pagamento = Column(Integer, ForeignKey("t_pagamenti.id_pagamento"))
    note = Column(Integer)
    id_banca = Column(Integer)
    n_conf = Column(Integer)


class TFatturaStudioDetTrading(Base):
    __tablename__ = "t_fat_studio_det_trading"
    
    id_fat_studio_det = Column(Integer, primary_key=True)
    id_fat_studio = Column(Integer, ForeignKey("t_fatture_studio_trading.id_fatt_studio"))
    articolo = Column(Integer, ForeignKey("t_articoli.id_articolo"))
    qta = Column(Integer)
    prezzo = Column(Integer)
    data_consegna = Column(Integer)


# NOTA: Le tabelle nuove (articoli, venditori, compratori, etc. senza prefisso t_)
# sono state create da SQLAlchemy ma non le usiamo per ora.
# Per usare solo le tabelle legacy, commenta le nuove nel main.py