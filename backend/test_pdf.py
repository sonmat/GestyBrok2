"""
Script di test per la generazione dei PDF delle conferme d'ordine
"""
from pdf_generator import PDFConfermaOrdine
import os


def test_genera_pdf():
    """Test della generazione PDF"""

    # Dati di esempio
    conferma_data = {
        'id_conferma': 1,
        'n_conf': 'CONF-2024-001',
        'data_conf': '01/10/2025',
        'numero_conferma': 'CONF-2024-001',
        'data_conferma': '01/10/2025',
        'quantita': 1000.0,
        'qta': 1000.0,
        'prezzo': 25.50,
        'provvigione': 2.5,
        'tipologia': 'Standard',
        'note': 'Consegna presso magazzino centrale. Si prega di confermare la data di consegna almeno 48 ore prima.'
    }

    venditore_data_italiano = {
        'id': 1,
        'azienda': 'ABC Import Export S.r.l.',
        'indirizzo': 'Via Roma 123',
        'cap': '20100',
        'citta': 'Milano',
        'piva': 'IT12345678901',
        'partita_iva': 'IT12345678901',
        'telefono': '+39 02 1234567',
        'italiano': 'Si'
    }

    venditore_data_estero = {
        'id': 2,
        'azienda': 'Global Trade Inc.',
        'indirizzo': '456 Market Street',
        'cap': '10001',
        'citta': 'New York, NY',
        'piva': 'US987654321',
        'partita_iva': 'US987654321',
        'telefono': '+1 212 555-1234',
        'italiano': 'No'
    }

    compratore_data_italiano = {
        'id': 1,
        'azienda': 'XYZ Distribuzione S.p.A.',
        'indirizzo': 'Corso Vittorio Emanuele 456',
        'cap': '10121',
        'citta': 'Torino',
        'piva': 'IT98765432109',
        'partita_iva': 'IT98765432109',
        'telefono': '+39 011 9876543',
        'italiano': 'Si'
    }

    compratore_data_estero = {
        'id': 2,
        'azienda': 'European Trading GmbH',
        'indirizzo': 'Hauptstraße 789',
        'cap': '10115',
        'citta': 'Berlin',
        'piva': 'DE123456789',
        'partita_iva': 'DE123456789',
        'telefono': '+49 30 12345678',
        'italiano': 'No'
    }

    articolo_data = {
        'id': 1,
        'nome': 'Grano Duro Biologico',
        'nome_articolo': 'Grano Duro Biologico',
        'unita_misura': 'Q'
    }

    date_consegna_data = [
        {'data_consegna': '15/10/2025', 'qta_consegna': '500'},
        {'data_consegna': '30/10/2025', 'qta_consegna': '500'}
    ]

    # Inizializza il generatore
    pdf_gen = PDFConfermaOrdine()

    # Test 1: Conferma venditore italiano
    print("Generazione PDF: Venditore Italiano...")
    pdf_buffer = pdf_gen.genera_conferma_venditore(
        conferma_data,
        venditore_data_italiano,
        compratore_data_italiano,
        articolo_data,
        date_consegna_data
    )

    output_path = '/home/mattia/GestyBrok2/report/test_venditore_italiano.pdf'
    with open(output_path, 'wb') as f:
        f.write(pdf_buffer.read())
    print(f"✓ Salvato: {output_path}")

    # Test 2: Conferma venditore estero (inglese)
    print("\nGenerazione PDF: Venditore Estero (Inglese)...")
    pdf_buffer = pdf_gen.genera_conferma_venditore(
        conferma_data,
        venditore_data_estero,
        compratore_data_italiano,
        articolo_data,
        date_consegna_data
    )

    output_path = '/home/mattia/GestyBrok2/report/test_venditore_estero_en.pdf'
    with open(output_path, 'wb') as f:
        f.write(pdf_buffer.read())
    print(f"✓ Salvato: {output_path}")

    # Test 3: Conferma compratore italiano
    print("\nGenerazione PDF: Compratore Italiano...")
    pdf_buffer = pdf_gen.genera_conferma_compratore(
        conferma_data,
        venditore_data_italiano,
        compratore_data_italiano,
        articolo_data,
        date_consegna_data
    )

    output_path = '/home/mattia/GestyBrok2/report/test_compratore_italiano.pdf'
    with open(output_path, 'wb') as f:
        f.write(pdf_buffer.read())
    print(f"✓ Salvato: {output_path}")

    # Test 4: Conferma compratore estero (inglese)
    print("\nGenerazione PDF: Compratore Estero (Inglese)...")
    pdf_buffer = pdf_gen.genera_conferma_compratore(
        conferma_data,
        venditore_data_italiano,
        compratore_data_estero,
        articolo_data,
        date_consegna_data
    )

    output_path = '/home/mattia/GestyBrok2/report/test_compratore_estero_en.pdf'
    with open(output_path, 'wb') as f:
        f.write(pdf_buffer.read())
    print(f"✓ Salvato: {output_path}")

    print("\n" + "="*60)
    print("✓ Tutti i test completati con successo!")
    print("="*60)
    print("\nPDF generati nella cartella: /home/mattia/GestyBrok2/report/")
    print("  - test_venditore_italiano.pdf")
    print("  - test_venditore_estero_en.pdf")
    print("  - test_compratore_italiano.pdf")
    print("  - test_compratore_estero_en.pdf")


if __name__ == "__main__":
    test_genera_pdf()
