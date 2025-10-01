import os
import sqlite3
import subprocess
import re
from dateutil import parser as dateparser

MDB_FILE = "db_gesty.mdb"
OUTPUT_DIR = "output"
SQLITE_FILE = os.path.join(OUTPUT_DIR, "db_gesty.db")

# --- FUNZIONI DI NORMALIZZAZIONE ---
NUM_COMMA_RE = re.compile(r'^[\-\+]?\d{1,3}(\.\d{3})*(,\d+)?$')
NUM_DOT_RE = re.compile(r'^[\-\+]?\d+(\.\d+)?$')

def normalize_numeric(val):
    if val is None: return None
    s = str(val).strip()
    if NUM_COMMA_RE.match(s):
        return float(s.replace('.', '').replace(',', '.'))
    if NUM_DOT_RE.match(s):
        return float(s)
    return val

def normalize_date(val):
    try:
        return dateparser.parse(str(val), dayfirst=True).date().isoformat()
    except Exception:
        return val

def clean_table(conn, table):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cur.fetchall()]
    cur.execute(f"SELECT rowid, * FROM {table}")
    rows = cur.fetchall()

    for row in rows:
        rowid = row[0]
        values = list(row[1:])
        new_values = []
        changed = False
        for v in values:
            newv = v
            if isinstance(v, str):
                tmp = normalize_numeric(v)
                if tmp == v:  # se non è numero, prova come data
                    tmp = normalize_date(v)
                newv = tmp
            if newv != v:
                changed = True
            new_values.append(newv)
        if changed:
            placeholders = ', '.join([f"{col}=?" for col in cols])
            conn.execute(f"UPDATE {table} SET {placeholders} WHERE rowid=?",
                         (*new_values, rowid))
    conn.commit()


def main():
    if not os.path.exists(MDB_FILE):
        print(f"❌ File {MDB_FILE} non trovato!")
        return

    # crea la sottocartella se non esiste
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Esporta schema da MDB
    print("📤 Esporto schema da MDB...")
    schema_sql = os.path.join(OUTPUT_DIR, "schema.sql")
    with open(schema_sql, "w") as f:
        subprocess.run(["mdb-schema", MDB_FILE, "sqlite"], stdout=f)

    # 2. Crea SQLite DB con lo schema
    print("📥 Creo database SQLite...")
    if os.path.exists(SQLITE_FILE):
        os.remove(SQLITE_FILE)
    subprocess.run(["sqlite3", SQLITE_FILE], stdin=open(schema_sql, "r"))

    # 3. Elenco tabelle
    print("📋 Estraggo lista tabelle...")
    tables_out = subprocess.check_output(["mdb-tables", "-1", MDB_FILE]).decode().splitlines()
    tables = [t.strip() for t in tables_out if t.strip()]

    # 4. Esporta dati e importa in SQLite
    for t in tables:
        print(f"➡️  Esporto tabella {t}...")
        csv_file = os.path.join(OUTPUT_DIR, f"{t}.csv")
        with open(csv_file, "w") as f:
            subprocess.run(["mdb-export", "-D", "%Y-%m-%d", "-R", "\n", "-d", ",", MDB_FILE, t], stdout=f)

        print(f"➡️  Importo tabella {t} in SQLite...")
        subprocess.run([
            "sqlite3", SQLITE_FILE,
            f".mode csv", f".import {csv_file} {t}"
        ])

    # 5. Pulizia dati
    print("🧹 Pulizia dati...")
    conn = sqlite3.connect(SQLITE_FILE)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [r[0] for r in cur.fetchall()]
    for t in all_tables:
        print(f"   Pulisco {t}...")
        try:
            clean_table(conn, t)
        except Exception as e:
            print(f"   ⚠️ Errore in tabella {t}: {e}")
    conn.close()

    print(f"✅ Conversione completata: {SQLITE_FILE}")

if __name__ == "__main__":
    main()
