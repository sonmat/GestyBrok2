#!/bin/bash
# start.sh - Script per avvio Linux/Mac

echo "=== GestyBrok 2.0 - Avvio Applicazione ==="
echo ""

# Funzione per cleanup
cleanup() {
    echo ""
    echo "Chiusura applicazione..."
    kill $BACKEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Controlla se venv esiste
if [ ! -d "venv" ]; then
    echo "Ambiente virtuale non trovato. Creazione in corso..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Avvia backend in background
echo "Avvio Backend..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Attendi che il backend sia pronto
echo "Attendo avvio backend..."
sleep 3

# Controlla se backend è attivo
if ! curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "ERRORE: Backend non risponde"
    kill $BACKEND_PID
    exit 1
fi

echo "✓ Backend attivo su http://127.0.0.1:8000"
echo ""

# Avvia frontend
echo "Avvio Frontend..."
cd frontend
python gui_main.py

# Cleanup quando frontend chiude
cleanup

# ============================================
# start.bat - Script per avvio Windows
# Salvare questo contenuto in start.bat
# ============================================
#
# @echo off
# echo === GestyBrok 2.0 - Avvio Applicazione ===
# echo.
#
# REM Controlla se venv esiste
# if not exist "venv" (
#     echo Ambiente virtuale non trovato. Creazione in corso...
#     python -m venv venv
#     call venv\Scripts\activate
#     pip install -r requirements.txt
# ) else (
#     call venv\Scripts\activate
# )
#
# REM Avvia backend in nuova finestra
# echo Avvio Backend...
# start "GestyBrok Backend" cmd /c "cd backend && python main.py"
#
# REM Attendi backend
# echo Attendo avvio backend...
# timeout /t 3 /nobreak > nul
#
# REM Avvia frontend
# echo Avvio Frontend...
# cd frontend
# python gui_main.py
#
# REM Chiudi backend quando frontend chiude
# taskkill /FI "WINDOWTITLE eq GestyBrok Backend*" /T /F 2>nul
# echo.
# echo Applicazione chiusa.
# pause
