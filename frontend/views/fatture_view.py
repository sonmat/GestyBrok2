"""
Vista per gestione Fatture
Con funzionalità generazione automatica
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict
from datetime import datetime


class FattureView(ttk.Frame):
    """Vista fatture con generazione automatica"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_id: Optional[int] = None
        self.fatture = []
        self.sort_column = None
        self.sort_reverse = False

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup interfaccia"""
        # Toolbar con filtri
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            toolbar,
            text="Genera Fatture",
            command=self.apri_dialog_genera
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(toolbar, text="Aggiorna", command=self.load_data).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Filtri data
        ttk.Label(toolbar, text="Da:").pack(side=tk.LEFT, padx=5)
        self.data_da_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.data_da_var, width=12).pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar, text="A:").pack(side=tk.LEFT, padx=5)
        self.data_a_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.data_a_var, width=12).pack(side=tk.LEFT, padx=2)

        ttk.Button(toolbar, text="Filtra", command=self.filtra_date).pack(side=tk.LEFT, padx=5)

        # Tabella fatture
        table_frame = ttk.LabelFrame(self, text="Fatture", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("id", "numero", "data", "cliente_id", "importo_tot", "pagata", "data_pag")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="tree headings")

        # Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)

        # Configurazione colonne
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("numero", width=150)
        self.tree.column("data", width=100, anchor=tk.CENTER)
        self.tree.column("cliente_id", width=100, anchor=tk.CENTER)
        self.tree.column("importo_tot", width=120, anchor=tk.E)
        self.tree.column("pagata", width=80, anchor=tk.CENTER)
        self.tree.column("data_pag", width=100, anchor=tk.CENTER)

        # Headers con ordinamento
        headers = {
            "id": "ID",
            "numero": "Numero Fattura",
            "data": "Data",
            "cliente_id": "Cliente",
            "importo_tot": "Importo",
            "pagata": "Pagata",
            "data_pag": "Data Pag."
        }

        for col, header in headers.items():
            self.tree.heading(col, text=header, command=lambda c=col: self.sort_by(c))

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Tag per fatture pagate/non pagate
        self.tree.tag_configure("pagata", background="#d4edda")
        self.tree.tag_configure("non_pagata", background="#fff3cd")

    def load_data(self):
        """Carica fatture"""
        try:
            self.fatture = self.api_client.get_fatture()
            self.populate_table(self.fatture)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare fatture:\n{str(e)}")

    def populate_table(self, data: List[Dict]):
        """Popola tabella"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for f in data:
            values = (
                f.get("id"),
                f.get("numero_fattura", ""),
                f.get("data_fattura", ""),
                f.get("cliente_nome", f.get("cliente_id", "")),
                f"€ {f.get('importo_totale', 0):.2f}" if f.get('importo_totale') else "",
                "Si" if f.get("pagata") else "No",
                f.get("data_pagamento", "")
            )

            tag = "pagata" if f.get("pagata") else "non_pagata"
            self.tree.insert("", tk.END, values=values, tags=(tag,))

    def sort_by(self, col):
        """Ordina per colonna"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        col_map = {
            "id": "id",
            "numero": "numero_fattura",
            "data": "data_fattura",
            "cliente_id": "cliente_id",
            "importo_tot": "importo_totale",
            "pagata": "pagata",
            "data_pag": "data_pagamento"
        }
        sort_key = col_map.get(col, col)

        try:
            sorted_data = sorted(
                self.fatture,
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_reverse
            )
            self.populate_table(sorted_data)

            # Aggiorna intestazione con freccia
            headers = {
                "id": "ID",
                "numero": "Numero Fattura",
                "data": "Data",
                "cliente_id": "Cliente",
                "importo_tot": "Importo",
                "pagata": "Pagata",
                "data_pag": "Data Pag."
            }
            for c, header in headers.items():
                text = header
                if c == col:
                    text += " ↓" if self.sort_reverse else " ↑"
                self.tree.heading(c, text=text)
        except:
            pass

    def _sort_key(self, value):
        """Chiave ordinamento"""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            try:
                return float(value.replace(',', '.').replace('€', '').strip())
            except:
                return value.lower()
        return str(value)
    
    def filtra_date(self):
        """Filtra per range date"""
        data_da = self.data_da_var.get()
        data_a = self.data_a_var.get()
        
        try:
            filters = {}
            if data_da:
                filters["data_da"] = data_da
            if data_a:
                filters["data_a"] = data_a
            
            fatture_filtrate = self.api_client.get_fatture(**filters)
            self.populate_table(fatture_filtrate)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel filtro:\n{str(e)}")
    
    def apri_dialog_genera(self):
        """Apre dialog per generazione fatture"""
        GeneraFattureDialog(self, self.api_client, callback=self.load_data)


class GeneraFattureDialog(tk.Toplevel):
    """Dialog per generazione automatica fatture"""
    
    def __init__(self, parent, api_client, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.callback = callback
        
        self.title("Genera Fatture Automaticamente")
        self.geometry("500x400")
        self.resizable(False, False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog"""
        # Frame principale
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Istruzioni
        ttk.Label(
            main_frame,
            text="Seleziona i mesi per cui generare le fatture:",
            font=("Arial", 10, "bold")
        ).pack(pady=(0, 20))
        
        # Anno
        anno_frame = ttk.Frame(main_frame)
        anno_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(anno_frame, text="Anno:").pack(side=tk.LEFT, padx=5)
        self.anno_var = tk.StringVar(value=str(datetime.now().year))
        ttk.Entry(anno_frame, textvariable=self.anno_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Frame per checkbutton mesi
        mesi_frame = ttk.LabelFrame(main_frame, text="Mesi", padding=10)
        mesi_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Checkbutton per ogni mese
        self.mesi_vars = {}
        mesi_nomi = [
            "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
            "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
        ]
        
        for i, mese in enumerate(mesi_nomi, 1):
            var = tk.BooleanVar(value=False)
            self.mesi_vars[f"{i:02d}"] = var
            
            ttk.Checkbutton(
                mesi_frame,
                text=mese,
                variable=var
            ).grid(row=i//3, column=i%3, sticky=tk.W, padx=10, pady=5)
        
        # Bottoni selezione rapida
        quick_frame = ttk.Frame(main_frame)
        quick_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            quick_frame,
            text="Seleziona Tutti",
            command=self.seleziona_tutti
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            quick_frame,
            text="Deseleziona Tutti",
            command=self.deseleziona_tutti
        ).pack(side=tk.LEFT, padx=5)
        
        # Bottoni azione
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            btn_frame,
            text="Genera",
            command=self.genera
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Annulla",
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def seleziona_tutti(self):
        """Seleziona tutti i mesi"""
        for var in self.mesi_vars.values():
            var.set(True)
    
    def deseleziona_tutti(self):
        """Deseleziona tutti i mesi"""
        for var in self.mesi_vars.values():
            var.set(False)
    
    def genera(self):
        """Genera fatture per mesi selezionati"""
        mesi_selezionati = [
            mese for mese, var in self.mesi_vars.items() if var.get()
        ]
        
        if not mesi_selezionati:
            messagebox.showwarning("Attenzione", "Seleziona almeno un mese")
            return
        
        try:
            anno = int(self.anno_var.get())
        except ValueError:
            messagebox.showerror("Errore", "Anno non valido")
            return
        
        # Conferma
        msg = f"Generare fatture per {len(mesi_selezionati)} mese/i dell'anno {anno}?"
        if not messagebox.askyesno("Conferma", msg):
            return
        
        try:
            risultato = self.api_client.genera_fatture(mesi_selezionati, anno)
            messagebox.showinfo(
                "Successo",
                f"Generate {len(risultato)} fatture con successo"
            )
            
            if self.callback:
                self.callback()
            
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione:\n{str(e)}")