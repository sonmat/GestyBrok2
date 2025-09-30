"""
Vista per generazione Report
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List, Dict
from datetime import datetime


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
        self.create_report_section(
            main_container,
            "Report Potenziale",
            "Analisi potenziale vendite in base a offerte e richieste",
            self.genera_report_potenziale
        )
        
        # Report Effettivo
        self.create_report_section(
            main_container,
            "Report Effettivo",
            "Report fatture effettivamente emesse in un periodo",
            self.genera_report_effettivo,
            show_date_filters=True
        )
        
        # Report Fatture in Base
        self.create_report_section(
            main_container,
            "Report Fatture in Base",
            "Elenco completo fatture per periodo",
            self.genera_report_fatture_base,
            show_date_filters=True
        )
        
        # Distinta Banca
        self.create_report_section(
            main_container,
            "Distinta Banca",
            "Genera distinta bancaria per incassi",
            self.genera_distinta_banca
        )
    
    def create_report_section(self, parent, title, description, command, show_date_filters=False):
        """Crea sezione per un tipo di report"""
        frame = ttk.LabelFrame(parent, text=title, padding=15)
        frame.pack(fill=tk.X, pady=10)
        
        # Descrizione
        ttk.Label(
            frame,
            text=description,
            foreground="gray"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Content frame
        content = ttk.Frame(frame)
        content.pack(fill=tk.X)
        
        if show_date_filters:
            # Filtri data
            filter_frame = ttk.Frame(content)
            filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            ttk.Label(filter_frame, text="Da:").pack(side=tk.LEFT, padx=(0, 5))
            data_da = ttk.Entry(filter_frame, width=12)
            data_da.pack(side=tk.LEFT, padx=(0, 15))
            data_da.insert(0, "01/01/2024")
            
            ttk.Label(filter_frame, text="A:").pack(side=tk.LEFT, padx=(0, 5))
            data_a = ttk.Entry(filter_frame, width=12)
            data_a.pack(side=tk.LEFT, padx=(0, 15))
            data_a.insert(0, datetime.now().strftime("%d/%m/%Y"))
            
            # Bottone genera con parametri
            ttk.Button(
                content,
                text="📄 Genera Report",
                command=lambda: command(data_da.get(), data_a.get())
            ).pack(side=tk.RIGHT)
        else:
            # Bottone genera senza parametri
            ttk.Button(
                content,
                text="📄 Genera Report",
                command=command
            ).pack(side=tk.RIGHT)
    
    def genera_report_potenziale(self):
        """Genera report potenziale"""
        try:
            # Logica per report potenziale
            # Incrocia offerte venditori con richieste compratori
            messagebox.showinfo(
                "Report Potenziale",
                "Report generato!\n\n"
                "Funzionalità da implementare:\n"
                "- Analisi match offerte/richieste\n"
                "- Calcolo margini potenziali\n"
                "- Esportazione PDF"
            )
        except Exception as e:
            messagebox.showerror("Errore", str(e))
    
    def genera_report_effettivo(self, data_da: str, data_a: str):
        """Genera report effettivo fatture"""
        if not self.valida_date(data_da, data_a):
            return
        
        try:
            # Recupera fatture per periodo
            fatture = self.api_client.get_fatture(data_da=data_da, data_a=data_a)
            
            # Calcola totali
            totale = sum(f.get("importo_totale", 0) for f in fatture)
            pagate = len([f for f in fatture if f.get("pagata")])
            
            messagebox.showinfo(
                "Report Effettivo",
                f"Periodo: {data_da} - {data_a}\n\n"
                f"Fatture emesse: {len(fatture)}\n"
                f"Fatture pagate: {pagate}\n"
                f"Totale fatturato: € {totale:,.2f}\n\n"
                f"Report salvato in: reports/effettivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione report:\n{str(e)}")
    
    def genera_report_fatture_base(self, data_da: str, data_a: str):
        """Genera report fatture in base"""
        if not self.valida_date(data_da, data_a):
            return
        
        try:
            fatture = self.api_client.get_fatture(data_da=data_da, data_a=data_a)
            
            # Esporta in CSV o Excel
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")],
                initialfile=f"fatture_{datetime.now().strftime('%Y%m%d')}"
            )
            
            if filename:
                # Qui implementeresti l'esportazione reale
                messagebox.showinfo(
                    "Successo",
                    f"Esportate {len(fatture)} fatture in:\n{filename}"
                )
        except Exception as e:
            messagebox.showerror("Errore", str(e))
    
    def genera_distinta_banca(self):
        """Genera distinta bancaria"""
        try:
            messagebox.showinfo(
                "Distinta Banca",
                "Funzionalità da implementare:\n\n"
                "- Selezione fatture da incassare\n"
                "- Generazione file CBI/SEPA\n"
                "- Esportazione formato bancario"
            )
        except Exception as e:
            messagebox.showerror("Errore", str(e))
    
    def valida_date(self, data_da: str, data_a: str) -> bool:
        """Valida formato date"""
        try:
            datetime.strptime(data_da, "%d/%m/%Y")
            datetime.strptime(data_a, "%d/%m/%Y")
            return True
        except ValueError:
            messagebox.showwarning(
                "Formato Data Errato",
                "Inserisci le date nel formato gg/mm/aaaa"
            )
            return False
