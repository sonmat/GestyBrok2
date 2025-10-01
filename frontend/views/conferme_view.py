"""
Vista Conferme d'Ordine con 3 tabelle dinamiche:
- t_conferme (sopra, larghezza piena)
- t_date_consegna (sotto a sinistra)
- t_fatture (sotto a destra)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import customtkinter as ctk
from tkinter import ttk, messagebox
import requests
import json
from views.conferme_dialogs import ConfermaDialog, DataConsegnaDialog


class ConfermeOrdineView(ctk.CTkFrame):
    """Vista conferme d'ordine con layout a 3 tabelle"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.base_url = "http://localhost:8000"
        self.selected_conferma_id = None

        self.db_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "backend", "db_gesty.db"
        )

        # Dati e stato ordinamento
        self.conferme_data = []
        self.date_data = []
        self.fatture_data = []

        self.sort_conferme_col = None
        self.sort_conferme_reverse = False
        self.sort_date_col = None
        self.sort_date_reverse = False
        self.sort_fatture_col = None
        self.sort_fatture_reverse = False

        self.create_widgets()
        self.load_conferme()

    def create_widgets(self):
        """Crea il layout con 3 tabelle"""
        # Titolo principale
        title_label = ctk.CTkLabel(
            self,
            text="Gestione Conferme d'Ordine",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        # Pulsanti principali per conferme
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            btn_frame,
            text="➕ Nuova Conferma",
            command=self.nuova_conferma,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="✏️ Modifica Conferma",
            command=self.modifica_conferma,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Elimina Conferma",
            command=self.elimina_conferma,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="📄 Stampa Conferma",
            command=self.stampa_conferma,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Aggiorna",
            command=self.load_conferme,
            width=100
        ).pack(side="right", padx=5)

        # === TABELLA CONFERME (sopra) ===
        conferme_frame = ctk.CTkFrame(self)
        conferme_frame.pack(fill="both", expand=False, padx=10, pady=5)

        ctk.CTkLabel(
            conferme_frame,
            text="Lista Conferme d'Ordine",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Treeview conferme con scrollbar
        tree_container = ctk.CTkFrame(conferme_frame)
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Tutte le colonne di t_conferme
        conferme_cols = ("id_conferma", "n_conf", "data_conf", "compratore", "venditore",
                        "articolo", "qta", "prezzo", "provvigione", "tipologia",
                        "luogo_consegna", "condizioni_pag", "carico", "arrivo",
                        "emailv", "emailc", "note")

        self.tree_conferme = ttk.Treeview(
            tree_container,
            columns=conferme_cols,
            show="headings",
            selectmode="browse",
            height=8
        )

        for col in conferme_cols:
            self.tree_conferme.heading(
                col,
                text=col.replace("_", " ").replace("id ", "ID ").title(),
                command=lambda c=col: self.sort_conferme(c)
            )
            if col == "id_conferma":
                self.tree_conferme.column(col, width=50, anchor="center")
            elif col in ["n_conf", "data_conf"]:
                self.tree_conferme.column(col, width=100, anchor="center")
            elif col in ["compratore", "venditore", "articolo", "luogo_consegna"]:
                self.tree_conferme.column(col, width=150, anchor="w")
            elif col in ["note", "condizioni_pag"]:
                self.tree_conferme.column(col, width=200, anchor="w")
            else:
                self.tree_conferme.column(col, width=100, anchor="center")

        # Scrollbar per conferme
        vsb_conferme = ttk.Scrollbar(tree_container, orient="vertical",
                                     command=self.tree_conferme.yview)
        hsb_conferme = ttk.Scrollbar(tree_container, orient="horizontal",
                                    command=self.tree_conferme.xview)
        self.tree_conferme.configure(yscrollcommand=vsb_conferme.set,
                                    xscrollcommand=hsb_conferme.set)

        self.tree_conferme.grid(row=0, column=0, sticky="nsew")
        vsb_conferme.grid(row=0, column=1, sticky="ns")
        hsb_conferme.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Bind selezione
        self.tree_conferme.bind("<<TreeviewSelect>>", self.on_conferma_select)

        # === CONTAINER BOTTOM: 2 tabelle affiancate ===
        bottom_container = ctk.CTkFrame(self)
        bottom_container.pack(fill="both", expand=True, padx=10, pady=5)

        # === TABELLA DATE CONSEGNA (sotto sx) ===
        date_frame = ctk.CTkFrame(bottom_container)
        date_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(
            date_frame,
            text="Date di Consegna",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Pulsanti gestione date
        date_btn_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        date_btn_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            date_btn_frame,
            text="➕ Nuova Data",
            command=self.nuova_data_consegna,
            width=120
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            date_btn_frame,
            text="✏️ Modifica",
            command=self.modifica_data_consegna,
            width=100
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            date_btn_frame,
            text="🗑️ Elimina",
            command=self.elimina_data_consegna,
            width=100
        ).pack(side="left", padx=2)

        # Treeview date consegna
        date_tree_container = ctk.CTkFrame(date_frame)
        date_tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        date_cols = ("id_data_consegna", "data_consegna", "qta_consegna")
        self.tree_date = ttk.Treeview(
            date_tree_container,
            columns=date_cols,
            show="headings",
            selectmode="browse",
            height=8
        )

        for col in date_cols:
            self.tree_date.heading(
                col,
                text=col.replace("_", " ").replace("id ", "ID ").title(),
                command=lambda c=col: self.sort_date(c)
            )
            if col == "id_data_consegna":
                self.tree_date.column(col, width=50, anchor="center")
            else:
                self.tree_date.column(col, width=120, anchor="center")

        vsb_date = ttk.Scrollbar(date_tree_container, orient="vertical",
                                command=self.tree_date.yview)
        hsb_date = ttk.Scrollbar(date_tree_container, orient="horizontal",
                                command=self.tree_date.xview)
        self.tree_date.configure(yscrollcommand=vsb_date.set,
                                xscrollcommand=hsb_date.set)

        self.tree_date.grid(row=0, column=0, sticky="nsew")
        vsb_date.grid(row=0, column=1, sticky="ns")
        hsb_date.grid(row=1, column=0, sticky="ew")

        date_tree_container.grid_rowconfigure(0, weight=1)
        date_tree_container.grid_columnconfigure(0, weight=1)

        # === TABELLA FATTURE (sotto dx) ===
        fatture_frame = ctk.CTkFrame(bottom_container)
        fatture_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(
            fatture_frame,
            text="Fatture Associate",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Pulsanti gestione fatture
        fatture_btn_frame = ctk.CTkFrame(fatture_frame, fg_color="transparent")
        fatture_btn_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            fatture_btn_frame,
            text="📋 Vedi Dettagli",
            command=self.vedi_fattura,
            width=120
        ).pack(side="left", padx=2)

        # Treeview fatture
        fatture_tree_container = ctk.CTkFrame(fatture_frame)
        fatture_tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Tutte le colonne di t_fatture
        fatture_cols = ("id_fattura", "n_fat", "data_fat", "nota_acr",
                       "articolo", "qta", "prezzo", "iva_perc",
                       "data_consegna", "compilato", "fatturata")

        self.tree_fatture = ttk.Treeview(
            fatture_tree_container,
            columns=fatture_cols,
            show="headings",
            selectmode="browse",
            height=8
        )

        for col in fatture_cols:
            self.tree_fatture.heading(
                col,
                text=col.replace("_", " ").replace("id ", "ID ").title(),
                command=lambda c=col: self.sort_fatture(c)
            )
            if col == "id_fattura":
                self.tree_fatture.column(col, width=50, anchor="center")
            elif col in ["compilato", "fatturata"]:
                self.tree_fatture.column(col, width=70, anchor="center")
            else:
                self.tree_fatture.column(col, width=100, anchor="center")

        vsb_fatture = ttk.Scrollbar(fatture_tree_container, orient="vertical",
                                   command=self.tree_fatture.yview)
        hsb_fatture = ttk.Scrollbar(fatture_tree_container, orient="horizontal",
                                   command=self.tree_fatture.xview)
        self.tree_fatture.configure(yscrollcommand=vsb_fatture.set,
                                   xscrollcommand=hsb_fatture.set)

        self.tree_fatture.grid(row=0, column=0, sticky="nsew")
        vsb_fatture.grid(row=0, column=1, sticky="ns")
        hsb_fatture.grid(row=1, column=0, sticky="ew")

        fatture_tree_container.grid_rowconfigure(0, weight=1)
        fatture_tree_container.grid_columnconfigure(0, weight=1)

    def load_conferme(self):
        """Carica lista conferme"""
        try:
            response = requests.get(f"{self.base_url}/api/conferme-ordine")
            if response.status_code == 200:
                self.conferme_data = response.json()
                self.populate_conferme()
        except Exception as e:
            print(f"Errore caricamento conferme: {e}")

    def populate_conferme(self):
        """Popola tabella conferme dai dati in memoria"""
        for item in self.tree_conferme.get_children():
            self.tree_conferme.delete(item)

        for c in self.conferme_data:
            values = (
                c.get("id", ""),
                c.get("n_conf", ""),
                c.get("data_conf", ""),
                c.get("compratore_nome", ""),
                c.get("venditore_nome", ""),
                c.get("articolo_nome", ""),
                c.get("qta", ""),
                c.get("prezzo", ""),
                c.get("provvigione", ""),
                c.get("tipologia", ""),
                c.get("luogo_consegna", ""),
                c.get("condizioni_pag", ""),
                c.get("carico", ""),
                c.get("arrivo", ""),
                c.get("emailv", ""),
                c.get("emailc", ""),
                c.get("note", "")
            )
            self.tree_conferme.insert("", "end", values=values,
                                     tags=(str(c.get("id")),))

    def on_conferma_select(self, event):
        """Quando seleziono una conferma, carico date e fatture"""
        selection = self.tree_conferme.selection()
        if not selection:
            return

        tags = self.tree_conferme.item(selection[0])['tags']
        if tags:
            self.selected_conferma_id = int(tags[0])
            self.load_date_consegna()
            self.load_fatture()

    def load_date_consegna(self):
        """Carica date consegna della conferma selezionata"""
        if not self.selected_conferma_id:
            return

        try:
            response = requests.get(
                f"{self.base_url}/api/date-consegna/by-conferma/{self.selected_conferma_id}"
            )
            if response.status_code == 200:
                self.date_data = response.json()
                self.populate_date()
        except Exception as e:
            print(f"Errore caricamento date consegna: {e}")

    def populate_date(self):
        """Popola tabella date dai dati in memoria"""
        for item in self.tree_date.get_children():
            self.tree_date.delete(item)

        for d in self.date_data:
            values = (
                d.get("id", ""),
                d.get("data_consegna", ""),
                d.get("qta_consegna", "")
            )
            self.tree_date.insert("", "end", values=values,
                                 tags=(str(d.get("id")),))

    def load_fatture(self):
        """Carica fatture della conferma selezionata"""
        if not self.selected_conferma_id:
            return

        try:
            response = requests.get(
                f"{self.base_url}/api/conferme-ordine/{self.selected_conferma_id}/fatture"
            )
            if response.status_code == 200:
                self.fatture_data = response.json()
                self.populate_fatture()
        except Exception as e:
            print(f"Errore caricamento fatture: {e}")

    def populate_fatture(self):
        """Popola tabella fatture dai dati in memoria"""
        for item in self.tree_fatture.get_children():
            self.tree_fatture.delete(item)

        for f in self.fatture_data:
            values = (
                f.get("id_fattura", ""),
                f.get("n_fat", ""),
                f.get("data_fat", ""),
                f.get("nota_acr", ""),
                f.get("articolo", ""),
                f.get("qta", ""),
                f.get("prezzo", ""),
                f.get("iva_perc", ""),
                f.get("data_consegna", ""),
                "Sì" if f.get("compilato") else "No",
                "Sì" if f.get("fatturata") else "No"
            )
            self.tree_fatture.insert("", "end", values=values,
                                    tags=(str(f.get("id_fattura")),))

    # === METODI CRUD CONFERME ===
    def nuova_conferma(self):
        dialog = ConfermaDialog(self, self.api_client)
        self.wait_window(dialog)
        if dialog.result:
            self.load_conferme()

    def modifica_conferma(self):
        if not self.selected_conferma_id:
            messagebox.showwarning("Attenzione", "Seleziona una conferma")
            return
        dialog = ConfermaDialog(self, self.api_client, self.selected_conferma_id)
        self.wait_window(dialog)
        self.load_conferme()

    def elimina_conferma(self):
        if not self.selected_conferma_id:
            messagebox.showwarning("Attenzione", "Seleziona una conferma")
            return

        if messagebox.askyesno("Conferma", "Eliminare la conferma selezionata?"):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/conferme-ordine/{self.selected_conferma_id}"
                )
                if response.status_code in [200, 204]:
                    self.load_conferme()
                    messagebox.showinfo("Successo", "Conferma eliminata")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    def stampa_conferma(self):
        """Stampa conferma d'ordine (genera PDF per venditore e compratore)"""
        if not self.selected_conferma_id:
            messagebox.showwarning("Attenzione", "Seleziona una conferma ordine da stampare")
            return

        selection = self.tree_conferme.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una conferma ordine da stampare")
            return

        try:
            # Leggi valori dalla riga selezionata
            values = self.tree_conferme.item(selection[0])["values"]

            conferme_cols = ("id_conferma", "n_conf", "data_conf", "compratore", "venditore",
                           "articolo", "qta", "prezzo", "provvigione", "tipologia",
                           "luogo_consegna", "condizioni_pag", "carico", "arrivo",
                           "emailv", "emailc", "note")

            conferma_display = {}
            for i, col in enumerate(conferme_cols):
                conferma_display[col] = values[i] if i < len(values) else ""

            # Carica dati aziendali
            config_path = os.path.join(
                os.path.dirname(__file__),
                "..", "..", "config", "company_data.json"
            )

            with open(config_path, 'r', encoding='utf-8') as f:
                company_data = json.load(f)

            # Carica date consegna
            date_consegna = []
            for item in self.tree_date.get_children():
                date_values = self.tree_date.item(item)["values"]
                date_consegna.append({
                    "data": date_values[1] if len(date_values) > 1 else "",
                    "quantita": date_values[2] if len(date_values) > 2 else ""
                })

            date_info = "\n".join([f"  - {d['data']}: {d['quantita']}" for d in date_consegna]) if date_consegna else "  Nessuna data consegna"

            messagebox.showinfo(
                "Stampa Conferma",
                f"Funzione in fase di implementazione.\n\n"
                f"Verranno generati 2 PDF:\n"
                f"1. Conferma per Venditore: {conferma_display.get('venditore', 'N/A')}\n"
                f"2. Conferma per Compratore: {conferma_display.get('compratore', 'N/A')}\n\n"
                f"Conferma N°: {conferma_display.get('n_conf', 'N/A')}\n"
                f"Data: {conferma_display.get('data_conf', 'N/A')}\n"
                f"Articolo: {conferma_display.get('articolo', 'N/A')}\n"
                f"Quantità: {conferma_display.get('qta', 'N/A')}\n"
                f"Prezzo: {conferma_display.get('prezzo', 'N/A')}\n"
                f"Provvigione: {conferma_display.get('provvigione', 'N/A')}\n"
                f"Luogo consegna: {conferma_display.get('luogo_consegna', 'N/A')}\n\n"
                f"Date Consegna:\n{date_info}"
            )

        except Exception as e:
            import traceback
            messagebox.showerror("Errore", f"Errore durante la stampa:\n{str(e)}\n\n{traceback.format_exc()}")

    # === METODI CRUD DATE CONSEGNA ===
    def nuova_data_consegna(self):
        if not self.selected_conferma_id:
            messagebox.showwarning("Attenzione", "Seleziona prima una conferma")
            return
        dialog = DataConsegnaDialog(self, self.api_client, self.selected_conferma_id)
        self.wait_window(dialog)
        if dialog.result:
            self.load_date_consegna()

    def modifica_data_consegna(self):
        selection = self.tree_date.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una data da modificare")
            return

        tags = self.tree_date.item(selection[0])['tags']
        if not tags:
            return
        data_id = int(tags[0])

        dialog = DataConsegnaDialog(self, self.api_client, self.selected_conferma_id, data_id)
        self.wait_window(dialog)
        self.load_date_consegna()

    def elimina_data_consegna(self):
        selection = self.tree_date.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una data da eliminare")
            return

        tags = self.tree_date.item(selection[0])['tags']
        if not tags:
            return

        data_id = int(tags[0])

        if messagebox.askyesno("Conferma", "Eliminare questa data di consegna?"):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/date-consegna/{data_id}"
                )
                if response.status_code in [200, 204]:
                    self.load_date_consegna()
                    messagebox.showinfo("Successo", "Data eliminata")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    # === METODI FATTURE ===
    def vedi_fattura(self):
        selection = self.tree_fatture.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una fattura")
            return
        messagebox.showinfo("TODO", "Implementare visualizzazione dettagli fattura")

    # === METODI ORDINAMENTO ===
    def sort_conferme(self, col):
        """Ordina tabella conferme per colonna"""
        if self.sort_conferme_col == col:
            self.sort_conferme_reverse = not self.sort_conferme_reverse
        else:
            self.sort_conferme_col = col
            self.sort_conferme_reverse = False

        col_map = {
            "id_conferma": "id",
            "n_conf": "n_conf",
            "data_conf": "data_conf",
            "compratore": "compratore_nome",
            "venditore": "venditore_nome",
            "articolo": "articolo_nome",
            "qta": "qta",
            "prezzo": "prezzo",
            "provvigione": "provvigione",
            "tipologia": "tipologia",
            "luogo_consegna": "luogo_consegna",
            "condizioni_pag": "condizioni_pag",
            "carico": "carico",
            "arrivo": "arrivo",
            "emailv": "emailv",
            "emailc": "emailc",
            "note": "note"
        }

        sort_key = col_map.get(col, col)

        try:
            self.conferme_data.sort(
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_conferme_reverse
            )
            self.populate_conferme()

            # Aggiorna intestazioni con frecce
            conferme_cols = ("id_conferma", "n_conf", "data_conf", "compratore", "venditore",
                           "articolo", "qta", "prezzo", "provvigione", "tipologia",
                           "luogo_consegna", "condizioni_pag", "carico", "arrivo",
                           "emailv", "emailc", "note")
            for c in conferme_cols:
                text = c.replace("_", " ").replace("id ", "ID ").title()
                if c == col:
                    text += " ↓" if self.sort_conferme_reverse else " ↑"
                self.tree_conferme.heading(c, text=text)
        except Exception as e:
            print(f"Errore ordinamento: {e}")

    def sort_date(self, col):
        """Ordina tabella date per colonna"""
        if self.sort_date_col == col:
            self.sort_date_reverse = not self.sort_date_reverse
        else:
            self.sort_date_col = col
            self.sort_date_reverse = False

        col_map = {
            "id_data_consegna": "id",
            "data_consegna": "data_consegna",
            "qta_consegna": "qta_consegna"
        }

        sort_key = col_map.get(col, col)

        try:
            self.date_data.sort(
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_date_reverse
            )
            self.populate_date()

            # Aggiorna intestazioni con frecce
            date_cols = ("id_data_consegna", "data_consegna", "qta_consegna")
            for c in date_cols:
                text = c.replace("_", " ").replace("id ", "ID ").title()
                if c == col:
                    text += " ↓" if self.sort_date_reverse else " ↑"
                self.tree_date.heading(c, text=text)
        except Exception as e:
            print(f"Errore ordinamento: {e}")

    def sort_fatture(self, col):
        """Ordina tabella fatture per colonna"""
        if self.sort_fatture_col == col:
            self.sort_fatture_reverse = not self.sort_fatture_reverse
        else:
            self.sort_fatture_col = col
            self.sort_fatture_reverse = False

        col_map = {
            "id_fattura": "id_fattura",
            "n_fat": "n_fat",
            "data_fat": "data_fat",
            "nota_acr": "nota_acr",
            "articolo": "articolo",
            "qta": "qta",
            "prezzo": "prezzo",
            "iva_perc": "iva_perc",
            "data_consegna": "data_consegna",
            "compilato": "compilato",
            "fatturata": "fatturata"
        }

        sort_key = col_map.get(col, col)

        try:
            self.fatture_data.sort(
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_fatture_reverse
            )
            self.populate_fatture()

            # Aggiorna intestazioni con frecce
            fatture_cols = ("id_fattura", "n_fat", "data_fat", "nota_acr",
                          "articolo", "qta", "prezzo", "iva_perc",
                          "data_consegna", "compilato", "fatturata")
            for c in fatture_cols:
                text = c.replace("_", " ").replace("id ", "ID ").title()
                if c == col:
                    text += " ↓" if self.sort_fatture_reverse else " ↑"
                self.tree_fatture.heading(c, text=text)
        except Exception as e:
            print(f"Errore ordinamento: {e}")

    def _sort_key(self, value):
        """Restituisce chiave di ordinamento normalizzata"""
        if value is None:
            return ""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            # Prova a convertire in numero se possibile
            try:
                return float(value.replace(",", "."))
            except:
                return value.lower()
        return str(value).lower()
