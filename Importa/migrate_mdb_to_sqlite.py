#!/usr/bin/env python3
"""
Script per sincronizzare database Access MDB con database SQLite.
Cancella e ricarica tutte le tabelle con prefisso t_ mantenendo la stessa struttura.
Gestisce anche le tabelle con nomi diversi tra MDB e SQLite.
"""

import os
import sys
import sqlite3
import subprocess
import tempfile
import csv
from pathlib import Path

# Configurazione
SQLITE_DB = "../backend/db_gesty.db"  # Path relativo da Importa/

# Mapping per tabelle con nomi diversi: SQLite -> MDB
TABLE_NAME_MAPPING = {
    "t_fat_studio_det": "t_fat_studio_dett",
    "t_fat_studio_det_trading": "t_fat_studio_dett_trading",
    "t_venditore_offre": "t_venditori_offre",
    "t_famiglie_articoli": "t_famiglia_articoli"
}


def print_step(msg):
    """Stampa un messaggio di progresso"""
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print('='*60)


def get_mdb_tables(mdb_file):
    """Ottiene lista delle tabelle dal file MDB"""
    try:
        result = subprocess.run(
            ["mdb-tables", "-1", mdb_file],
            capture_output=True,
            text=True,
            check=True
        )
        tables = [t.strip() for t in result.stdout.splitlines() if t.strip()]
        return tables
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore nell'ottenere le tabelle: {e}")
        return []


def clear_table(conn, table_name):
    """Cancella tutti i record da una tabella"""
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table_name}")
        count = cur.rowcount
        conn.commit()
        print(f"  🗑️  {table_name}: {count} record cancellati")
        return True
    except sqlite3.Error as e:
        print(f"  ⚠️  {table_name}: Errore nella cancellazione - {e}")
        return False


def export_mdb_to_csv(mdb_file, table_name, csv_file):
    """Esporta una tabella MDB in CSV"""
    try:
        with open(csv_file, "w") as f:
            subprocess.run(
                ["mdb-export", "-D", "%Y-%m-%d", "-R", "\n", "-d", ",", "-q", '"', mdb_file, table_name],
                stdout=f,
                check=True
            )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Errore nell'esportazione: {e}")
        return False


def import_csv_to_sqlite(sqlite_file, table_name, csv_file):
    """Importa un CSV in una tabella SQLite usando Python per maggiore controllo"""
    try:
        # Verifica che il CSV non sia vuoto
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) <= 1:
                print(f"    ⚠️  CSV vuoto o solo header")
                return True

        # Importa usando Python
        conn = sqlite3.connect(sqlite_file)
        cur = conn.cursor()

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header

            # Prepara query di insert
            placeholders = ','.join(['?' for _ in header])
            insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"

            rows_imported = 0
            rows_failed = 0
            for row in reader:
                # Converti stringhe vuote in NULL
                row = [None if val == '' else val for val in row]
                try:
                    cur.execute(insert_query, row)
                    rows_imported += 1
                except sqlite3.Error as e:
                    rows_failed += 1
                    if rows_failed <= 3:  # Mostra solo i primi 3 errori
                        print(f"      ⚠️  Errore importando riga: {e}")

            conn.commit()
            if rows_failed > 0:
                print(f"    ⚠️  {rows_failed} righe non importate")
            print(f"    ✅ {rows_imported} record importati")

        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ Errore nell'importazione: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_table_count(conn, table_name):
    """Ottiene il numero di record in una tabella"""
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        return count
    except sqlite3.Error:
        return -1


def migrate_table(mdb_file, sqlite_file, sqlite_table_name, mdb_table_name, temp_dir):
    """Migra una singola tabella dal MDB al SQLite (con supporto per nomi diversi)"""
    if sqlite_table_name == mdb_table_name:
        print(f"\n  📋 Tabella: {sqlite_table_name}")
    else:
        print(f"\n  📋 Tabella: {sqlite_table_name} <- {mdb_table_name}")

    # File CSV temporaneo
    csv_file = os.path.join(temp_dir, f"{mdb_table_name}.csv")

    # 1. Esporta da MDB a CSV
    print(f"    📤 Esportazione da MDB...")
    if not export_mdb_to_csv(mdb_file, mdb_table_name, csv_file):
        return False

    # Verifica che il CSV non sia vuoto
    if os.path.getsize(csv_file) == 0:
        print(f"    ⚠️  Tabella vuota, skip")
        return True

    # 2. Importa CSV in SQLite
    print(f"    📥 Importazione in SQLite...")
    if not import_csv_to_sqlite(sqlite_file, sqlite_table_name, csv_file):
        return False

    return True


def clear_all_tables(conn, tables):
    """Cancella tutte le tabelle nell'ordine inverso per rispettare FK"""
    print_step("CANCELLAZIONE DATI ESISTENTI")

    # Disabilita temporaneamente i foreign key constraints
    conn.execute("PRAGMA foreign_keys = OFF")

    # Cancella in ordine inverso (per sicurezza con le FK)
    for table in reversed(tables):
        clear_table(conn, table)

    # Riabilita i foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()


def get_sqlite_tables_with_prefix(sqlite_file, prefix="t_"):
    """Ottiene lista tabelle SQLite che iniziano con un prefisso"""
    try:
        conn = sqlite3.connect(sqlite_file)
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ? ORDER BY name",
            (f"{prefix}%",)
        )
        tables = [row[0] for row in cur.fetchall()]
        conn.close()
        return tables
    except sqlite3.Error as e:
        print(f"❌ Errore nel leggere le tabelle SQLite: {e}")
        return []


