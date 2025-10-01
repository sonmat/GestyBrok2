"""
Vista per generazione Report
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List, Dict
from datetime import datetime
import os


class ReportView(ttk.Frame):
    """Vista per generazione report"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client

        self.setup_ui()

    def setup_ui(self):
        """Setup interfaccia"""
        # Container principale con padding
        main_container = ttk.Frame(self, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Titolo
        title = ttk.Label(
            main_container,
            text="📊 Generazione Report",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=(0, 30))

        # Report Potenziale
        self.create_report_potenziale_section(main_container)

        # Report Effettivo
        self.create_report_effettivo_section(main_container)

    def create_report_potenziale_section(self, parent):
        """Crea sezione Report Potenziale"""
        frame = ttk.LabelFrame(parent, text="Report Potenziale", padding=15)
        frame.pack(fill=tk.X, pady=10)

        # Descrizione
        ttk.Label(
            frame,
            text="Analisi potenziale vendite basato su date consegna previste",
            foreground="gray"
        ).pack(anchor=tk.W, pady=(0, 10))

        # Form
        form_frame = ttk.Frame(frame)
        form_frame.pack(fill=tk.X, pady=10)

        # Data Dal
        ttk.Label(form_frame, text="Dal:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.pot_data_dal = ttk.Entry(form_frame, width=15)
        self.pot_data_dal.grid(row=0, column=1, padx=(0, 20))
        self.pot_data_dal.insert(0, "2024-01-01")

        # Data Al
        ttk.Label(form_frame, text="Al:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.pot_data_al = ttk.Entry(form_frame, width=15)
        self.pot_data_al.grid(row=0, column=3, padx=(0, 20))
        self.pot_data_al.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Venditore (opzionale)
        ttk.Label(form_frame, text="Venditore (opzionale):").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))

        # Combo venditore
        self.pot_venditore_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.pot_venditore_combo.grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=(10, 0))
        self.load_venditori_combo(self.pot_venditore_combo)

        # Bottoni
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(
            btn_frame,
            text="📄 Genera PDF",
            command=self.genera_report_potenziale_pdf
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            btn_frame,
            text="👁 Anteprima Dati",
            command=self.anteprima_report_potenziale
        ).pack(side=tk.RIGHT, padx=5)

    def create_report_effettivo_section(self, parent):
        """Crea sezione Report Effettivo"""
        frame = ttk.LabelFrame(parent, text="Report Effettivo", padding=15)
        frame.pack(fill=tk.X, pady=10)

        # Descrizione
        ttk.Label(
            frame,
            text="Report fatture effettivamente emesse basato su dati fatturazione reali",
            foreground="gray"
        ).pack(anchor=tk.W, pady=(0, 10))

        # Form
        form_frame = ttk.Frame(frame)
        form_frame.pack(fill=tk.X, pady=10)

        # Data Dal
        ttk.Label(form_frame, text="Dal:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.eff_data_dal = ttk.Entry(form_frame, width=15)
        self.eff_data_dal.grid(row=0, column=1, padx=(0, 20))
        self.eff_data_dal.insert(0, "2024-01-01")

        # Data Al
        ttk.Label(form_frame, text="Al:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.eff_data_al = ttk.Entry(form_frame, width=15)
        self.eff_data_al.grid(row=0, column=3, padx=(0, 20))
        self.eff_data_al.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Venditore (opzionale)
        ttk.Label(form_frame, text="Venditore (opzionale):").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))

        # Combo venditore
        self.eff_venditore_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.eff_venditore_combo.grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=(10, 0))
        self.load_venditori_combo(self.eff_venditore_combo)

        # Bottoni
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(
            btn_frame,
            text="📄 Genera PDF",
            command=self.genera_report_effettivo_pdf
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            btn_frame,
            text="👁 Anteprima Dati",
            command=self.anteprima_report_effettivo
        ).pack(side=tk.RIGHT, padx=5)

    def load_venditori_combo(self, combo: ttk.Combobox):
        """Carica venditori nella combo"""
        try:
            venditori = self.api_client.get_venditori()
            combo_values = ["Tutti i venditori"]
            self.venditori_map = {0: None}  # 0 = tutti

            for v in venditori:
                nome = v.get("azienda", "")
                combo_values.append(f"{v['id']} - {nome}")
                self.venditori_map[v['id']] = v['id']

            combo['values'] = combo_values
            combo.current(0)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento venditori:\n{str(e)}")

    def get_selected_venditore_id(self, combo: ttk.Combobox) -> Optional[int]:
        """Ottiene ID venditore selezionato"""
        selection = combo.get()
        if selection == "Tutti i venditori":
            return None

        try:
            venditore_id = int(selection.split(" - ")[0])
            return venditore_id
        except:
            return None

    def anteprima_report_potenziale(self):
        """Mostra anteprima dati report potenziale"""
        data_dal = self.pot_data_dal.get()
        data_al = self.pot_data_al.get()
        id_venditore = self.get_selected_venditore_id(self.pot_venditore_combo)

        if not self.valida_date(data_dal, data_al):
            return

        try:
            report_data = self.api_client.get_report_potenziale(data_dal, data_al, id_venditore)
            records = report_data.get('records', [])

            # Calcola totali
            totale_qta = sum(float(r.get('qta_cons', 0) or 0) for r in records)
            totale_euro = sum(float(r.get('euro', 0) or 0) for r in records)

            msg = f"REPORT POTENZIALE\n"
            msg += f"Periodo: {data_dal} - {data_al}\n"
            if id_venditore:
                msg += f"Venditore: ID {id_venditore}\n"
            msg += f"\n"
            msg += f"Totale Righe: {len(records)}\n"
            msg += f"Totale Quantità: {totale_qta:,.2f}\n"
            msg += f"Totale Euro: € {totale_euro:,.2f}\n"

            messagebox.showinfo("Anteprima Report Potenziale", msg)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore recupero dati:\n{str(e)}")

    def anteprima_report_effettivo(self):
        """Mostra anteprima dati report effettivo"""
        data_dal = self.eff_data_dal.get()
        data_al = self.eff_data_al.get()
        id_venditore = self.get_selected_venditore_id(self.eff_venditore_combo)

        if not self.valida_date(data_dal, data_al):
            return

        try:
            report_data = self.api_client.get_report_effettivo(data_dal, data_al, id_venditore)
            records = report_data.get('records', [])

            # Calcola totali
            totale_qta = sum(float(r.get('qta', 0) or 0) for r in records)
            totale_euro = sum(float(r.get('euro', 0) or 0) for r in records)

            msg = f"REPORT EFFETTIVO\n"
            msg += f"Periodo: {data_dal} - {data_al}\n"
            if id_venditore:
                msg += f"Venditore: ID {id_venditore}\n"
            msg += f"\n"
            msg += f"Totale Righe: {len(records)}\n"
            msg += f"Totale Quantità: {totale_qta:,.2f}\n"
            msg += f"Totale Euro: € {totale_euro:,.2f}\n"

            messagebox.showinfo("Anteprima Report Effettivo", msg)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore recupero dati:\n{str(e)}")

    def genera_report_potenziale_pdf(self):
        """Genera e salva PDF report potenziale"""
        data_dal = self.pot_data_dal.get()
        data_al = self.pot_data_al.get()
        id_venditore = self.get_selected_venditore_id(self.pot_venditore_combo)

        if not self.valida_date(data_dal, data_al):
            return

        # Chiedi all'utente dove salvare
        filename = f"report_potenziale_{data_dal}_{data_al}.pdf"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=filename,
            title="Salva Report Potenziale"
        )

        if not filepath:
            return  # Utente ha annullato

        # Controlla se file esiste già
        if os.path.exists(filepath):
            risposta = messagebox.askyesno(
                "Conferma Sovrascrittura",
                f"Il file '{os.path.basename(filepath)}' esiste già.\n\nVuoi sovrascriverlo?"
            )
            if not risposta:
                return

        try:
            # Scarica PDF
            pdf_content = self.api_client.download_report_potenziale_pdf(data_dal, data_al, id_venditore)

            # Salva su disco
            with open(filepath, 'wb') as f:
                f.write(pdf_content)

            messagebox.showinfo(
                "Successo",
                f"Report potenziale generato con successo!\n\nSalvato in:\n{filepath}"
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione PDF:\n{str(e)}")

    def genera_report_effettivo_pdf(self):
        """Genera e salva PDF report effettivo"""
        data_dal = self.eff_data_dal.get()
        data_al = self.eff_data_al.get()
        id_venditore = self.get_selected_venditore_id(self.eff_venditore_combo)

        if not self.valida_date(data_dal, data_al):
            return

        # Chiedi all'utente dove salvare
        filename = f"report_effettivo_{data_dal}_{data_al}.pdf"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=filename,
            title="Salva Report Effettivo"
        )

        if not filepath:
            return  # Utente ha annullato

        # Controlla se file esiste già
        if os.path.exists(filepath):
            risposta = messagebox.askyesno(
                "Conferma Sovrascrittura",
                f"Il file '{os.path.basename(filepath)}' esiste già.\n\nVuoi sovrascriverlo?"
            )
            if not risposta:
                return

        try:
            # Scarica PDF
            pdf_content = self.api_client.download_report_effettivo_pdf(data_dal, data_al, id_venditore)

            # Salva su disco
            with open(filepath, 'wb') as f:
                f.write(pdf_content)

            messagebox.showinfo(
                "Successo",
                f"Report effettivo generato con successo!\n\nSalvato in:\n{filepath}"
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione PDF:\n{str(e)}")

    def valida_date(self, data_dal: str, data_al: str) -> bool:
        """Valida formato date YYYY-MM-DD"""
        try:
            datetime.strptime(data_dal, "%Y-%m-%d")
            datetime.strptime(data_al, "%Y-%m-%d")
            return True
        except ValueError:
            messagebox.showwarning(
                "Formato Data Errato",
                "Inserisci le date nel formato YYYY-MM-DD\n(es: 2024-01-01)"
            )
            return False
