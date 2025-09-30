# 🚀 GestyBrok 2.0 - Guida Rapida

## Setup Iniziale (5 minuti)

### 1. Requisiti
- Python 3.8 o superiore
- pip (gestore pacchetti Python)

### 2. Installazione

```bash
# Clona/scarica il progetto
cd gestybrok2

# Crea ambiente virtuale
python -m venv venv

# Attiva ambiente (scegli in base al tuo OS)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt
```

### 3. Avvio Rapido

**Opzione A - Script automatico (raccomandato)**

```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows
start.bat
```

**Opzione B - Manuale (2 terminali)**

Terminale 1 - Backend:
```bash
cd backend
python main.py
```

Terminale 2 - Frontend:
```bash
cd frontend
python gui_main.py
```

## 📋 Primi Passi nell'App

### 1. Crea Articoli
- Vai su tab "Anagrafiche" → "Articoli"
- Clicca "Nuovo"
- Compila: Nome, Codice, Unità di Misura
- Clicca "Salva"

### 2. Aggiungi Venditori
- Tab "Anagrafiche" → "Venditori"
- Clicca "Nuovo"
- Compila: Azienda (obbligatorio), dati contatto
- Clicca "Salva"

### 3. Aggiungi Compratori
- Tab "Anagrafiche" → "Compratori"
- Stessa procedura dei venditori

### 4. Crea Conferme Ordine
- Tab "Conferme Ordine"
- Clicca "Nuova Conferma"
- Seleziona: Venditore, Compratore, Articolo
- Inserisci: Quantità, Prezzo, Provvigione
- Clicca "Salva"

### 5. Genera Fatture
- Tab "Fatture"
- Clicca "Genera Fatture"
- Seleziona i mesi
- Conferma generazione

### 6. Visualizza Report
- Tab "Report"
- Scegli tipo report
- Inserisci date (se richiesto)
- Clicca "Genera Report"

## 🔧 Risoluzione Problemi Comuni

### Backend non si avvia
```bash
# Verifica che la porta 8000 sia libera
# Windows:
netstat -ano | findstr :8000
# Linux/Mac:
lsof -i :8000

# Se occupata, termina il processo o cambia porta
```

### Frontend non si connette
```bash
# Verifica che backend sia attivo
curl http://127.0.0.1:8000/health

# Dovrebbe rispondere: {"status":"healthy"}
```

### Errori dipendenze
```bash
# Reinstalla tutto
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Database corrotto
```bash
# Elimina e ricrea
cd backend
rm gestybrok.db
python main.py  # Ricrea automaticamente
```

## 📚 Documentazione Completa

- **README.md** - Documentazione dettagliata architettura
- **API Docs** - http://127.0.0.1:8000/docs (quando backend attivo)
- **Codice sorgente** - Commenti e docstring in ogni file

## 🎯 Workflow Tipico

1. **Setup anagrafiche** (una tantum)
   - Articoli che tratti
   - Venditori con cui lavori
   - Compratori tuoi clienti

2. **Operatività quotidiana**
   - Registra conferme ordine
   - Traccia date consegna
   - Genera fatture mensilmente

3. **Reportistica**
   - Report fatture periodici
   - Analisi potenziale vendite
   - Esportazione dati contabili

## ⌨️ Scorciatoie e Tips

- **Doppio click** su riga tabella = Modifica rapida
- **Ricerca** in tempo reale nelle tabelle
- **Filtri data** per report = formato gg/mm/aaaa
- **F5** o "Aggiorna" per refresh dati

## 🔐 Backup Dati

Il database è in `backend/gestybrok.db`

```bash
# Backup manuale
cp backend/gestybrok.db backup_$(date +%Y%m%d).db

# Restore
cp backup_YYYYMMDD.db backend/gestybrok.db
```

## 📞 Supporto

Per problemi o domande:
1. Controlla questa guida
2. Verifica logs backend (terminale 1)
3. Leggi README.md per dettagli tecnici
4. Controlla file di test per esempi uso API

## 🎓 Prossimi Step

Una volta familiarizzato:
- Esplora API docs per integrazioni
- Personalizza viste in `frontend/views/`
- Aggiungi validazioni custom
- Implementa report personalizzati

---

**Versione**: 2.0.0  
**Ultimo aggiornamento**: 2024
