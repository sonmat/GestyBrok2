"""
Backend API per db_gesty.db esistente
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import get_db, init_db
from models import (
    TArticolo, TVenditore, TCompratore, TConferma,
    TFatturaStudio, TFatturaStudioDet, TDataConsegna, TFattura,
    TDatiVenditore, TDatiCompratore, TIva, TPagamento, TBanca
)
from pdf_generator import PDFConfermaOrdine
from pdf_report_generator import PDFReportGenerator

# Connetti al database
init_db()

app = FastAPI(title="GestyBrok API", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ARTICOLI ====================
@app.get("/api/articoli")
def get_articoli(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    """Lista articoli"""
    # ORDER BY per mostrare anche i nuovi articoli
    articoli = db.query(TArticolo).order_by(TArticolo.id_articolo.desc()).offset(skip).limit(limit).all()
    
    print(f"DEBUG BACKEND: Query restituisce {len(articoli)} articoli")
    if articoli:
        print(f"  Primo: ID={articoli[0].id_articolo}, Nome={articoli[0].nome_articolo}")
        print(f"  Ultimo: ID={articoli[-1].id_articolo}, Nome={articoli[-1].nome_articolo}")
    
    result = [
        {
            "id": a.id_articolo,
            "nome": a.nome_articolo,
            "codice": str(a.id_articolo),
            "unita_misura": a.unita_misura,
            "tipo_id": a.tipologia,
            "famiglia_id": a.famiglia,
            "descrizione": "",
            "attivo": True
        }
        for a in articoli
    ]
    
    print(f"DEBUG BACKEND: Restituisco {len(result)} articoli al frontend")
    
    return result


@app.get("/api/articoli/{articolo_id}")
def get_articolo(articolo_id: int, db: Session = Depends(get_db)):
    """Singolo articolo"""
    a = db.query(TArticolo).filter(TArticolo.id_articolo == articolo_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Non trovato")
    return {
        "id": a.id_articolo,
        "nome": a.nome_articolo,
        "codice": str(a.id_articolo),
        "unita_misura": a.unita_misura,
        "tipo_id": a.tipologia,
        "famiglia_id": a.famiglia,
        "descrizione": "",
        "attivo": True
    }


@app.post("/api/articoli", status_code=201)
def create_articolo(data: dict, db: Session = Depends(get_db)):
    """Crea articolo"""
    nuovo = TArticolo(
        nome_articolo=data["nome"],
        unita_misura=data.get("unita_misura"),
        famiglia=data.get("famiglia_id"),
        tipologia=data.get("tipo_id")
    )
    db.add(nuovo)
    db.commit()
    db.refresh(nuovo)
    return {"id": nuovo.id_articolo, "nome": nuovo.nome_articolo}


@app.put("/api/articoli/{articolo_id}")
def update_articolo(articolo_id: int, data: dict, db: Session = Depends(get_db)):
    """Aggiorna articolo"""
    a = db.query(TArticolo).filter(TArticolo.id_articolo == articolo_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Non trovato")
    
    a.nome_articolo = data.get("nome", a.nome_articolo)
    a.unita_misura = data.get("unita_misura", a.unita_misura)
    a.famiglia = data.get("famiglia_id", a.famiglia)
    a.tipologia = data.get("tipo_id", a.tipologia)
    
    db.commit()
    return {"id": a.id_articolo, "nome": a.nome_articolo}


@app.delete("/api/articoli/{articolo_id}", status_code=204)
def delete_articolo(articolo_id: int, db: Session = Depends(get_db)):
    """Elimina articolo"""
    a = db.query(TArticolo).filter(TArticolo.id_articolo == articolo_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Non trovato")
    db.delete(a)
    db.commit()


# ==================== VENDITORI ====================
@app.get("/api/venditori")
def get_venditori(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista venditori"""
    venditori = db.query(TVenditore).offset(skip).limit(limit).all()
    return [
        {
            "id": v.id_venditore,
            "codice": str(v.id_venditore),
            "azienda": v.azienda or "",
            "partita_iva": v.piva or "",
            "indirizzo": v.indirizzo or "",
            "cap": v.cap or "",
            "citta": v.citta or "",
            "telefono": v.telefono or "",
            "fax": v.fax or "",
            "email": "",
            "italiano": v.italiano == "Si",
            "attivo": True
        }
        for v in venditori
    ]


@app.get("/api/venditori/{venditore_id}")
def get_venditore(venditore_id: int, db: Session = Depends(get_db)):
    """Dettaglio venditore"""
    venditore = db.query(TVenditore).filter(TVenditore.id_venditore == venditore_id).first()
    if not venditore:
        raise HTTPException(status_code=404, detail="Venditore non trovato")

    return {
        "id": venditore.id_venditore,
        "codice": str(venditore.id_venditore),
        "azienda": venditore.azienda or "",
        "partita_iva": venditore.piva or "",
        "indirizzo": venditore.indirizzo or "",
        "cap": venditore.cap or "",
        "citta": venditore.citta or "",
        "telefono": venditore.telefono or "",
        "fax": venditore.fax or "",
        "italiano": venditore.italiano == "Si"
    }


@app.post("/api/venditori", status_code=201)
def create_venditore(data: dict, db: Session = Depends(get_db)):
    """Crea venditore"""
    nuovo = TVenditore(
        azienda=data["azienda"],
        piva=data.get("partita_iva"),
        indirizzo=data.get("indirizzo"),
        cap=data.get("cap"),
        citta=data.get("citta"),
        telefono=data.get("telefono"),
        fax=data.get("fax"),
        italiano="Si" if data.get("italiano", True) else "No"
    )
    db.add(nuovo)
    db.commit()
    db.refresh(nuovo)
    return {"id": nuovo.id_venditore, "azienda": nuovo.azienda}


