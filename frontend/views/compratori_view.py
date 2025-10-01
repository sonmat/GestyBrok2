"""
Vista Compratori con 3 tabelle:
- t_compratori (sopra, larghezza piena)
- t_dati_compratori (sotto a sinistra)
- t_compratore_cerca (sotto a destra)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import customtkinter as ctk
from tkinter import ttk, messagebox
import requests
from views.anagrafiche_dialogs import CompratoreDialog, DatiCompratoreDialog


class CompratorView(ctk.CTkFrame):
    """Vista compratori con layout a 3 tabelle"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.base_url = "http://localhost:8000"
        self.selected_compratore_id = None

        self.db_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "backend", "db_gesty.db"
        )

        # Dati e stato ordinamento
        self.compratori_data = []
        self.dati_data = []
        self.cerca_data = []

        self.sort_compratori_col = None
        self.sort_compratori_reverse = False
        self.sort_dati_col = None
        self.sort_dati_reverse = False
        self.sort_cerca_col = None
        self.sort_cerca_reverse = False

        self.create_widgets()
        self.load_compratori()

    def create_widgets(self):
        """Crea il layout con 3 tabelle"""
        # Titolo principale
        title_label = ctk.CTkLabel(
            self,
            text="Gestione Compratori",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        # Pulsanti principali per compratori
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            btn_frame,
            text="➕ Nuovo Compratore",
            command=self.nuovo_compratore,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="✏️ Modifica Compratore",
            command=self.modifica_compratore,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Elimina Compratore",
            command=self.elimina_compratore,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Aggiorna",
            command=self.load_compratori,
            width=100
        ).pack(side="right", padx=5)

        # === TABELLA COMPRATORI (sopra) ===
        compratori_frame = ctk.CTkFrame(self)
        compratori_frame.pack(fill="both", expand=False, padx=10, pady=5)

        ctk.CTkLabel(
            compratori_frame,
            text="Lista Compratori",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Treeview compratori con scrollbar
        tree_container = ctk.CTkFrame(compratori_frame)
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        compratori_cols = ("id", "azienda", "indirizzo", "cap", "citta", "stato",
                          "fax", "telefono", "piva", "italiano", "tipo_pagamento", "iva")
        self.tree_compratori = ttk.Treeview(
            tree_container,
            columns=compratori_cols,
            show="headings",
            selectmode="browse",
            height=8
        )

        for col in compratori_cols:
            self.tree_compratori.heading(
                col,
                text=col.replace("_", " ").title(),
                command=lambda c=col: self.sort_compratori(c)
            )
            if col == "id":
                self.tree_compratori.column(col, width=50, anchor="center")
            elif col in ["azienda", "indirizzo"]:
                self.tree_compratori.column(col, width=200, anchor="w")
            else:
                self.tree_compratori.column(col, width=100, anchor="center")

        # Scrollbar per compratori
        vsb_compratori = ttk.Scrollbar(tree_container, orient="vertical",
                                       command=self.tree_compratori.yview)
        hsb_compratori = ttk.Scrollbar(tree_container, orient="horizontal",
                                      command=self.tree_compratori.xview)
        self.tree_compratori.configure(yscrollcommand=vsb_compratori.set,
                                      xscrollcommand=hsb_compratori.set)

        self.tree_compratori.grid(row=0, column=0, sticky="nsew")
        vsb_compratori.grid(row=0, column=1, sticky="ns")
        hsb_compratori.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Bind selezione
        self.tree_compratori.bind("<<TreeviewSelect>>", self.on_compratore_select)

        # === CONTAINER BOTTOM: 2 tabelle affiancate ===
        bottom_container = ctk.CTkFrame(self)
        bottom_container.pack(fill="both", expand=True, padx=10, pady=5)

        # === TABELLA DATI COMPRATORI (sotto sx) ===
        dati_frame = ctk.CTkFrame(bottom_container)
        dati_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(
            dati_frame,
            text="Dati Contatto Compratore",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Pulsanti gestione dati
        dati_btn_frame = ctk.CTkFrame(dati_frame, fg_color="transparent")
        dati_btn_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            dati_btn_frame,
            text="➕ Nuovo Dato",
            command=self.nuovo_dato_compratore,
            width=120
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            dati_btn_frame,
            text="✏️ Modifica",
            command=self.modifica_dato_compratore,
            width=100
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            dati_btn_frame,
            text="🗑️ Elimina",
            command=self.elimina_dato_compratore,
            width=100
        ).pack(side="left", padx=2)

        # Treeview dati compratori
        dati_tree_container = ctk.CTkFrame(dati_frame)
        dati_tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        dati_cols = ("id", "mail", "fax", "telefono", "tipologia", "contatto")
        self.tree_dati = ttk.Treeview(
            dati_tree_container,
            columns=dati_cols,
            show="headings",
            selectmode="browse",
            height=8
        )

        for col in dati_cols:
            self.tree_dati.heading(
                col,
                text=col.replace("_", " ").title(),
                command=lambda c=col: self.sort_dati(c)
            )
            if col == "id":
                self.tree_dati.column(col, width=40, anchor="center")
            else:
                self.tree_dati.column(col, width=120, anchor="w")

        vsb_dati = ttk.Scrollbar(dati_tree_container, orient="vertical",
                                command=self.tree_dati.yview)
        hsb_dati = ttk.Scrollbar(dati_tree_container, orient="horizontal",
                                command=self.tree_dati.xview)
        self.tree_dati.configure(yscrollcommand=vsb_dati.set,
                                xscrollcommand=hsb_dati.set)

        self.tree_dati.grid(row=0, column=0, sticky="nsew")
        vsb_dati.grid(row=0, column=1, sticky="ns")
        hsb_dati.grid(row=1, column=0, sticky="ew")

        dati_tree_container.grid_rowconfigure(0, weight=1)
        dati_tree_container.grid_columnconfigure(0, weight=1)

        # === TABELLA COMPRATORE CERCA (sotto dx) ===
        cerca_frame = ctk.CTkFrame(bottom_container)
        cerca_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(
            cerca_frame,
            text="Cosa Cerca",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Pulsanti gestione ricerche
        cerca_btn_frame = ctk.CTkFrame(cerca_frame, fg_color="transparent")
        cerca_btn_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            cerca_btn_frame,
            text="➕ Nuova Ricerca",
            command=self.nuova_ricerca,
            width=120
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            cerca_btn_frame,
            text="🗑️ Elimina Ricerca",
            command=self.elimina_ricerca,
            width=120
        ).pack(side="left", padx=2)

        # Treeview ricerche
        cerca_tree_container = ctk.CTkFrame(cerca_frame)
        cerca_tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        cerca_cols = ("id", "articolo", "note")
        self.tree_cerca = ttk.Treeview(
            cerca_tree_container,
            columns=cerca_cols,
            show="headings",
            selectmode="browse",
            height=8
        )

        for col in cerca_cols:
            self.tree_cerca.heading(
                col,
                text=col.replace("_", " ").title(),
                command=lambda c=col: self.sort_cerca(c)
            )
            if col == "id":
                self.tree_cerca.column(col, width=40, anchor="center")
            elif col == "articolo":
                self.tree_cerca.column(col, width=200, anchor="w")
            else:
                self.tree_cerca.column(col, width=150, anchor="w")

        vsb_cerca = ttk.Scrollbar(cerca_tree_container, orient="vertical",
                                 command=self.tree_cerca.yview)
        hsb_cerca = ttk.Scrollbar(cerca_tree_container, orient="horizontal",
                                 command=self.tree_cerca.xview)
        self.tree_cerca.configure(yscrollcommand=vsb_cerca.set,
                                 xscrollcommand=hsb_cerca.set)

        self.tree_cerca.grid(row=0, column=0, sticky="nsew")
        vsb_cerca.grid(row=0, column=1, sticky="ns")
        hsb_cerca.grid(row=1, column=0, sticky="ew")

        cerca_tree_container.grid_rowconfigure(0, weight=1)
        cerca_tree_container.grid_columnconfigure(0, weight=1)

    def load_compratori(self):
        """Carica lista compratori"""
        try:
            response = requests.get(f"{self.base_url}/api/compratori")
            if response.status_code == 200:
                self.compratori_data = response.json()
                self.populate_compratori()
        except Exception as e:
            print(f"Errore caricamento compratori: {e}")

    def populate_compratori(self):
        """Popola tabella compratori dai dati in memoria"""
        for item in self.tree_compratori.get_children():
            self.tree_compratori.delete(item)

        for c in self.compratori_data:
            values = (
                c.get("id", ""),
                c.get("azienda", ""),
                c.get("indirizzo", ""),
                c.get("cap", ""),
                c.get("citta", ""),
                c.get("stato", ""),
                c.get("fax", ""),
                c.get("telefono", ""),
                c.get("partita_iva", ""),
                "Sì" if c.get("italiano") else "No",
                c.get("tipo_pagamento", ""),
                c.get("iva", "")
            )
            self.tree_compratori.insert("", "end", values=values,
                                       tags=(str(c.get("id")),))

    def on_compratore_select(self, event):
        """Quando seleziono un compratore, carico dati e ricerche"""
        selection = self.tree_compratori.selection()
        if not selection:
            return

        tags = self.tree_compratori.item(selection[0])['tags']
        if tags:
            self.selected_compratore_id = int(tags[0])
            self.load_dati_compratore()
            self.load_cerca()

    def load_dati_compratore(self):
        """Carica dati contatto del compratore selezionato"""
        if not self.selected_compratore_id:
            return

        try:
            response = requests.get(
                f"{self.base_url}/api/dati-compratori?id_compratore={self.selected_compratore_id}"
            )
            if response.status_code == 200:
                self.dati_data = response.json()
                self.populate_dati()
        except Exception as e:
            print(f"Errore caricamento dati compratore: {e}")

    def populate_dati(self):
        """Popola tabella dati dai dati in memoria"""
        for item in self.tree_dati.get_children():
            self.tree_dati.delete(item)

        for d in self.dati_data:
            values = (
                d.get("id_dati_compratore", ""),
                d.get("mail", ""),
                d.get("fax", ""),
                d.get("telefono", ""),
                d.get("ntel_tipologia", ""),
                d.get("contatto", "")
            )
            self.tree_dati.insert("", "end", values=values,
                                 tags=(str(d.get("id_dati_compratore")),))

    def load_cerca(self):
        """Carica cosa cerca il compratore selezionato"""
        if not self.selected_compratore_id:
            return

        try:
            response = requests.get(
                f"{self.base_url}/api/compratori/{self.selected_compratore_id}/cerca"
            )
            if response.status_code == 200:
                self.cerca_data = response.json()
                self.populate_cerca()
        except Exception as e:
            print(f"Errore caricamento ricerche: {e}")

    def populate_cerca(self):
        """Popola tabella ricerche dai dati in memoria"""
        for item in self.tree_cerca.get_children():
            self.tree_cerca.delete(item)

        for c in self.cerca_data:
            values = (
                c.get("id", ""),
                c.get("articolo_nome", ""),
                c.get("note", "")
            )
            self.tree_cerca.insert("", "end", values=values,
                                  tags=(str(c.get("id")),))

    # === METODI CRUD COMPRATORI ===
    def nuovo_compratore(self):
        dialog = CompratoreDialog(self, self.api_client)
        self.wait_window(dialog)
        if dialog.result:
            self.load_compratori()

    def modifica_compratore(self):
        if not self.selected_compratore_id:
            messagebox.showwarning("Attenzione", "Seleziona un compratore")
            return
        dialog = CompratoreDialog(self, self.api_client, self.selected_compratore_id)
        self.wait_window(dialog)
        self.load_compratori()

    def elimina_compratore(self):
        if not self.selected_compratore_id:
            messagebox.showwarning("Attenzione", "Seleziona un compratore")
            return

        if messagebox.askyesno("Conferma", "Eliminare il compratore selezionato?"):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/compratori/{self.selected_compratore_id}"
                )
                if response.status_code in [200, 204]:
                    self.load_compratori()
                    messagebox.showinfo("Successo", "Compratore eliminato")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    # === METODI CRUD DATI COMPRATORI ===
    def nuovo_dato_compratore(self):
        if not self.selected_compratore_id:
            messagebox.showwarning("Attenzione", "Seleziona prima un compratore")
            return
        dialog = DatiCompratoreDialog(self, self.api_client, self.selected_compratore_id)
        self.wait_window(dialog)
        if dialog.result:
            self.load_dati_compratore()

    def modifica_dato_compratore(self):
        selection = self.tree_dati.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un dato da modificare")
            return

        tags = self.tree_dati.item(selection[0])['tags']
        if not tags:
            return
        dato_id = int(tags[0])

        dialog = DatiCompratoreDialog(self, self.api_client, self.selected_compratore_id, dato_id)
        self.wait_window(dialog)
        self.load_dati_compratore()

    def elimina_dato_compratore(self):
        selection = self.tree_dati.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un dato da eliminare")
            return

        tags = self.tree_dati.item(selection[0])['tags']
        if not tags:
            return

        dato_id = int(tags[0])

        if messagebox.askyesno("Conferma", "Eliminare questo dato?"):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/dati-compratori/{dato_id}"
                )
                if response.status_code in [200, 204]:
                    self.load_dati_compratore()
                    messagebox.showinfo("Successo", "Dato eliminato")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    # === METODI CRUD RICERCHE ===
    def nuova_ricerca(self):
        if not self.selected_compratore_id:
            messagebox.showwarning("Attenzione", "Seleziona prima un compratore")
            return
        messagebox.showinfo("TODO", "Implementare dialog nuova ricerca")

    def elimina_ricerca(self):
        selection = self.tree_cerca.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una ricerca da eliminare")
            return

        tags = self.tree_cerca.item(selection[0])['tags']
        if not tags:
            return

        ricerca_id = int(tags[0])

        if messagebox.askyesno("Conferma", "Eliminare questa ricerca?"):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/cerca/{ricerca_id}"
                )
                if response.status_code in [200, 204]:
                    self.load_cerca()
                    messagebox.showinfo("Successo", "Ricerca eliminata")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    # === METODI ORDINAMENTO ===
    def sort_compratori(self, col):
        """Ordina tabella compratori per colonna"""
        if self.sort_compratori_col == col:
            self.sort_compratori_reverse = not self.sort_compratori_reverse
        else:
            self.sort_compratori_col = col
            self.sort_compratori_reverse = False

        col_map = {
            "id": "id",
            "azienda": "azienda",
            "indirizzo": "indirizzo",
            "cap": "cap",
            "citta": "citta",
            "stato": "stato",
            "fax": "fax",
            "telefono": "telefono",
            "piva": "partita_iva",
            "italiano": "italiano",
            "tipo_pagamento": "tipo_pagamento",
            "iva": "iva"
        }

        sort_key = col_map.get(col, col)

        try:
            self.compratori_data.sort(
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_compratori_reverse
            )
            self.populate_compratori()

            # Aggiorna intestazioni con frecce
            compratori_cols = ("id", "azienda", "indirizzo", "cap", "citta", "stato",
                              "fax", "telefono", "piva", "italiano", "tipo_pagamento", "iva")
            for c in compratori_cols:
                text = c.replace("_", " ").title()
                if c == col:
                    text += " ↓" if self.sort_compratori_reverse else " ↑"
                self.tree_compratori.heading(c, text=text)
        except Exception as e:
            print(f"Errore ordinamento: {e}")

    def sort_dati(self, col):
        """Ordina tabella dati per colonna"""
        if self.sort_dati_col == col:
            self.sort_dati_reverse = not self.sort_dati_reverse
        else:
            self.sort_dati_col = col
            self.sort_dati_reverse = False

        col_map = {
            "id": "id_dati_compratore",
            "mail": "mail",
            "fax": "fax",
            "telefono": "telefono",
            "tipologia": "ntel_tipologia",
            "contatto": "contatto"
        }

        sort_key = col_map.get(col, col)

        try:
            self.dati_data.sort(
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_dati_reverse
            )
            self.populate_dati()

            # Aggiorna intestazioni con frecce
            dati_cols = ("id", "mail", "fax", "telefono", "tipologia", "contatto")
            for c in dati_cols:
                text = c.replace("_", " ").title()
                if c == col:
                    text += " ↓" if self.sort_dati_reverse else " ↑"
                self.tree_dati.heading(c, text=text)
        except Exception as e:
            print(f"Errore ordinamento: {e}")

    def sort_cerca(self, col):
        """Ordina tabella ricerche per colonna"""
        if self.sort_cerca_col == col:
            self.sort_cerca_reverse = not self.sort_cerca_reverse
        else:
            self.sort_cerca_col = col
            self.sort_cerca_reverse = False

        col_map = {
            "id": "id",
            "articolo": "articolo_nome",
            "note": "note"
        }

        sort_key = col_map.get(col, col)

        try:
            self.cerca_data.sort(
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_cerca_reverse
            )
            self.populate_cerca()

            # Aggiorna intestazioni con frecce
            cerca_cols = ("id", "articolo", "note")
            for c in cerca_cols:
                text = c.replace("_", " ").title()
                if c == col:
                    text += " ↓" if self.sort_cerca_reverse else " ↑"
                self.tree_cerca.heading(c, text=text)
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
