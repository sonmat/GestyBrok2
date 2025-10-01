"""
Script di migrazione per aggiungere foreign key
da t_conferme.condizioni_pag a t_pagamenti.id_pagamento

ATTENZIONE: Questo script modifica la struttura del database!
Esegue un backup prima delle modifiche.
"""
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# Path al database
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db_gesty.db"
BACKUP_PATH = BASE_DIR / f"db_gesty_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def backup_database():
    """Crea backup del database"""
    print(f"📦 Creazione backup: {BACKUP_PATH}")
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"✓ Backup completato!")

def migrate_database():
    """Esegue la migrazione"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("\n🔍 Verifica struttura attuale...")

        # Verifica se la colonna condizioni_pag esiste già come foreign key
        cursor.execute("PRAGMA foreign_key_list(t_conferme)")
        existing_fks = cursor.fetchall()

        # Controlla se esiste già la FK verso t_pagamenti
        has_payment_fk = any(fk[2] == 't_pagamenti' and fk[3] == 'condizioni_pag'
                            for fk in existing_fks)

        if has_payment_fk:
            print("⚠️  La foreign key esiste già!")
            return

        print("\n📊 Dati prima della migrazione:")

        # Mostra le conferme con condizioni_pag
        cursor.execute("""
            SELECT id_conferma, condizioni_pag, n_conf
            FROM t_conferme
            WHERE condizioni_pag IS NOT NULL AND condizioni_pag != ''
            LIMIT 5
        """)
        print("  Esempi di conferme con condizioni_pag:")
        for row in cursor.fetchall():
            print(f"    Conferma {row[0]}: condizioni_pag='{row[1]}', n_conf={row[2]}")

        # Mostra i pagamenti disponibili
        cursor.execute("SELECT id_pagamento, tipo_pagamento FROM t_pagamenti")
        pagamenti = cursor.fetchall()
        print("\n  Pagamenti disponibili:")
        for row in pagamenti:
            print(f"    ID {row[0]}: {row[1]}")

        print("\n⚠️  ATTENZIONE: Per aggiungere una foreign key in SQLite, è necessario ricreare la tabella!")
        print("     Questa operazione potrebbe richiedere qualche secondo...\n")

        # SQLite non supporta ALTER TABLE per aggiungere FK direttamente
        # Dobbiamo ricreare la tabella

        # 1. Disabilita temporaneamente le foreign keys
        cursor.execute("PRAGMA foreign_keys=OFF")

        # 2. Inizia transazione
        cursor.execute("BEGIN TRANSACTION")

        # 3. Rinomina la tabella originale
        cursor.execute("ALTER TABLE t_conferme RENAME TO t_conferme_old")

        # 4. Crea nuova tabella con la foreign key
        cursor.execute("""
            CREATE TABLE t_conferme (
                id_conferma INTEGER PRIMARY KEY,
                compratore INTEGER,
                venditore INTEGER,
                qta TEXT,
                prezzo TEXT,
                articolo INTEGER,
                n_conf TEXT,
                data_conf TEXT,
                provvigione TEXT,
                tipologia TEXT,
                luogo_consegna TEXT,
                condizioni_pag INTEGER,
                note TEXT,
                carico TEXT,
                arrivo TEXT,
                emailv TEXT,
                emailc TEXT,
                FOREIGN KEY (compratore) REFERENCES t_compratori(id_compratore),
                FOREIGN KEY (venditore) REFERENCES t_venditori(id_venditore),
                FOREIGN KEY (articolo) REFERENCES t_articoli(id_articolo),
                FOREIGN KEY (condizioni_pag) REFERENCES t_pagamenti(id_pagamento)
            )
        """)

        # 5. Copia i dati dalla vecchia tabella alla nuova
        # Converte condizioni_pag da TEXT a INTEGER se possibile
        cursor.execute("""
            INSERT INTO t_conferme
            SELECT
                id_conferma,
                compratore,
                venditore,
                qta,
                prezzo,
                articolo,
                n_conf,
                data_conf,
                provvigione,
                tipologia,
                luogo_consegna,
                CASE
                    WHEN condizioni_pag IS NULL OR condizioni_pag = '' THEN NULL
                    WHEN CAST(condizioni_pag AS INTEGER) > 0 THEN CAST(condizioni_pag AS INTEGER)
                    ELSE NULL
                END,
                note,
                carico,
                arrivo,
                emailv,
                emailc
            FROM t_conferme_old
        """)

        # 6. Elimina la vecchia tabella
        cursor.execute("DROP TABLE t_conferme_old")

        # 7. Commit transazione
        cursor.execute("COMMIT")

        # 8. Riabilita le foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")

        print("✓ Migrazione completata!")

        # Verifica i risultati
        print("\n📊 Verifica dati dopo migrazione:")
        cursor.execute("""
            SELECT COUNT(*)
            FROM t_conferme
            WHERE condizioni_pag IS NOT NULL
        """)
        count = cursor.fetchone()[0]
        print(f"  Conferme con condizioni_pag: {count}")

        # Mostra esempi con JOIN
        cursor.execute("""
            SELECT
                c.id_conferma,
                c.n_conf,
                c.condizioni_pag,
                p.tipo_pagamento
            FROM t_conferme c
            LEFT JOIN t_pagamenti p ON c.condizioni_pag = p.id_pagamento
            WHERE c.condizioni_pag IS NOT NULL
            LIMIT 5
        """)
        print("\n  Esempi di conferme con nome pagamento:")
        for row in cursor.fetchall():
            print(f"    Conferma {row[0]} (n_conf={row[1]}): ID pagamento={row[2]}, Nome='{row[3] or 'N/A'}'")

        # Verifica la FK è stata creata
        cursor.execute("PRAGMA foreign_key_list(t_conferme)")
        fks = cursor.fetchall()
        print("\n  Foreign keys presenti:")
        for fk in fks:
            print(f"    {fk[3]} -> {fk[2]}({fk[4]})")

        print("\n✅ Migrazione completata con successo!")
        print(f"📁 Backup disponibile in: {BACKUP_PATH}")

    except Exception as e:
        print(f"\n❌ Errore durante la migrazione: {e}")
        print("⚠️  Eseguendo rollback...")
        cursor.execute("ROLLBACK")
        print("💡 Il database non è stato modificato. Backup disponibile in:", BACKUP_PATH)
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    import sys

    print("="*60)
    print("MIGRAZIONE DATABASE - Aggiunta FK condizioni_pag")
    print("="*60)

    if not DB_PATH.exists():
        print(f"❌ Database non trovato: {DB_PATH}")
        exit(1)

    print(f"📂 Database: {DB_PATH}")
    print(f"📦 Backup: {BACKUP_PATH}")

    # Chiedi conferma
    print("\n⚠️  ATTENZIONE: Questa operazione modificherà il database!")

    # Controlla se è stato passato --yes come parametro
    if '--yes' in sys.argv or '-y' in sys.argv:
        print("Flag --yes rilevato, procedo senza conferma...")
        risposta = 's'
    else:
        risposta = input("Continuare? (s/n): ")

    if risposta.lower() != 's':
        print("❌ Operazione annullata.")
        exit(0)

    # Esegui backup
    backup_database()

    # Esegui migrazione
    migrate_database()

    print("\n" + "="*60)
    print("OPERAZIONE COMPLETATA")
    print("="*60)
