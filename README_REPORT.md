# Sistema di Generazione Report - Conferme d'Ordine

## Panoramica

Il sistema genera automaticamente le conferme d'ordine in formato PDF sia per il venditore che per il compratore.
I PDF vengono generati in **italiano** o **inglese** in base alla nazionalità del destinatario (campo `italiano` nelle tabelle venditori/compratori).

## Funzionalità Implementate

### 4 Versioni di Report
1. **Conferma Venditore - Italiano**: per venditori italiani
2. **Conferma Venditore - Inglese**: per venditori esteri
3. **Conferma Compratore - Italiano**: per compratori italiani
4. **Conferma Compratore - Inglese**: per compratori esteri

### Contenuto dei Report
- Header con logo aziendale (da `frontend/Logo.png`)
- Dati aziendali (da `config/company_data.json`)
- Informazioni conferma (numero, data)
- Dati venditore e compratore con indirizzi completi
- Dettagli articolo con quantità, prezzo unitario e totale
- Provvigione (se presente)
- Date di consegna (se presenti)
- Note (se presenti)
- Footer con note legali e informazioni

## API Endpoints

### Stampa Conferma Venditore
```
GET /api/conferme-ordine/{conferma_id}/stampa-venditore
```
Genera il PDF della conferma per il venditore. La lingua viene determinata automaticamente dal campo `italiano` del venditore.

**Risposta**: File PDF con nome `Conferma_Venditore_{numero}_IT.pdf` o `Conferma_Venditore_{numero}_EN.pdf`

### Stampa Conferma Compratore
```
GET /api/conferme-ordine/{conferma_id}/stampa-compratore
```
Genera il PDF della conferma per il compratore. La lingua viene determinata automaticamente dal campo `italiano` del compratore.

**Risposta**: File PDF con nome `Conferma_Compratore_{numero}_IT.pdf` o `Conferma_Compratore_{numero}_EN.pdf`

## File Creati

### Backend
- `backend/pdf_generator.py`: Classe `PDFConfermaOrdine` per la generazione dei PDF
- `backend/test_pdf.py`: Script di test per verificare la generazione

### Configurazione
- `config/company_data.json`: Dati aziendali utilizzati nell'intestazione

### Report di Test
Nella cartella `report/` trovi 4 PDF di esempio:
- `test_venditore_italiano.pdf`
- `test_venditore_estero_en.pdf`
- `test_compratore_italiano.pdf`
- `test_compratore_estero_en.pdf`

## Come Testare

### Test Locale con Script
```bash
cd backend
source ../venv/bin/activate
python test_pdf.py
```

### Test con Server Backend
1. Avvia il backend:
   ```bash
   cd backend
   source ../venv/bin/activate
   python main.py
   ```

2. Accedi agli endpoint:
   - Venditore: `http://localhost:8000/api/conferme-ordine/1/stampa-venditore`
   - Compratore: `http://localhost:8000/api/conferme-ordine/1/stampa-compratore`

## Integrazione Frontend

Nel frontend, quando l'utente clicca sul pulsante "Stampa Conferme", dovrai:

```javascript
// Esempio di chiamata API
const confermaId = 123; // ID della conferma selezionata

// Scarica conferma venditore
const urlVenditore = `http://localhost:8000/api/conferme-ordine/${confermaId}/stampa-venditore`;
window.open(urlVenditore, '_blank');

// Scarica conferma compratore
const urlCompratore = `http://localhost:8000/api/conferme-ordine/${confermaId}/stampa-compratore`;
window.open(urlCompratore, '_blank');
```

Oppure per scaricare entrambi automaticamente:

```javascript
async function stampaBoth(confermaId) {
    // Scarica venditore
    const responseV = await fetch(`http://localhost:8000/api/conferme-ordine/${confermaId}/stampa-venditore`);
    const blobV = await responseV.blob();
    const urlV = window.URL.createObjectURL(blobV);
    const aV = document.createElement('a');
    aV.href = urlV;
    aV.download = `Conferma_Venditore_${confermaId}.pdf`;
    aV.click();

    // Scarica compratore
    const responseC = await fetch(`http://localhost:8000/api/conferme-ordine/${confermaId}/stampa-compratore`);
    const blobC = await responseC.blob();
    const urlC = window.URL.createObjectURL(blobC);
    const aC = document.createElement('a');
    aC.href = urlC;
    aC.download = `Conferma_Compratore_${confermaId}.pdf`;
    aC.click();
}
```

## Personalizzazione

### Modificare i Dati Aziendali
Modifica il file `config/company_data.json` per aggiornare:
- Ragione sociale
- Indirizzo
- Contatti
- Note legali (italiano e inglese)
- Condizioni generali

### Modificare il Logo
Sostituisci il file `frontend/Logo.png` con il tuo logo aziendale.

### Modificare lo Stile dei PDF
Modifica il file `backend/pdf_generator.py`:
- **Colori**: Cerca `colors.HexColor` per modificare i colori
- **Font**: Modifica i valori `fontSize` e `fontName`
- **Layout**: Modifica i valori `colWidths` nelle tabelle

## Dipendenze

Il sistema utilizza:
- `reportlab==4.0.9`: per la generazione dei PDF
- `fastapi`: per gli endpoint API
- `sqlalchemy`: per l'accesso al database

## Note Importanti

1. **Rilevamento Lingua**: Il sistema determina automaticamente la lingua dal campo `italiano` ('Si' o 'No') nelle tabelle `t_venditori` e `t_compratori`

2. **Date di Consegna**: Se presenti nella tabella `t_date_consegna`, vengono incluse nel PDF

3. **Provvigione**: Se presente nella conferma, viene mostrata nella tabella dettagli

4. **Note**: Se presenti, vengono mostrate in una sezione dedicata

5. **Logo**: Se il file logo non esiste, viene mostrato solo il testo dell'header

## Risoluzione Problemi

### Il PDF non viene generato
- Verifica che il backend sia avviato
- Controlla i log del backend per errori
- Verifica che l'ID conferma esista nel database

### Logo non visualizzato
- Verifica che il file `frontend/Logo.png` esista
- Verifica i permessi di lettura del file

### Testi in lingua sbagliata
- Verifica il campo `italiano` nella tabella venditori/compratori
- Deve essere 'Si' per italiano, qualsiasi altro valore per inglese

## Supporto

Per problemi o domande, controlla:
1. I log del backend (`backend/main.py`)
2. I PDF di test nella cartella `report/`
3. Lo script di test `backend/test_pdf.py`
