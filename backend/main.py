"""
Backend API per GestyBrok
FastAPI application per gestione ordini trading
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import get_db, engine, Base
from models import (
    Articolo, Venditore, Compratore, ConfermaOrdine,
    Fattura, TipoArticolo, FamigliaArticolo
)
from schemas import (
    ArticoloCreate, ArticoloResponse,
    VenditoreCreate, VenditoreResponse,
    CompratoreCreate, CompratoreResponse,
    ConfermaOrdineCreate, ConfermaOrdineResponse,
    FatturaCreate, FatturaResponse
)

# Crea tutte le tabelle
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GestyBrok API",
    description="API per gestione ordini trading",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ARTICOLI ====================
@app.get("/api/articoli", response_model=List[ArticoloResponse])
def get_articoli(
    skip: int = 0,
    limit: int = 100,
    tipo_id: Optional[int] = None,
    famiglia_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Recupera lista articoli con filtri opzionali"""
    query = db.query(Articolo)
    
    if tipo_id:
        query = query.filter(Articolo.tipo_id == tipo_id)
    if famiglia_id:
        query = query.filter(Articolo.famiglia_id == famiglia_id)
    
    return query.offset(skip).limit(limit).all()


@app.get("/api/articoli/{articolo_id}", response_model=ArticoloResponse)
def get_articolo(articolo_id: int, db: Session = Depends(get_db)):
    """Recupera singolo articolo"""
    articolo = db.query(Articolo).filter(Articolo.id == articolo_id).first()
    if not articolo:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    return articolo


@app.post("/api/articoli", response_model=ArticoloResponse, status_code=201)
def create_articolo(articolo: ArticoloCreate, db: Session = Depends(get_db)):
    """Crea nuovo articolo"""
    db_articolo = Articolo(**articolo.dict())
    db.add(db_articolo)
    try:
        db.commit()
        db.refresh(db_articolo)
        return db_articolo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/articoli/{articolo_id}", response_model=ArticoloResponse)
def update_articolo(
    articolo_id: int,
    articolo: ArticoloCreate,
    db: Session = Depends(get_db)
):
    """Aggiorna articolo esistente"""
    db_articolo = db.query(Articolo).filter(Articolo.id == articolo_id).first()
    if not db_articolo:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    
    for key, value in articolo.dict().items():
        setattr(db_articolo, key, value)
    
    try:
        db.commit()
        db.refresh(db_articolo)
        return db_articolo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/articoli/{articolo_id}", status_code=204)
def delete_articolo(articolo_id: int, db: Session = Depends(get_db)):
    """Elimina articolo"""
    db_articolo = db.query(Articolo).filter(Articolo.id == articolo_id).first()
    if not db_articolo:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    
    db.delete(db_articolo)
    db.commit()
    return None


# ==================== VENDITORI ====================
@app.get("/api/venditori", response_model=List[VenditoreResponse])
def get_venditori(
    skip: int = 0,
    limit: int = 100,
    italiano: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Recupera lista venditori"""
    query = db.query(Venditore)
    if italiano is not None:
        query = query.filter(Venditore.italiano == italiano)
    return query.offset(skip).limit(limit).all()


@app.post("/api/venditori", response_model=VenditoreResponse, status_code=201)
def create_venditore(venditore: VenditoreCreate, db: Session = Depends(get_db)):
    """Crea nuovo venditore"""
    db_venditore = Venditore(**venditore.dict())
    db.add(db_venditore)
    try:
        db.commit()
        db.refresh(db_venditore)
        return db_venditore
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# ==================== COMPRATORI ====================
@app.get("/api/compratori", response_model=List[CompratoreResponse])
def get_compratori(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Recupera lista compratori"""
    return db.query(Compratore).offset(skip).limit(limit).all()


@app.post("/api/compratori", response_model=CompratoreResponse, status_code=201)
def create_compratore(compratore: CompratoreCreate, db: Session = Depends(get_db)):
    """Crea nuovo compratore"""
    db_compratore = Compratore(**compratore.dict())
    db.add(db_compratore)
    try:
        db.commit()
        db.refresh(db_compratore)
        return db_compratore
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# ==================== CONFERME ORDINE ====================
@app.get("/api/conferme-ordine", response_model=List[ConfermaOrdineResponse])
def get_conferme_ordine(
    skip: int = 0,
    limit: int = 100,
    venditore_id: Optional[int] = None,
    compratore_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Recupera conferme ordine con filtri"""
    query = db.query(ConfermaOrdine)
    
    if venditore_id:
        query = query.filter(ConfermaOrdine.venditore_id == venditore_id)
    if compratore_id:
        query = query.filter(ConfermaOrdine.compratore_id == compratore_id)
    
    return query.offset(skip).limit(limit).all()


@app.post("/api/conferme-ordine", response_model=ConfermaOrdineResponse, status_code=201)
def create_conferma_ordine(
    conferma: ConfermaOrdineCreate,
    db: Session = Depends(get_db)
):
    """Crea nuova conferma ordine"""
    db_conferma = ConfermaOrdine(**conferma.dict())
    db.add(db_conferma)
    try:
        db.commit()
        db.refresh(db_conferma)
        return db_conferma
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# ==================== FATTURE ====================
@app.get("/api/fatture", response_model=List[FatturaResponse])
def get_fatture(
    skip: int = 0,
    limit: int = 100,
    data_da: Optional[str] = None,
    data_a: Optional[str] = None,
    cliente_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Recupera fatture con filtri per date e cliente"""
    query = db.query(Fattura)
    
    if data_da:
        query = query.filter(Fattura.data_fattura >= data_da)
    if data_a:
        query = query.filter(Fattura.data_fattura <= data_a)
    if cliente_id:
        query = query.filter(Fattura.cliente_id == cliente_id)
    
    return query.offset(skip).limit(limit).all()


@app.post("/api/fatture/genera", response_model=List[FatturaResponse])
def genera_fatture(
    mesi: List[str],
    anno: int,
    db: Session = Depends(get_db)
):
    """
    Genera fatture per i mesi specificati
    Logica: per ogni mese, crea fatture per venditori con consegne
    """
    fatture_create = []
    
    for mese in mesi:
        # Query per trovare venditori con consegne nel mese
        query = """
        SELECT DISTINCT venditore_id
        FROM conferme_ordine co
        JOIN date_consegna dc ON co.id = dc.conferma_ordine_id
        WHERE strftime('%m', dc.data_consegna) = :mese
        AND strftime('%Y', dc.data_consegna) = :anno
        """
        
        result = db.execute(query, {"mese": mese, "anno": str(anno)})
        venditori_ids = [row[0] for row in result]
        
        for venditore_id in venditori_ids:
            # Crea fattura per questo venditore/mese
            fattura = Fattura(
                numero_fattura=f"{venditore_id}/{mese}/{anno}",
                data_fattura=f"01/{mese}/{anno}",
                cliente_id=venditore_id,
                pagata=False
            )
            db.add(fattura)
            fatture_create.append(fattura)
    
    try:
        db.commit()
        for f in fatture_create:
            db.refresh(f)
        return fatture_create
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# ==================== HEALTH CHECK ====================
@app.get("/health")
def health_check():
    """Verifica stato API"""
    return {"status": "healthy", "service": "GestyBrok API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