@app.put("/api/venditori/{venditore_id}")
def update_venditore(venditore_id: int, data: dict, db: Session = Depends(get_db)):
    """Aggiorna venditore"""
    v = db.query(TVenditore).filter(TVenditore.id_venditore == venditore_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Non trovato")
    
    v.azienda = data.get("azienda", v.azienda)
    v.piva = data.get("partita_iva", v.piva)
    v.indirizzo = data.get("indirizzo", v.indirizzo)
    v.cap = data.get("cap", v.cap)
    v.citta = data.get("citta", v.citta)
    v.telefono = data.get("telefono", v.telefono)
    v.italiano = "Si" if data.get("italiano", True) else "No"
    
    db.commit()
    return {"id": v.id_venditore, "azienda": v.azienda}


@app.delete("/api/venditori/{venditore_id}", status_code=204)
def delete_venditore(venditore_id: int, db: Session = Depends(get_db)):
    """Elimina venditore"""
    v = db.query(TVenditore).filter(TVenditore.id_venditore == venditore_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Non trovato")
    db.delete(v)
    db.commit()


# ==================== DATI VENDITORI ====================
@app.get("/api/dati-venditori")
def get_dati_venditori(id_venditore: Optional[int] = None, db: Session = Depends(get_db)):
    """Lista dati venditori (opzionalmente filtrati per venditore)"""
    query = db.query(TDatiVenditore)
    if id_venditore:
        query = query.filter(TDatiVenditore.id_venditore == id_venditore)

    dati = query.all()
    return [
        {
            "id_dati_venditore": d.id_dati_venditore,
            "id_venditore": d.id_venditore,
            "mail": d.mail or "",
            "fax": d.fax or "",
            "telefono": d.telefono or "",
            "ntel_tipologia": d.ntel_tipologia or "",
            "contatto": d.contatto or ""
        }
        for d in dati
    ]


@app.get("/api/dati-venditori/{dato_id}")
def get_dato_venditore(dato_id: int, db: Session = Depends(get_db)):
    """Singolo dato venditore"""
    d = db.query(TDatiVenditore).filter(TDatiVenditore.id_dati_venditore == dato_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Non trovato")

    return {
        "id_dati_venditore": d.id_dati_venditore,
        "id_venditore": d.id_venditore,
        "mail": d.mail or "",
        "fax": d.fax or "",
        "telefono": d.telefono or "",
        "ntel_tipologia": d.ntel_tipologia or "",
        "contatto": d.contatto or ""
    }


@app.post("/api/dati-venditori", status_code=201)
def create_dato_venditore(data: dict, db: Session = Depends(get_db)):
    """Crea dato venditore"""
    nuovo = TDatiVenditore(
        id_venditore=data["id_venditore"],
        mail=data.get("mail"),
        fax=data.get("fax"),
        telefono=data.get("telefono"),
        ntel_tipologia=data.get("ntel_tipologia"),
        contatto=data.get("contatto")
    )
    db.add(nuovo)
    db.commit()
    db.refresh(nuovo)
    return {"id": nuovo.id_dati_venditore}


@app.put("/api/dati-venditori/{dato_id}")
def update_dato_venditore(dato_id: int, data: dict, db: Session = Depends(get_db)):
    """Aggiorna dato venditore"""
    d = db.query(TDatiVenditore).filter(TDatiVenditore.id_dati_venditore == dato_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Non trovato")

    d.mail = data.get("mail", d.mail)
    d.fax = data.get("fax", d.fax)
    d.telefono = data.get("telefono", d.telefono)
    d.ntel_tipologia = data.get("ntel_tipologia", d.ntel_tipologia)
    d.contatto = data.get("contatto", d.contatto)

    db.commit()
    return {"id": d.id_dati_venditore}


@app.delete("/api/dati-venditori/{dato_id}", status_code=204)
def delete_dato_venditore(dato_id: int, db: Session = Depends(get_db)):
    """Elimina dato venditore"""
    d = db.query(TDatiVenditore).filter(TDatiVenditore.id_dati_venditore == dato_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Non trovato")
    db.delete(d)
    db.commit()


# ==================== COMPRATORI ====================
@app.get("/api/compratori")
def get_compratori(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista compratori"""
    compratori = db.query(TCompratore).offset(skip).limit(limit).all()
    return [
        {
            "id": c.id_compratore,
            "codice": str(c.id_compratore),
            "azienda": c.azienda or "",
            "partita_iva": c.piva or "",
            "citta": c.citta or "",
            "telefono": c.telefono or "",
            "attivo": True
        }
        for c in compratori
    ]


@app.get("/api/compratori/{compratore_id}")
def get_compratore(compratore_id: int, db: Session = Depends(get_db)):
    """Dettaglio compratore"""
    compratore = db.query(TCompratore).filter(TCompratore.id_compratore == compratore_id).first()
    if not compratore:
        raise HTTPException(status_code=404, detail="Compratore non trovato")

    return {
        "id": compratore.id_compratore,
        "codice": str(compratore.id_compratore),
        "azienda": compratore.azienda or "",
        "partita_iva": compratore.piva or "",
        "citta": compratore.citta or "",
        "telefono": compratore.telefono or "",
        "attivo": True
    }


@app.post("/api/compratori", status_code=201)
def create_compratore(data: dict, db: Session = Depends(get_db)):
    """Crea compratore"""
    nuovo = TCompratore(
        azienda=data["azienda"],
        piva=data.get("partita_iva"),
        citta=data.get("citta"),
        telefono=data.get("telefono")
    )
    db.add(nuovo)
    db.commit()
    db.refresh(nuovo)
    return {"id": nuovo.id_compratore, "azienda": nuovo.azienda}


@app.put("/api/compratori/{compratore_id}")
def update_compratore(compratore_id: int, data: dict, db: Session = Depends(get_db)):
    """Aggiorna compratore"""
    c = db.query(TCompratore).filter(TCompratore.id_compratore == compratore_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Non trovato")
    
    c.azienda = data.get("azienda", c.azienda)
    c.piva = data.get("partita_iva", c.piva)
    c.citta = data.get("citta", c.citta)
    c.telefono = data.get("telefono", c.telefono)
    
    db.commit()
    return {"id": c.id_compratore, "azienda": c.azienda}


@app.delete("/api/compratori/{compratore_id}", status_code=204)
def delete_compratore(compratore_id: int, db: Session = Depends(get_db)):
    """Elimina compratore"""
    c = db.query(TCompratore).filter(TCompratore.id_compratore == compratore_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Non trovato")
    db.delete(c)
    db.commit()


# ==================== DATI COMPRATORI ====================
@app.get("/api/dati-compratori")
def get_dati_compratori(id_compratore: Optional[int] = None, db: Session = Depends(get_db)):
    """Lista dati compratori (opzionalmente filtrati per compratore)"""
    query = db.query(TDatiCompratore)
    if id_compratore:
        query = query.filter(TDatiCompratore.id_compratore == id_compratore)

    dati = query.all()
    return [
        {
            "id_dati_compratore": d.id_dati_compratore,
            "id_compratore": d.id_compratore,
            "mail": d.mail or "",
            "fax": d.fax or "",
            "telefono": d.telefono or "",
            "ntel_tipologia": d.ntel_tipologia or "",
            "contatto": d.contatto or ""
        }
        for d in dati
    ]


@app.get("/api/dati-compratori/{dato_id}")
def get_dato_compratore(dato_id: int, db: Session = Depends(get_db)):
    """Singolo dato compratore"""
    d = db.query(TDatiCompratore).filter(TDatiCompratore.id_dati_compratore == dato_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Non trovato")

    return {
        "id_dati_compratore": d.id_dati_compratore,
        "id_compratore": d.id_compratore,
        "mail": d.mail or "",
        "fax": d.fax or "",
        "telefono": d.telefono or "",
        "ntel_tipologia": d.ntel_tipologia or "",
        "contatto": d.contatto or ""
    }


@app.post("/api/dati-compratori", status_code=201)
def create_dato_compratore(data: dict, db: Session = Depends(get_db)):
    """Crea dato compratore"""
    nuovo = TDatiCompratore(
        id_compratore=data["id_compratore"],
        mail=data.get("mail"),
        fax=data.get("fax"),
        telefono=data.get("telefono"),
        ntel_tipologia=data.get("ntel_tipologia"),
        contatto=data.get("contatto")
    )
    db.add(nuovo)
    db.commit()
    db.refresh(nuovo)
    return {"id": nuovo.id_dati_compratore}


@app.put("/api/dati-compratori/{dato_id}")
def update_dato_compratore(dato_id: int, data: dict, db: Session = Depends(get_db)):
    """Aggiorna dato compratore"""
    d = db.query(TDatiCompratore).filter(TDatiCompratore.id_dati_compratore == dato_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Non trovato")

    d.mail = data.get("mail", d.mail)
    d.fax = data.get("fax", d.fax)
    d.telefono = data.get("telefono", d.telefono)
    d.ntel_tipologia = data.get("ntel_tipologia", d.ntel_tipologia)
    d.contatto = data.get("contatto", d.contatto)

    db.commit()
    return {"id": d.id_dati_compratore}


@app.delete("/api/dati-compratori/{dato_id}", status_code=204)
def delete_dato_compratore(dato_id: int, db: Session = Depends(get_db)):
    """Elimina dato compratore"""
    d = db.query(TDatiCompratore).filter(TDatiCompratore.id_dati_compratore == dato_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Non trovato")
    db.delete(d)
    db.commit()


# ==================== CONFERME ORDINE ====================
def parse_float(value):
    """Converte stringhe con formato europeo in float"""
    if not value:
        return 0.0
    try:
        # Rimuovi simboli € e spazi, sostituisci virgola con punto
        clean = str(value).replace('€', '').replace(' ', '').replace(',', '.')
        return float(clean)
    except:
        return 0.0


@app.get("/api/conferme-ordine")
def get_conferme_ordine(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    """Lista conferme con nomi al posto di ID"""
    conferme = db.query(TConferma).order_by(TConferma.id_conferma.desc()).offset(skip).limit(limit).all()

    result = []
    for c in conferme:
        # Recupera nomi dalle relazioni
        venditore = db.query(TVenditore).filter(TVenditore.id_venditore == c.venditore).first()
        compratore = db.query(TCompratore).filter(TCompratore.id_compratore == c.compratore).first()
        articolo = db.query(TArticolo).filter(TArticolo.id_articolo == c.articolo).first()
        pagamento = db.query(TPagamento).filter(TPagamento.id_pagamento == c.condizioni_pag).first()

        result.append({
            "id": c.id_conferma,
            "n_conf": c.n_conf or "",
            "data_conf": c.data_conf or "",
            "numero_conferma": c.n_conf or "",
            "data_conferma": c.data_conf or "",
            "venditore_id": c.venditore,
            "venditore_nome": venditore.azienda if venditore else f"ID: {c.venditore}",
            "compratore_id": c.compratore,
            "compratore_nome": compratore.azienda if compratore else f"ID: {c.compratore}",
            "articolo_id": c.articolo,
            "articolo_nome": articolo.nome_articolo if articolo else f"ID: {c.articolo}",
            "qta": c.qta or "",
            "quantita": parse_float(c.qta),
            "prezzo": c.prezzo or "",
            "provvigione": c.provvigione or "",
            "tipologia": c.tipologia or "",
            "luogo_consegna": c.luogo_consegna or "",
            "condizioni_pag": pagamento.tipo_pagamento if pagamento else (str(c.condizioni_pag) if c.condizioni_pag else ""),
            "condizioni_pag_id": c.condizioni_pag,
            "carico": c.carico or "",
            "arrivo": c.arrivo or "",
            "emailv": c.emailv or "",
            "emailc": c.emailc or "",
            "note": c.note or ""
        })

    return result


@app.get("/api/conferme-ordine/{conferma_id}")
def get_conferma_ordine(conferma_id: int, db: Session = Depends(get_db)):
    """Ottiene singola conferma ordine"""
    c = db.query(TConferma).filter(TConferma.id_conferma == conferma_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conferma non trovata")

    # Recupera il nome del pagamento
    pagamento = db.query(TPagamento).filter(TPagamento.id_pagamento == c.condizioni_pag).first()

    return {
        "id": c.id_conferma,
        "n_conf": c.n_conf or "",
        "data_conf": c.data_conf or "",
        "numero_conferma": c.n_conf or "",
        "data_conferma": c.data_conf or "",
        "venditore_id": c.venditore,
        "compratore_id": c.compratore,
        "articolo_id": c.articolo,
        "qta": c.qta or "",
        "quantita": parse_float(c.qta),
        "prezzo": c.prezzo or "",
        "provvigione": c.provvigione or "",
        "tipologia": c.tipologia or "",
        "luogo_consegna": c.luogo_consegna or "",
        "condizioni_pag": pagamento.tipo_pagamento if pagamento else (str(c.condizioni_pag) if c.condizioni_pag else ""),
        "condizioni_pag_id": c.condizioni_pag,
        "carico": c.carico or "",
        "arrivo": c.arrivo or "",
        "emailv": c.emailv or "",
        "emailc": c.emailc or "",
        "note": c.note or ""
    }


@app.post("/api/conferme-ordine", status_code=201)
def create_conferma_ordine(data: dict, db: Session = Depends(get_db)):
    """Crea conferma"""
    nuova = TConferma(
        n_conf=data.get("numero_conferma"),
        data_conf=data.get("data_conferma"),
        venditore=data["venditore_id"],
        compratore=data["compratore_id"],
        articolo=data["articolo_id"],
        qta=str(data["quantita"]),
        prezzo=str(data["prezzo"]),
        provvigione=str(data.get("provvigione", 0)),
        tipologia=data.get("tipologia"),
        note=data.get("note")
    )
    db.add(nuova)
    db.commit()
    db.refresh(nuova)
    return {"id": nuova.id_conferma}


@app.put("/api/conferme-ordine/{conferma_id}")
def update_conferma_ordine(conferma_id: int, data: dict, db: Session = Depends(get_db)):
    """Aggiorna conferma ordine"""
    c = db.query(TConferma).filter(TConferma.id_conferma == conferma_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conferma non trovata")

    c.n_conf = data.get("numero_conferma")
    c.data_conf = data.get("data_conferma")
    c.venditore = data["venditore_id"]
    c.compratore = data["compratore_id"]
    c.articolo = data["articolo_id"]
    c.qta = str(data["quantita"])
    c.prezzo = str(data["prezzo"])
    c.provvigione = str(data.get("provvigione", 0))
    c.tipologia = data.get("tipologia")
    c.note = data.get("note")

    db.commit()
    return {"id": c.id_conferma}


@app.delete("/api/conferme-ordine/{conferma_id}", status_code=204)
def delete_conferma_ordine(conferma_id: int, db: Session = Depends(get_db)):
    """Elimina conferma ordine"""
    c = db.query(TConferma).filter(TConferma.id_conferma == conferma_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conferma non trovata")
    db.delete(c)
    db.commit()


@app.get("/api/conferme-ordine/{conferma_id}/stampa-venditore")
def stampa_conferma_venditore(conferma_id: int, db: Session = Depends(get_db)):
    """
    Genera e scarica il PDF della conferma d'ordine per il venditore

    Restituisce il PDF in italiano se il venditore è italiano, altrimenti in inglese
    """
    # Recupera la conferma
    conferma = db.query(TConferma).filter(TConferma.id_conferma == conferma_id).first()
    if not conferma:
        raise HTTPException(status_code=404, detail="Conferma non trovata")

    # Recupera il venditore
    venditore = db.query(TVenditore).filter(TVenditore.id_venditore == conferma.venditore).first()
    if not venditore:
        raise HTTPException(status_code=404, detail="Venditore non trovato")

    # Recupera il compratore
    compratore = db.query(TCompratore).filter(TCompratore.id_compratore == conferma.compratore).first()
    if not compratore:
        raise HTTPException(status_code=404, detail="Compratore non trovato")

    # Recupera l'articolo
    articolo = db.query(TArticolo).filter(TArticolo.id_articolo == conferma.articolo).first()
    if not articolo:
        raise HTTPException(status_code=404, detail="Articolo non trovato")

    # Recupera le date di consegna
    date_consegna = db.query(TDataConsegna).filter(
        TDataConsegna.id_conferma == conferma_id
    ).order_by(TDataConsegna.data_consegna).all()

    # Prepara i dati
    conferma_data = {
        'id_conferma': conferma.id_conferma,
        'n_conf': conferma.n_conf,
        'data_conf': conferma.data_conf,
        'numero_conferma': conferma.n_conf,
        'data_conferma': conferma.data_conf,
        'quantita': parse_float(conferma.qta),
        'qta': parse_float(conferma.qta),
        'prezzo': parse_float(conferma.prezzo),
        'provvigione': parse_float(conferma.provvigione) if conferma.provvigione else None,
        'tipologia': conferma.tipologia,
        'note': conferma.note
    }

    venditore_data = {
        'id': venditore.id_venditore,
        'azienda': venditore.azienda or '',
        'indirizzo': venditore.indirizzo or '',
        'cap': venditore.cap or '',
        'citta': venditore.citta or '',
        'piva': venditore.piva or '',
        'partita_iva': venditore.piva or '',
        'telefono': venditore.telefono or '',
        'italiano': venditore.italiano or 'Si'
    }

    compratore_data = {
        'id': compratore.id_compratore,
        'azienda': compratore.azienda or '',
        'indirizzo': compratore.indirizzo or '',
        'cap': compratore.cap or '',
        'citta': compratore.citta or '',
        'piva': compratore.piva or '',
        'partita_iva': compratore.piva or '',
        'telefono': compratore.telefono or '',
        'italiano': compratore.italiano or 'Si'
    }

    articolo_data = {
        'id': articolo.id_articolo,
        'nome': articolo.nome_articolo or '',
        'nome_articolo': articolo.nome_articolo or '',
        'unita_misura': articolo.unita_misura or ''
    }

    date_consegna_data = []
    for dc in date_consegna:
        date_consegna_data.append({
            'data_consegna': dc.data_consegna,
            'qta_consegna': dc.qta_consegna
        })

    # Genera il PDF
    pdf_gen = PDFConfermaOrdine()
    pdf_buffer = pdf_gen.genera_conferma_venditore(
        conferma_data,
        venditore_data,
        compratore_data,
        articolo_data,
        date_consegna_data if date_consegna_data else None
    )

    # Nome file
    is_estero = venditore.italiano != 'Si'
    lang_suffix = '_EN' if is_estero else '_IT'
    filename = f"Conferma_Venditore_{conferma.n_conf or conferma_id}{lang_suffix}.pdf"

    # Restituisce il PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@app.get("/api/conferme-ordine/{conferma_id}/stampa-compratore")
def stampa_conferma_compratore(conferma_id: int, db: Session = Depends(get_db)):
    """
    Genera e scarica il PDF della conferma d'ordine per il compratore

    Restituisce il PDF in italiano se il compratore è italiano, altrimenti in inglese
    """
    # Recupera la conferma
    conferma = db.query(TConferma).filter(TConferma.id_conferma == conferma_id).first()
    if not conferma:
        raise HTTPException(status_code=404, detail="Conferma non trovata")

    # Recupera il venditore
    venditore = db.query(TVenditore).filter(TVenditore.id_venditore == conferma.venditore).first()
    if not venditore:
        raise HTTPException(status_code=404, detail="Venditore non trovato")

    # Recupera il compratore
    compratore = db.query(TCompratore).filter(TCompratore.id_compratore == conferma.compratore).first()
    if not compratore:
        raise HTTPException(status_code=404, detail="Compratore non trovato")

    # Recupera l'articolo
    articolo = db.query(TArticolo).filter(TArticolo.id_articolo == conferma.articolo).first()
    if not articolo:
        raise HTTPException(status_code=404, detail="Articolo non trovato")

    # Recupera le date di consegna
    date_consegna = db.query(TDataConsegna).filter(
        TDataConsegna.id_conferma == conferma_id
    ).order_by(TDataConsegna.data_consegna).all()

    # Prepara i dati
    conferma_data = {
        'id_conferma': conferma.id_conferma,
        'n_conf': conferma.n_conf,
        'data_conf': conferma.data_conf,
        'numero_conferma': conferma.n_conf,
        'data_conferma': conferma.data_conf,
        'quantita': parse_float(conferma.qta),
        'qta': parse_float(conferma.qta),
        'prezzo': parse_float(conferma.prezzo),
        'provvigione': parse_float(conferma.provvigione) if conferma.provvigione else None,
        'tipologia': conferma.tipologia,
        'note': conferma.note
    }

    venditore_data = {
        'id': venditore.id_venditore,
        'azienda': venditore.azienda or '',
        'indirizzo': venditore.indirizzo or '',
        'cap': venditore.cap or '',
        'citta': venditore.citta or '',
        'piva': venditore.piva or '',
        'partita_iva': venditore.piva or '',
        'telefono': venditore.telefono or '',
        'italiano': venditore.italiano or 'Si'
    }

    compratore_data = {
        'id': compratore.id_compratore,
        'azienda': compratore.azienda or '',
        'indirizzo': compratore.indirizzo or '',
        'cap': compratore.cap or '',
        'citta': compratore.citta or '',
        'piva': compratore.piva or '',
        'partita_iva': compratore.piva or '',
        'telefono': compratore.telefono or '',
        'italiano': compratore.italiano or 'Si'
    }

    articolo_data = {
        'id': articolo.id_articolo,
        'nome': articolo.nome_articolo or '',
        'nome_articolo': articolo.nome_articolo or '',
        'unita_misura': articolo.unita_misura or ''
    }

    date_consegna_data = []
    for dc in date_consegna:
        date_consegna_data.append({
            'data_consegna': dc.data_consegna,
            'qta_consegna': dc.qta_consegna
        })

    # Genera il PDF
    pdf_gen = PDFConfermaOrdine()
    pdf_buffer = pdf_gen.genera_conferma_compratore(
        conferma_data,
        venditore_data,
        compratore_data,
        articolo_data,
        date_consegna_data if date_consegna_data else None
    )

    # Nome file
    is_estero = compratore.italiano != 'Si'
    lang_suffix = '_EN' if is_estero else '_IT'
    filename = f"Conferma_Compratore_{conferma.n_conf or conferma_id}{lang_suffix}.pdf"

    # Restituisce il PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

# ==================== DATE CONSEGNA ====================
@app.get("/api/conferme-ordine/{id_conferma}/date-consegna")
def get_date_consegna_conferma(id_conferma: int, db: Session = Depends(get_db)):
    """Ottiene tutte le date di consegna per una conferma ordine"""
    date_consegna = db.query(TDataConsegna).filter(
        TDataConsegna.id_conferma == id_conferma
    ).order_by(TDataConsegna.data_consegna).all()
    
    # Restituisce un dizionario con lista di date
    date_uniche = list(set([d.data_consegna for d in date_consegna if d.data_consegna]))
    date_uniche.sort()
    
    return {"date": date_uniche}


@app.get("/api/date-consegna/by-conferma/{id_conferma}")
def get_date_consegna_full(id_conferma: int, db: Session = Depends(get_db)):
    """Ottiene tutti i record delle date di consegna con dettagli"""
    date_consegna = db.query(TDataConsegna).filter(
        TDataConsegna.id_conferma == id_conferma
    ).all()
    
    result = []
    for dc in date_consegna:
        result.append({
            "id": dc.id_data_consegna,
            "data_consegna": dc.data_consegna,
            "qta_consegna": dc.qta_consegna
        })
    
    return result

@app.post("/api/date-consegna", status_code=201)
def create_data_consegna(data: dict, db: Session = Depends(get_db)):
    """Crea una nuova data di consegna"""
    nuova = TDataConsegna(
        id_conferma=data["conferma_id"],
        data_consegna=data["data_consegna"],
        qta_consegna=str(data.get("qta_consegna", ""))
    )
    db.add(nuova)
    db.commit()
    db.refresh(nuova)
    return {"id": nuova.id_data_consegna}


@app.get("/api/date-consegna/{id_data}")
def get_data_consegna(id_data: int, db: Session = Depends(get_db)):
    """Ottiene singola data di consegna"""
    data_consegna = db.query(TDataConsegna).filter(
        TDataConsegna.id_data_consegna == id_data
    ).first()
    if not data_consegna:
        raise HTTPException(status_code=404, detail="Data consegna non trovata")
    return {
        "id": data_consegna.id_data_consegna,
        "conferma_id": data_consegna.id_conferma,
        "data_consegna": data_consegna.data_consegna,
        "qta_consegna": data_consegna.qta_consegna
    }


@app.put("/api/date-consegna/{id_data}")
def update_data_consegna(id_data: int, data: dict, db: Session = Depends(get_db)):
    """Aggiorna data di consegna"""
    data_consegna = db.query(TDataConsegna).filter(
        TDataConsegna.id_data_consegna == id_data
    ).first()
    if not data_consegna:
        raise HTTPException(status_code=404, detail="Data consegna non trovata")

    data_consegna.data_consegna = data["data_consegna"]
    data_consegna.qta_consegna = str(data.get("qta_consegna", ""))

    db.commit()
    return {"id": data_consegna.id_data_consegna}


@app.delete("/api/date-consegna/{id_data}", status_code=204)
def delete_data_consegna(id_data: int, db: Session = Depends(get_db)):
    """Elimina una data di consegna"""
    data_consegna = db.query(TDataConsegna).filter(
        TDataConsegna.id_data_consegna == id_data
    ).first()
    if not data_consegna:
        raise HTTPException(status_code=404, detail="Data consegna non trovata")
    db.delete(data_consegna)
    db.commit()
# ==================== FATTURE ====================

@app.get("/api/conferme-ordine/{id_conferma}/fatture")
def get_fatture_conferma(id_conferma: int, db: Session = Depends(get_db)):
    """Ottiene le fatture associate a una conferma ordine dalla tabella t_fatture"""
    fatture = db.query(TFattura).filter(
        TFattura.confermaordine == id_conferma
    ).all()

    result = []
    for f in fatture:
        # Calcola importo se disponibili qta e prezzo
        importo = 0
        if f.qta and f.prezzo:
            try:
                importo = float(f.qta) * float(f.prezzo)
            except:
                importo = 0

        result.append({
            "id_fattura": f.id_fattura if f.id_fattura is not None else "",
            "n_fat": str(f.n_fat) if f.n_fat is not None else "",
            "data_fat": str(f.data_fat) if f.data_fat is not None else "",
            "nota_acr": str(f.nota_acr) if f.nota_acr is not None else "",
            "articolo": str(f.articolo) if f.articolo is not None else "",
            "qta": str(f.qta) if f.qta is not None else "",
            "prezzo": str(f.prezzo) if f.prezzo is not None else "",
            "iva_perc": str(f.iva_perc) if f.iva_perc is not None else "",
            "data_consegna": str(f.data_consegna) if f.data_consegna is not None else "",
            "compilato": f.compilato if f.compilato is not None else "",
            "fatturata": f.fatturata if f.fatturata is not None else "",
            "importo": importo
        })

    return result

@app.get("/api/fatture")
def get_fatture(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista fatture con nome cliente"""
    fatture = db.query(TFatturaStudio).offset(skip).limit(limit).all()

    result = []
    for f in fatture:
        # Recupera nome cliente (può essere venditore o compratore)
        cliente_nome = ""
        if f.cliente:
            # Prova prima nei venditori
            venditore = db.query(TVenditore).filter(TVenditore.id_venditore == f.cliente).first()
            if venditore:
                cliente_nome = venditore.azienda
            else:
                # Prova nei compratori
                compratore = db.query(TCompratore).filter(TCompratore.id_compratore == f.cliente).first()
                if compratore:
                    cliente_nome = compratore.azienda
                else:
                    cliente_nome = f"ID: {f.cliente}"

        result.append({
            "id": f.id_fatt_studio,
            "numero_fattura": str(f.n_fat) if f.n_fat else "",
            "data_fattura": str(f.data_fat) if f.data_fat else "",
            "cliente_id": f.cliente,
            "cliente_nome": cliente_nome,
            "importo_totale": 0,
            "pagata": False,
            "data_pagamento": ""
        })

    return result


@app.post("/api/fatture/genera")
def genera_fatture(data: dict, db: Session = Depends(get_db)):
    """Genera fatture"""
    mesi = data.get("mesi", [])
    anno = data.get("anno", 2024)
    # Logica generazione fatture da implementare
    return []


# ==================== HEALTH ====================
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ==================== TIPOLOGIE E FAMIGLIE ====================
@app.get("/api/tipologie")
def get_tipologie(db: Session = Depends(get_db)):
    """Lista tipologie"""
    from models import TTipoArticolo
    tipi = db.query(TTipoArticolo).all()
    return [t.tipologia for t in tipi if t.tipologia]


@app.post("/api/tipologie", status_code=201)
def create_tipologia(data: dict, db: Session = Depends(get_db)):
    """Crea tipologia"""
    from models import TTipoArticolo
    nuova = TTipoArticolo(tipologia=data["nome"])
    db.add(nuova)
    db.commit()
    return {"nome": data["nome"]}


@app.delete("/api/tipologie/{nome}", status_code=204)
def delete_tipologia(nome: str, db: Session = Depends(get_db)):
    """Elimina tipologia"""
    from models import TTipoArticolo
    tipo = db.query(TTipoArticolo).filter(TTipoArticolo.tipologia == nome).first()
    if tipo:
        db.delete(tipo)
        db.commit()


@app.get("/api/famiglie")
def get_famiglie(db: Session = Depends(get_db)):
    """Lista famiglie"""
    from models import TFamigliaArticolo
    famiglie = db.query(TFamigliaArticolo).all()
    return [f.famiglia for f in famiglie if f.famiglia]


@app.post("/api/famiglie", status_code=201)
def create_famiglia(data: dict, db: Session = Depends(get_db)):
    """Crea famiglia"""
    from models import TFamigliaArticolo
    nuova = TFamigliaArticolo(famiglia=data["nome"])
    db.add(nuova)
    db.commit()
    return {"nome": data["nome"]}


@app.delete("/api/famiglie/{nome}", status_code=204)
def delete_famiglia(nome: str, db: Session = Depends(get_db)):
    """Elimina famiglia"""
    from models import TFamigliaArticolo
    fam = db.query(TFamigliaArticolo).filter(TFamigliaArticolo.famiglia == nome).first()
    if fam:
        db.delete(fam)
        db.commit()


# ==================== CHI OFFRE / CHI CERCA ====================
@app.get("/api/articoli/{articolo_id}/offre")
def get_articolo_offre(articolo_id: int, db: Session = Depends(get_db)):
    """Chi offre questo articolo"""
    from models import TVenditoreOffre
    offerte = db.query(TVenditoreOffre).filter(TVenditoreOffre.articolo == articolo_id).all()
    
    result = []
    for o in offerte:
        venditore = db.query(TVenditore).filter(TVenditore.id_venditore == o.venditore).first()
        result.append({
            "venditore_id": o.venditore,
            "venditore_nome": venditore.azienda if venditore else "",
            "prezzo": o.prezzo,
            "provvigione": o.provvigione,
            "tipologia": o.tipologia
        })
    return result


@app.get("/api/articoli/{articolo_id}/cerca")
def get_articolo_cerca(articolo_id: int, db: Session = Depends(get_db)):
    """Chi cerca questo articolo"""
    from models import TCompratoreCerca
    ricerche = db.query(TCompratoreCerca).filter(TCompratoreCerca.articolo == articolo_id).all()
    
    result = []
    for r in ricerche:
        compratore = db.query(TCompratore).filter(TCompratore.id_compratore == r.compratore).first()
        result.append({
            "compratore_id": r.compratore,
            "compratore_nome": compratore.azienda if compratore else "",
            "note": r.note
        })
    return result


@app.get("/api/venditori/{venditore_id}/offre")
def get_venditore_offre(venditore_id: int, db: Session = Depends(get_db)):
    """Cosa offre questo venditore"""
    from models import TVenditoreOffre
    offerte = db.query(TVenditoreOffre).filter(TVenditoreOffre.venditore == venditore_id).all()
    
    result = []
    for o in offerte:
        articolo = db.query(TArticolo).filter(TArticolo.id_articolo == o.articolo).first()
        result.append({
            "id": o.id_offre,
            "articolo_id": o.articolo,
            "articolo_nome": articolo.nome_articolo if articolo else "",
            "prezzo": o.prezzo,
            "provvigione": o.provvigione,
            "tipologia": o.tipologia
        })
    return result


@app.post("/api/offre", status_code=201)
def create_offerta(data: dict, db: Session = Depends(get_db)):
    """Crea offerta venditore"""
    from models import TVenditoreOffre
    nuova = TVenditoreOffre(
        venditore=data["venditore_id"],
        articolo=data["articolo_id"],
        prezzo=data["prezzo"],
        provvigione=data.get("provvigione"),
        tipologia=data.get("tipologia")
    )
    db.add(nuova)
    db.commit()
    db.refresh(nuova)
    return {"id": nuova.id_offre}


@app.delete("/api/offre/{offerta_id}", status_code=204)
def delete_offerta(offerta_id: int, db: Session = Depends(get_db)):
    """Elimina offerta"""
    from models import TVenditoreOffre
    offerta = db.query(TVenditoreOffre).filter(TVenditoreOffre.id_offre == offerta_id).first()
    if offerta:
        db.delete(offerta)
        db.commit()


@app.get("/api/compratori/{compratore_id}/cerca")
def get_compratore_cerca(compratore_id: int, db: Session = Depends(get_db)):
    """Cosa cerca questo compratore"""
    from models import TCompratoreCerca
    ricerche = db.query(TCompratoreCerca).filter(TCompratoreCerca.compratore == compratore_id).all()
    
    result = []
    for r in ricerche:
        articolo = db.query(TArticolo).filter(TArticolo.id_articolo == r.articolo).first()
        result.append({
            "id": r.id_cerca,
            "articolo_id": r.articolo,
            "articolo_nome": articolo.nome_articolo if articolo else "",
            "note": r.note
        })
    return result


@app.post("/api/cerca", status_code=201)
def create_ricerca(data: dict, db: Session = Depends(get_db)):
    """Crea ricerca compratore"""
    from models import TCompratoreCerca
    nuova = TCompratoreCerca(
        compratore=data["compratore_id"],
        articolo=data["articolo_id"],
        note=data.get("note")
    )
    db.add(nuova)
    db.commit()
    db.refresh(nuova)
    return {"id": nuova.id_cerca}


@app.delete("/api/cerca/{ricerca_id}", status_code=204)
def delete_ricerca(ricerca_id: int, db: Session = Depends(get_db)):
    """Elimina ricerca"""
    from models import TCompratoreCerca
    ricerca = db.query(TCompratoreCerca).filter(TCompratoreCerca.id_cerca == ricerca_id).first()
    if ricerca:
        db.delete(ricerca)
        db.commit()


# ==================== IVA, PAGAMENTI, BANCHE ====================
@app.get("/api/iva")
def get_iva_list(db: Session = Depends(get_db)):
    """Lista IVA"""
    from models import TIva
    iva_list = db.query(TIva).all()
    return [{"id_iva": i.id_iva, "descrizione": i.descrizione, "iva": i.iva} for i in iva_list]


@app.get("/api/iva/{iva_id}")
def get_iva(iva_id: int, db: Session = Depends(get_db)):
    """Dettaglio IVA"""
    from models import TIva
    iva = db.query(TIva).filter(TIva.id_iva == iva_id).first()
    if not iva:
        raise HTTPException(status_code=404, detail="IVA non trovata")
    return {"id_iva": iva.id_iva, "descrizione": iva.descrizione, "iva": iva.iva}


@app.post("/api/iva", status_code=201)
def create_iva(data: dict, db: Session = Depends(get_db)):
    """Crea IVA"""
    from models import TIva
    nuova = TIva(descrizione=data.get("descrizione"), iva=data.get("iva"))
    db.add(nuova)
    db.commit()
    db.refresh(nuova)
    return {"id": nuova.id_iva}


@app.delete("/api/iva/{iva_id}", status_code=204)
def delete_iva(iva_id: int, db: Session = Depends(get_db)):
    """Elimina IVA"""
    from models import TIva
    iva = db.query(TIva).filter(TIva.id_iva == iva_id).first()
    if iva:
        db.delete(iva)
        db.commit()


@app.get("/api/pagamenti")
def get_pagamenti(db: Session = Depends(get_db)):
    """Lista pagamenti"""
    from models import TPagamento
    pagamenti = db.query(TPagamento).all()
    return [{"id": p.id_pagamento, "id_pagamento": p.id_pagamento, "tipo": p.tipo_pagamento, "tipo_pagamento": p.tipo_pagamento} for p in pagamenti]


@app.get("/api/pagamenti/{pag_id}")
def get_pagamento(pag_id: int, db: Session = Depends(get_db)):
    """Dettaglio pagamento"""
    from models import TPagamento
    pagamento = db.query(TPagamento).filter(TPagamento.id_pagamento == pag_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    return {"id_pagamento": pagamento.id_pagamento, "tipo_pagamento": pagamento.tipo_pagamento}


@app.post("/api/pagamenti", status_code=201)
def create_pagamento(data: dict, db: Session = Depends(get_db)):
    """Crea pagamento"""
    from models import TPagamento
    nuovo = TPagamento(tipo_pagamento=data.get("tipo_pagamento"))
    db.add(nuovo)
    db.commit()
    db.refresh(nuovo)
    return {"id": nuovo.id_pagamento}


@app.delete("/api/pagamenti/{pag_id}", status_code=204)
def delete_pagamento(pag_id: int, db: Session = Depends(get_db)):
    """Elimina pagamento"""
    from models import TPagamento
    pag = db.query(TPagamento).filter(TPagamento.id_pagamento == pag_id).first()
    if pag:
        db.delete(pag)
        db.commit()


@app.get("/api/banche")
def get_banche(db: Session = Depends(get_db)):
    """Lista banche"""
    from models import TBanca
    banche = db.query(TBanca).all()
    return [
        {
            "id_banca": b.id_banca,
            "nome_banca": b.nome_banca,
            "iban": b.iban,
            "bic": b.bic
        }
        for b in banche
    ]


@app.get("/api/banche/{banca_id}")
def get_banca(banca_id: int, db: Session = Depends(get_db)):
    """Dettaglio banca"""
    from models import TBanca
    banca = db.query(TBanca).filter(TBanca.id_banca == banca_id).first()
    if not banca:
        raise HTTPException(status_code=404, detail="Banca non trovata")
    return {
        "id_banca": banca.id_banca,
        "nome_banca": banca.nome_banca,
        "iban": banca.iban,
        "bic": banca.bic
    }


@app.post("/api/banche", status_code=201)
def create_banca(data: dict, db: Session = Depends(get_db)):
    """Crea banca"""
    from models import TBanca
    nuova = TBanca(
        nome_banca=data.get("nome_banca"),
        iban=data.get("iban"),
        bic=data.get("bic")
    )
    db.add(nuova)
    db.commit()
    db.refresh(nuova)
    return {"id": nuova.id_banca}


@app.delete("/api/banche/{banca_id}", status_code=204)
def delete_banca(banca_id: int, db: Session = Depends(get_db)):
    """Elimina banca"""
    from models import TBanca
    banca = db.query(TBanca).filter(TBanca.id_banca == banca_id).first()
    if banca:
        db.delete(banca)
        db.commit()


@app.get("/debug/articoli-raw")
def debug_articoli_raw(db: Session = Depends(get_db)):
    """DEBUG: Query SQL diretta sul database"""
    import sqlite3
    from database import DATABASE_PATH
    
    # Query diretta con sqlite3 (bypassa SQLAlchemy)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id_articolo, nome_articolo FROM t_articoli ORDER BY id_articolo DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    
    direct_result = [{"id": r[0], "nome": r[1]} for r in rows]
    
    # Query con SQLAlchemy
    articoli = db.query(TArticolo).order_by(TArticolo.id_articolo.desc()).limit(10).all()
    sqlalchemy_result = [{"id": a.id_articolo, "nome": a.nome_articolo} for a in articoli]
    
    return {
        "database_path": str(DATABASE_PATH),
        "direct_sqlite3": direct_result,
        "sqlalchemy": sqlalchemy_result,
        "match": direct_result == sqlalchemy_result
    }


# ==================== FATTURE STUDIO ====================
@app.get("/api/fatture-studio")
def get_fatture_studio(db: Session = Depends(get_db)):
    """Lista fatture studio con nomi delle relazioni"""
    fatture = db.query(TFatturaStudio).order_by(TFatturaStudio.id_fatt_studio.desc()).all()

    result = []
    for f in fatture:
        # Ottieni nome venditore (cliente)
        cliente_nome = ""
        if f.cliente:
            venditore = db.query(TVenditore).filter(TVenditore.id_venditore == f.cliente).first()
            if venditore:
                cliente_nome = venditore.azienda or ""

        # Ottieni descrizione IVA
        iva_desc = ""
        if f.t_iva:
            iva = db.query(TIva).filter(TIva.id_iva == f.t_iva).first()
            if iva:
                iva_desc = iva.descrizione or ""

        # Ottieni tipo pagamento
        pagamento_tipo = ""
        if f.t_pagamento:
            pagamento = db.query(TPagamento).filter(TPagamento.id_pagamento == f.t_pagamento).first()
            if pagamento:
                pagamento_tipo = pagamento.tipo_pagamento or ""

        # Ottieni nome banca
        banca_nome = ""
        if f.id_banca:
            banca = db.query(TBanca).filter(TBanca.id_banca == f.id_banca).first()
            if banca:
                banca_nome = banca.nome_banca or ""

        result.append({
            "id_fatt_studio": f.id_fatt_studio,
            "n_fat": f.n_fat,
            "data_fat": f.data_fat,
            "nota_acr": f.nota_acr,
            "cliente": f.cliente,
            "cliente_nome": cliente_nome,
            "t_iva": f.t_iva,
            "iva_desc": iva_desc,
            "t_pagamento": f.t_pagamento,
            "pagamento_tipo": pagamento_tipo,
            "note": f.note,
            "id_banca": f.id_banca,
            "banca_nome": banca_nome
        })

    return result


@app.get("/api/fatture-studio/{id_fattura}/stampa")
def stampa_fattura_studio(id_fattura: int, db: Session = Depends(get_db)):
    """
    Genera e scarica il PDF della fattura studio

    Restituisce il PDF in italiano se il cliente è italiano, altrimenti in inglese
    """
    # Recupera la fattura
    fattura = db.query(TFatturaStudio).filter(TFatturaStudio.id_fatt_studio == id_fattura).first()
    if not fattura:
        raise HTTPException(status_code=404, detail="Fattura non trovata")

    # Recupera il cliente (venditore)
    cliente = db.query(TVenditore).filter(TVenditore.id_venditore == fattura.cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")

    # Recupera IVA
    iva = db.query(TIva).filter(TIva.id_iva == fattura.t_iva).first()
    if not iva:
        raise HTTPException(status_code=404, detail="IVA non trovata")

    # Recupera tipo pagamento
    pagamento = db.query(TPagamento).filter(TPagamento.id_pagamento == fattura.t_pagamento).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Tipo pagamento non trovato")

    # Recupera banca (opzionale)
    banca = None
    if fattura.id_banca:
        banca = db.query(TBanca).filter(TBanca.id_banca == fattura.id_banca).first()

    # Recupera dettagli fattura
    dettagli = db.query(TFatturaStudioDet).filter(
        TFatturaStudioDet.id_fat_studio == id_fattura
    ).all()

    # Prepara i dati della fattura
    fattura_data = {
        'id_fatt_studio': fattura.id_fatt_studio,
        'n_fat': fattura.n_fat,
        'data_fat': fattura.data_fat,
        'nota_acr': fattura.nota_acr,
        'note': fattura.note
    }

    # Prepara i dati del cliente
    cliente_data = {
        'id': cliente.id_venditore,
        'azienda': cliente.azienda or '',
        'indirizzo': cliente.indirizzo or '',
        'cap': cliente.cap or '',
        'citta': cliente.citta or '',
        'piva': cliente.piva or '',
        'partita_iva': cliente.piva or '',
        'telefono': cliente.telefono or '',
        'italiano': cliente.italiano or 'Si'
    }

    # Prepara i dati IVA
    iva_data = {
        'id_iva': iva.id_iva,
        'descrizione': iva.descrizione or '',
        'iva': iva.iva or '0'
    }

    # Prepara i dati pagamento
    pagamento_data = {
        'id_pagamento': pagamento.id_pagamento,
        'tipo_pagamento': pagamento.tipo_pagamento or ''
    }

    # Prepara i dati banca (se presente)
    banca_data = None
    if banca:
        banca_data = {
            'id_banca': banca.id_banca,
            'nome_banca': banca.nome_banca or '',
            'iban': banca.iban or '',
            'bic': banca.bic or ''
        }

    # Prepara i dettagli con nomi compratori
    dettagli_data = []
    for det in dettagli:
        compratore = db.query(TCompratore).filter(
            TCompratore.id_compratore == det.compratore
        ).first()

        dettagli_data.append({
            'id_fat_studio_det': det.id_fat_studio_det,
            'compratore': det.compratore,
            'compratore_nome': compratore.azienda if compratore else '',
            'qta': det.qta,
            'prezzo': det.prezzo,
            'provvigione': det.provvigione,
            'tipologia': det.tipologia,
            'data_consegna': det.data_consegna
        })

    # Genera il PDF
    pdf_gen = PDFConfermaOrdine()
    pdf_buffer = pdf_gen.genera_fattura_studio(
        fattura_data,
        cliente_data,
        dettagli_data,
        iva_data,
        pagamento_data,
        banca_data
    )

    # Nome file
    is_estero = cliente.italiano != 'Si'
    lang_suffix = '_EN' if is_estero else '_IT'
    filename = f"Fattura_Studio_{fattura.n_fat or id_fattura}{lang_suffix}.pdf"

    # Restituisce il PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@app.get("/api/fatture-studio/{id_fattura}")
def get_fattura_studio(id_fattura: int, db: Session = Depends(get_db)):
    """Dettaglio fattura studio"""
    fattura = db.query(TFatturaStudio).filter(TFatturaStudio.id_fatt_studio == id_fattura).first()
    if not fattura:
        raise HTTPException(status_code=404, detail="Fattura non trovata")

    return {
        "id_fatt_studio": fattura.id_fatt_studio,
        "n_fat": fattura.n_fat,
        "data_fat": fattura.data_fat,
        "nota_acr": fattura.nota_acr,
        "cliente": fattura.cliente,
        "t_iva": fattura.t_iva,
        "t_pagamento": fattura.t_pagamento,
        "note": fattura.note,
        "id_banca": fattura.id_banca
    }


@app.post("/api/fatture-studio")
def create_fattura_studio(data: dict, db: Session = Depends(get_db)):
    """Crea nuova fattura studio"""
    fattura = TFatturaStudio(
        n_fat=data.get("n_fat"),
        data_fat=data.get("data_fat"),
        nota_acr=data.get("nota_acr"),
        cliente=data.get("cliente"),
        t_iva=data.get("t_iva"),
        t_pagamento=data.get("t_pagamento"),
        note=data.get("note"),
        id_banca=data.get("id_banca")
    )
    db.add(fattura)
    db.commit()
    db.refresh(fattura)
    return {"id": fattura.id_fatt_studio, "message": "Fattura studio creata"}


@app.put("/api/fatture-studio/{id_fattura}")
def update_fattura_studio(id_fattura: int, data: dict, db: Session = Depends(get_db)):
    """Aggiorna fattura studio"""
    fattura = db.query(TFatturaStudio).filter(TFatturaStudio.id_fatt_studio == id_fattura).first()
    if not fattura:
        raise HTTPException(status_code=404, detail="Fattura non trovata")

    fattura.n_fat = data.get("n_fat", fattura.n_fat)
    fattura.data_fat = data.get("data_fat", fattura.data_fat)
    fattura.nota_acr = data.get("nota_acr", fattura.nota_acr)
    fattura.cliente = data.get("cliente", fattura.cliente)
    fattura.t_iva = data.get("t_iva", fattura.t_iva)
    fattura.t_pagamento = data.get("t_pagamento", fattura.t_pagamento)
    fattura.note = data.get("note", fattura.note)
    fattura.id_banca = data.get("id_banca", fattura.id_banca)

    db.commit()
    return {"message": "Fattura studio aggiornata"}


@app.delete("/api/fatture-studio/{id_fattura}")
def delete_fattura_studio(id_fattura: int, db: Session = Depends(get_db)):
    """Elimina fattura studio"""
    fattura = db.query(TFatturaStudio).filter(TFatturaStudio.id_fatt_studio == id_fattura).first()
    if not fattura:
        raise HTTPException(status_code=404, detail="Fattura non trovata")

    db.delete(fattura)
    db.commit()
    return {"message": "Fattura studio eliminata"}


@app.get("/api/fatture-studio/{id_fattura}/dettagli")
def get_dettagli_fattura_studio(id_fattura: int, db: Session = Depends(get_db)):
    """Lista dettagli di una fattura studio con nomi delle relazioni"""
    print(f"DEBUG: Richiesta dettagli per fattura {id_fattura}")

    dettagli = db.query(TFatturaStudioDet).filter(
        TFatturaStudioDet.id_fat_studio == id_fattura
    ).all()

    print(f"DEBUG: Trovati {len(dettagli)} dettagli")

    result = []
    for d in dettagli:
        # Ottieni nome compratore
        compratore_nome = ""
        if d.compratore:
            compratore = db.query(TCompratore).filter(TCompratore.id_compratore == d.compratore).first()
            if compratore:
                compratore_nome = compratore.azienda or ""

        result.append({
            "id_fat_studio_det": d.id_fat_studio_det,
            "id_fat_studio": d.id_fat_studio,
            "compratore": d.compratore,
            "compratore_nome": compratore_nome,
            "qta": d.qta,
            "prezzo": d.prezzo,
            "provvigione": d.provvigione,
            "tipologia": d.tipologia,
            "data_consegna": d.data_consegna
        })

    print(f"DEBUG: Restituisco {len(result)} dettagli")
    return result


@app.post("/api/fatture-studio/dettagli")
def create_dettaglio_fattura_studio(data: dict, db: Session = Depends(get_db)):
    """Crea nuovo dettaglio fattura studio"""
    dettaglio = TFatturaStudioDet(
        id_fat_studio=data.get("id_fat_studio"),
        compratore=data.get("compratore"),
        qta=data.get("qta"),
        prezzo=data.get("prezzo"),
        provvigione=data.get("provvigione"),
        tipologia=data.get("tipologia"),
        data_consegna=data.get("data_consegna")
    )
    db.add(dettaglio)
    db.commit()
    db.refresh(dettaglio)
    return {"id": dettaglio.id_fat_studio_det, "message": "Dettaglio creato"}


@app.put("/api/fatture-studio/dettagli/{id_dettaglio}")
def update_dettaglio_fattura_studio(id_dettaglio: int, data: dict, db: Session = Depends(get_db)):
    """Aggiorna dettaglio fattura studio"""
    dettaglio = db.query(TFatturaStudioDet).filter(
        TFatturaStudioDet.id_fat_studio_det == id_dettaglio
    ).first()

    if not dettaglio:
        raise HTTPException(status_code=404, detail="Dettaglio non trovato")

    dettaglio.compratore = data.get("compratore", dettaglio.compratore)
    dettaglio.qta = data.get("qta", dettaglio.qta)
    dettaglio.prezzo = data.get("prezzo", dettaglio.prezzo)
    dettaglio.provvigione = data.get("provvigione", dettaglio.provvigione)
    dettaglio.tipologia = data.get("tipologia", dettaglio.tipologia)
    dettaglio.data_consegna = data.get("data_consegna", dettaglio.data_consegna)

    db.commit()
    return {"message": "Dettaglio aggiornato"}


@app.delete("/api/fatture-studio/dettagli/{id_dettaglio}")
def delete_dettaglio_fattura_studio(id_dettaglio: int, db: Session = Depends(get_db)):
    """Elimina dettaglio fattura studio"""
    dettaglio = db.query(TFatturaStudioDet).filter(
        TFatturaStudioDet.id_fat_studio_det == id_dettaglio
    ).first()

    if not dettaglio:
        raise HTTPException(status_code=404, detail="Dettaglio non trovato")

    db.delete(dettaglio)
    db.commit()
    return {"message": "Dettaglio eliminato"}


# ==================== REPORT ====================
@app.get("/api/report/potenziale")
def get_report_potenziale(
    data_dal: str = Query(..., description="Data inizio (YYYY-MM-DD)"),
    data_al: str = Query(..., description="Data fine (YYYY-MM-DD)"),
    id_venditore: Optional[int] = Query(None, description="Filtro opzionale per venditore"),
    db: Session = Depends(get_db)
):
    """
    Report POTENZIALE: consegne previste da t_date_consegna
    """
    from datetime import datetime as dt

    # Valida date
    try:
        data_dal_obj = dt.strptime(data_dal, "%Y-%m-%d")
        data_al_obj = dt.strptime(data_al, "%Y-%m-%d")
    except:
        raise HTTPException(status_code=400, detail="Formato data non valido. Usare YYYY-MM-DD")

    # Query SEMPLICE: leggi date consegna previste
    query = db.query(
        TDataConsegna.data_consegna,
        TDataConsegna.qta_consegna,
        TConferma.prezzo,
        TConferma.provvigione,
        TConferma.tipologia,
        TConferma.arrivo,
        TConferma.carico,
        TVenditore.azienda.label('venditore_nome'),
        TCompratore.azienda.label('compratore_nome'),
        TArticolo.nome_articolo,
        TArticolo.tipologia.label('articolo_tipologia')
    ).join(
        TConferma, TDataConsegna.id_conferma == TConferma.id_conferma
    ).join(
        TVenditore, TConferma.venditore == TVenditore.id_venditore
    ).join(
        TCompratore, TConferma.compratore == TCompratore.id_compratore
    ).join(
        TArticolo, TConferma.articolo == TArticolo.id_articolo
    )

    # Filtro venditore opzionale
    if id_venditore:
        query = query.filter(TVenditore.id_venditore == id_venditore)

    results = query.all()

    # Filtra per date e calcola totali
    records = []
    for r in results:
        # Filtra per data (formato DD/MM/YYYY)
        if r.data_consegna:
            try:
                if '/' in str(r.data_consegna):
                    data_obj = dt.strptime(str(r.data_consegna), "%d/%m/%Y")
                    if not (data_dal_obj <= data_obj <= data_al_obj):
                        continue
            except:
                continue

        # Calcola importo (gestisci stringhe vuote e None)
        try:
            qta = float(r.qta_consegna) if r.qta_consegna and str(r.qta_consegna).strip() else 0.0
        except:
            qta = 0.0

        try:
            prezzo = float(r.prezzo) if r.prezzo and str(r.prezzo).strip() else 0.0
        except:
            prezzo = 0.0

        try:
            provvigione = float(r.provvigione) if r.provvigione and str(r.provvigione).strip() else 0.0
        except:
            provvigione = 0.0

        if r.tipologia == "Q.TA":
            euro = qta * provvigione
        else:
            euro = qta * provvigione * prezzo

        records.append({
            'compratore_azienda': r.compratore_nome or '',
            'venditore_azienda': r.venditore_nome or '',
            'articolo_nome': r.nome_articolo or '',
            'articolo_tipologia': r.articolo_tipologia or '',
            'arrivo': r.arrivo or '',
            'carico': r.carico or '',
            'qta_cons': qta,
            'prezzo': prezzo,
            'delta': provvigione,
            'euro': euro,
            'data_consegna': r.data_consegna or '',
            'tipologia': r.tipologia or ''
        })

    return {
        "data_dal": data_dal,
        "data_al": data_al,
        "id_venditore": id_venditore,
        "records": records,
        "totale_righe": len(records)
    }


@app.get("/api/report/potenziale/pdf")
def download_report_potenziale_pdf(
    data_dal: str = Query(..., description="Data inizio (YYYY-MM-DD)"),
    data_al: str = Query(..., description="Data fine (YYYY-MM-DD)"),
    id_venditore: Optional[int] = Query(None, description="Filtro opzionale per venditore"),
    db: Session = Depends(get_db)
):
    """Genera e scarica PDF report potenziale"""
    # Ottieni dati
    report_data = get_report_potenziale(data_dal, data_al, id_venditore, db)

    # Nome venditore per titolo
    venditore_nome = None
    if id_venditore:
        venditore = db.query(TVenditore).filter(TVenditore.id_venditore == id_venditore).first()
        if venditore:
            venditore_nome = venditore.azienda

    # Genera PDF
    pdf_gen = PDFReportGenerator()
    pdf_buffer = pdf_gen.genera_report_potenziale(
        data_dal,
        data_al,
        report_data['records'],
        venditore_nome
    )

    # Nome file
    filename = f"report_potenziale_{data_dal}_{data_al}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@app.get("/api/report/effettivo")
def get_report_effettivo(
    data_dal: str = Query(..., description="Data inizio (YYYY-MM-DD)"),
    data_al: str = Query(..., description="Data fine (YYYY-MM-DD)"),
    id_venditore: Optional[int] = Query(None, description="Filtro opzionale per venditore"),
    db: Session = Depends(get_db)
):
    """
    Report EFFETTIVO: vendite fatturate da t_fatture
    """
    from datetime import datetime as dt

    # Valida date
    try:
        data_dal_obj = dt.strptime(data_dal, "%Y-%m-%d")
        data_al_obj = dt.strptime(data_al, "%Y-%m-%d")
    except:
        raise HTTPException(status_code=400, detail="Formato data non valido. Usare YYYY-MM-DD")

    # Query SEMPLICE: leggi fatture effettive
    query = db.query(
        TFattura.data_consegna,
        TFattura.qta,
        TFattura.prezzo,
        TConferma.provvigione,
        TConferma.tipologia,
        TConferma.arrivo,
        TConferma.carico,
        TVenditore.azienda.label('venditore_nome'),
        TCompratore.azienda.label('compratore_nome'),
        TArticolo.nome_articolo,
        TArticolo.tipologia.label('articolo_tipologia')
    ).join(
        TConferma, TFattura.confermaordine == TConferma.id_conferma
    ).join(
        TVenditore, TConferma.venditore == TVenditore.id_venditore
    ).join(
        TCompratore, TConferma.compratore == TCompratore.id_compratore
    ).join(
        TArticolo, TConferma.articolo == TArticolo.id_articolo
    )

    # Filtro venditore opzionale
    if id_venditore:
        query = query.filter(TVenditore.id_venditore == id_venditore)

    results = query.all()

    # Filtra per date e calcola totali
    records = []
    for r in results:
        # Filtra per data (può essere formato DD/MM/YYYY o numero)
        if r.data_consegna:
            try:
                if isinstance(r.data_consegna, str) and '/' in r.data_consegna:
                    data_obj = dt.strptime(r.data_consegna, "%d/%m/%Y")
                    if not (data_dal_obj <= data_obj <= data_al_obj):
                        continue
            except:
                continue

        # Calcola importo (gestisci stringhe vuote e None)
        try:
            qta = float(r.qta) if r.qta and str(r.qta).strip() else 0.0
        except:
            qta = 0.0

        try:
            prezzo = float(r.prezzo) if r.prezzo and str(r.prezzo).strip() else 0.0
        except:
            prezzo = 0.0

        try:
            provvigione = float(r.provvigione) if r.provvigione and str(r.provvigione).strip() else 0.0
        except:
            provvigione = 0.0

        if r.tipologia == "Q.TA":
            euro = qta * provvigione
        else:
            euro = qta * provvigione * prezzo

        records.append({
            'compratore_azienda': r.compratore_nome or '',
            'venditore_azienda': r.venditore_nome or '',
            'articolo_nome': r.nome_articolo or '',
            'articolo_tipologia': r.articolo_tipologia or '',
            'arrivo': r.arrivo or '',
            'carico': r.carico or '',
            'qta': qta,
            'prezzo': prezzo,
            'delta': provvigione,
            'euro': euro,
            'data_consegna': str(r.data_consegna) if r.data_consegna else '',
            'tipologia': r.tipologia or ''
        })

    return {
        "data_dal": data_dal,
        "data_al": data_al,
        "id_venditore": id_venditore,
        "records": records,
        "totale_righe": len(records)
    }


@app.get("/api/report/effettivo/pdf")
def download_report_effettivo_pdf(
    data_dal: str = Query(..., description="Data inizio (YYYY-MM-DD)"),
    data_al: str = Query(..., description="Data fine (YYYY-MM-DD)"),
    id_venditore: Optional[int] = Query(None, description="Filtro opzionale per venditore"),
    db: Session = Depends(get_db)
):
    """Genera e scarica PDF report effettivo"""
    # Ottieni dati
    report_data = get_report_effettivo(data_dal, data_al, id_venditore, db)

    # Nome venditore per titolo
    venditore_nome = None
    if id_venditore:
        venditore = db.query(TVenditore).filter(TVenditore.id_venditore == id_venditore).first()
        if venditore:
            venditore_nome = venditore.azienda

    # Genera PDF
    pdf_gen = PDFReportGenerator()
    pdf_buffer = pdf_gen.genera_report_effettivo(
        data_dal,
        data_al,
        report_data['records'],
        venditore_nome
    )

    # Nome file
    filename = f"report_effettivo_{data_dal}_{data_al}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)