def main():
    if len(sys.argv) < 2:
        print("Uso: python migrate_mdb_to_sqlite.py <file.mdb> [db_sqlite.db]")
        print("\nEsempio:")
        print("  python migrate_mdb_to_sqlite.py TestGesty/db_gesty.mdb")
        print("\nLo script:")
        print("  1. Trova tutte le tabelle t_* presenti sia in MDB che in SQLite")
        print("  2. Cancella tutti i record dalle tabelle SQLite")
        print("  3. Importa i dati dal file MDB")
        sys.exit(1)

    mdb_file = sys.argv[1]
    sqlite_file = sys.argv[2] if len(sys.argv) > 2 else SQLITE_DB

    # Converti in path assoluto
    mdb_file = os.path.abspath(mdb_file)
    sqlite_file = os.path.abspath(sqlite_file)

    if not os.path.exists(mdb_file):
        print(f"❌ File MDB non trovato: {mdb_file}")
        sys.exit(1)

    if not os.path.exists(sqlite_file):
        print(f"❌ Database SQLite non trovato: {sqlite_file}")
        sys.exit(1)

    print("\n" + "="*60)
    print("  SINCRONIZZAZIONE DATABASE ACCESS -> SQLITE")
    print("="*60)
    print(f"  Sorgente: {mdb_file}")
    print(f"  Dest:     {sqlite_file}")
    print("="*60)

    # Verifica che mdb-tools sia installato
    try:
        subprocess.run(["mdb-export", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n❌ mdb-tools non installato!")
        print("   Installa con: sudo apt-get install mdb-tools")
        sys.exit(1)

    # 1. Ottieni lista tabelle da MDB
    print_step("ANALISI TABELLE")
    mdb_tables = get_mdb_tables(mdb_file)
    print(f"  📊 Trovate {len(mdb_tables)} tabelle nel file MDB")

    # 2. Ottieni lista tabelle t_* da SQLite
    sqlite_tables = get_sqlite_tables_with_prefix(sqlite_file, "t_")
    print(f"  📊 Trovate {len(sqlite_tables)} tabelle t_* nel database SQLite")

    # 3. Trova tabelle comuni (dirette e mappate)
    common_tables = []
    table_mapping = {}  # SQLite table -> MDB table

    # Trova tabelle con nome identico
    for t in mdb_tables:
        if t in sqlite_tables:
            common_tables.append(t)
            table_mapping[t] = t  # Stesso nome

    # Aggiungi tabelle con nomi diversi dal mapping
    for sqlite_table, mdb_table in TABLE_NAME_MAPPING.items():
        if sqlite_table in sqlite_tables and mdb_table in mdb_tables:
            if sqlite_table not in common_tables:
                common_tables.append(sqlite_table)
            table_mapping[sqlite_table] = mdb_table

    if not common_tables:
        print("\n❌ Nessuna tabella in comune trovata!")
        print("   Tabelle MDB:", mdb_tables[:5], "...")
        print("   Tabelle SQLite:", sqlite_tables[:5], "...")
        sys.exit(1)

    print(f"\n  ✅ Tabelle da sincronizzare: {len(common_tables)}")
    for sqlite_table in common_tables:
        mdb_table = table_mapping[sqlite_table]
        if sqlite_table == mdb_table:
            print(f"     - {sqlite_table}")
        else:
            print(f"     - {sqlite_table} <- {mdb_table}")

    # Chiedi conferma
    risposta = input("\n⚠️  Tutti i dati delle tabelle t_* verranno cancellati e sostituiti. Continuare? (si/no): ")
    if risposta.lower() not in ['si', 'sì', 's', 'yes', 'y']:
        print("❌ Operazione annullata")
        sys.exit(0)

    # Crea directory temporanea per i CSV
    temp_dir = tempfile.mkdtemp(prefix="mdb_migration_")
    print(f"\n  📁 Directory temporanea: {temp_dir}")

    try:
        # 4. Cancella tutte le tabelle
        conn = sqlite3.connect(sqlite_file)
        clear_all_tables(conn, common_tables)
        conn.close()

        # 5. Migra ogni tabella
        print_step("IMPORTAZIONE DATI")

        success_count = 0
        fail_count = 0

        for sqlite_table in common_tables:
            mdb_table = table_mapping[sqlite_table]
            if migrate_table(mdb_file, sqlite_file, sqlite_table, mdb_table, temp_dir):
                success_count += 1
            else:
                fail_count += 1

        # Riepilogo finale
        print_step("RIEPILOGO")
        print(f"  ✅ Tabelle migrate con successo: {success_count}")
        if fail_count > 0:
            print(f"  ❌ Tabelle con errori: {fail_count}")

        print(f"\n  📊 Database aggiornato: {sqlite_file}")

        # Mostra conteggio finale
        print("\n  Conteggio record per tabella:")
        conn = sqlite3.connect(sqlite_file)
        for table in common_tables:
            count = get_table_count(conn, table)
            if count >= 0:
                print(f"    {table}: {count} record")
        conn.close()

        print("\n" + "="*60)
        print("  ✅ SINCRONIZZAZIONE COMPLETATA!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ ERRORE DURANTE LA MIGRAZIONE:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Pulizia file temporanei
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\n  🧹 File temporanei rimossi")


if __name__ == "__main__":
    main()
