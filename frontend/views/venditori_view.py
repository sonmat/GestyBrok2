"""
Vista Venditori con 3 tabelle:
- t_venditori (sopra, larghezza piena)
- t_dati_venditori (sotto a sinistra)
- t_venditore_offre (sotto a destra)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import customtkinter as ctk
from tkinter import ttk, messagebox
import requests
from views.anagrafiche_dialogs import VenditoreDialog, DatiVenditoreDialog


class VenditoriView(ctk.CTkFrame):
    """Vista venditori con layout a 3 tabelle"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.base_url = "http://localhost:8000"
        self.selected_venditore_id = None

        self.db_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "backend", "db_gesty.db"
        )

        # Dati e stato ordinamento
        self.venditori_data = []
        self.dati_data = []
        self.offre_data = []

        self.sort_venditori_col = None
        self.sort_venditori_reverse = False
        self.sort_dati_col = None
        self.sort_dati_reverse = False
        self.sort_offre_col = None
        self.sort_offre_reverse = False

        self.create_widgets()
        self.load_venditori()

    def create_widgets(self):
        """Crea il layout con 3 tabelle"""
        # Titolo principale
        title_label = ctk.CTkLabel(
            self,
            text="Gestione Venditori",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        # Pulsanti principali per venditori
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            btn_frame,
            text="➕ Nuovo Venditore",
            command=self.nuovo_venditore,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="✏️ Modifica Venditore",
            command=self.modifica_venditore,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Elimina Venditore",
            command=self.elimina_venditore,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Aggiorna",
            command=self.load_venditori,
            width=100
        ).pack(side="right", padx=5)

        # === TABELLA VENDITORI (sopra) ===
        venditori_frame = ctk.CTkFrame(self)
        venditori_frame.pack(fill="both", expand=False, padx=10, pady=5)

        ctk.CTkLabel(
            venditori_frame,
            text="Lista Venditori",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Treeview venditori con scrollbar
        tree_container = ctk.CTkFrame(venditori_frame)
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        venditori_cols = ("id", "azienda", "indirizzo", "cap", "citta", "stato",
                         "fax", "telefono", "piva", "italiano", "tipo_pagamento", "iva")
        self.tree_venditori = ttk.Treeview(
            tree_container,
            columns=venditori_cols,
            show="headings",
            selectmode="browse",
            height=8
        )

        for col in venditori_cols:
            self.tree_venditori.heading(
                col,
                text=col.replace("_", " ").title(),
                command=lambda c=col: self.sort_venditori(c)
            )
            if col == "id":
                self.tree_venditori.column(col, width=50, anchor="center")
            elif col in ["azienda", "indirizzo"]:
                self.tree_venditori.column(col, width=200, anchor="w")
            else:
                self.tree_venditori.column(col, width=100, anchor="center")

        # Scrollbar verticale per venditori
        vsb_venditori = ttk.Scrollbar(tree_container, orient="vertical",
                                      command=self.tree_venditori.yview)
        hsb_venditori = ttk.Scrollbar(tree_container, orient="horizontal",
                                     command=self.tree_venditori.xview)
        self.tree_venditori.configure(yscrollcommand=vsb_venditori.set,
                                     xscrollcommand=hsb_venditori.set)

        self.tree_venditori.grid(row=0, column=0, sticky="nsew")
        vsb_venditori.grid(row=0, column=1, sticky="ns")
        hsb_venditori.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Info totale record
        self.info_venditori_label = ctk.CTkLabel(
            venditori_frame,
            text="Totale venditori: 0",
            font=("Arial", 10, "italic")
        )
        self.info_venditori_label.pack(pady=5)

        # Bind selezione
        self.tree_venditori.bind("<<TreeviewSelect>>", self.on_venditore_select)

        # === CONTAINER BOTTOM: 2 tabelle affiancate ===
        bottom_container = ctk.CTkFrame(self)
        bottom_container.pack(fill="both", expand=True, padx=10, pady=5)

        # === TABELLA DATI VENDITORI (sotto sx) ===
        dati_frame = ctk.CTkFrame(bottom_container)
        dati_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(
            dati_frame,
            text="Dati Contatto Venditore",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Pulsanti gestione dati
        dati_btn_frame = ctk.CTkFrame(dati_frame, fg_color="transparent")
        dati_btn_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            dati_btn_frame,
            text="➕ Nuovo Dato",
            command=self.nuovo_dato_venditore,
            width=120
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            dati_btn_frame,
            text="✏️ Modifica",
            command=self.modifica_dato_venditore,
            width=100
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            dati_btn_frame,
            text="🗑️ Elimina",
            command=self.elimina_dato_venditore,
            width=100
        ).pack(side="left", padx=2)

        # Treeview dati venditori
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

        # Info totale record dati
        self.info_dati_label = ctk.CTkLabel(
            dati_frame,
            text="Totale contatti: 0",
            font=("Arial", 9, "italic")
        )
        self.info_dati_label.pack(pady=2)

        # === TABELLA VENDITORE OFFRE (sotto dx) ===
        offre_frame = ctk.CTkFrame(bottom_container)
        offre_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(
            offre_frame,
            text="Cosa Offre",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Pulsanti gestione offerte
        offre_btn_frame = ctk.CTkFrame(offre_frame, fg_color="transparent")
        offre_btn_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            offre_btn_frame,
            text="➕ Nuova Offerta",
            command=self.nuova_offerta,
            width=120
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            offre_btn_frame,
            text="🗑️ Elimina Offerta",
            command=self.elimina_offerta,
            width=120
        ).pack(side="left", padx=2)

        # Treeview offerte
        offre_tree_container = ctk.CTkFrame(offre_frame)
        offre_tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        offre_cols = ("id", "articolo", "prezzo", "provvigione", "tipologia")
        self.tree_offre = ttk.Treeview(
            offre_tree_container,
            columns=offre_cols,
            show="headings",
            selectmode="browse",
            height=8
        )

        for col in offre_cols:
            self.tree_offre.heading(
                col,
                text=col.replace("_", " ").title(),
                command=lambda c=col: self.sort_offre(c)
            )
            if col == "id":
                self.tree_offre.column(col, width=40, anchor="center")
            elif col == "articolo":
                self.tree_offre.column(col, width=200, anchor="w")
            else:
                self.tree_offre.column(col, width=100, anchor="center")

        vsb_offre = ttk.Scrollbar(offre_tree_container, orient="vertical",
                                 command=self.tree_offre.yview)
        hsb_offre = ttk.Scrollbar(offre_tree_container, orient="horizontal",
                                 command=self.tree_offre.xview)
        self.tree_offre.configure(yscrollcommand=vsb_offre.set,
                                 xscrollcommand=hsb_offre.set)

        self.tree_offre.grid(row=0, column=0, sticky="nsew")
        vsb_offre.grid(row=0, column=1, sticky="ns")
        hsb_offre.grid(row=1, column=0, sticky="ew")

        offre_tree_container.grid_rowconfigure(0, weight=1)
        offre_tree_container.grid_columnconfigure(0, weight=1)

        # Info totale record offerte
        self.info_offre_label = ctk.CTkLabel(
            offre_frame,
            text="Totale offerte: 0",
            font=("Arial", 9, "italic")
        )
        self.info_offre_label.pack(pady=2)

    def load_venditori(self):
        """Carica lista venditori"""
        try:
            response = requests.get(f"{self.base_url}/api/venditori")
            if response.status_code == 200:
                self.venditori_data = response.json()
                self.populate_venditori()
        except Exception as e:
            print(f"Errore caricamento venditori: {e}")

    def populate_venditori(self):
        """Popola tabella venditori dai dati in memoria"""
        for item in self.tree_venditori.get_children():
            self.tree_venditori.delete(item)

        for v in self.venditori_data:
            values = (
                v.get("id", ""),
                v.get("azienda", ""),
                v.get("indirizzo", ""),
                v.get("cap", ""),
                v.get("citta", ""),
                v.get("stato", ""),
                v.get("fax", ""),
                v.get("telefono", ""),
                v.get("partita_iva", ""),
                "Sì" if v.get("italiano") else "No",
                v.get("tipo_pagamento", ""),
                v.get("iva", "")
            )
            self.tree_venditori.insert("", "end", values=values,
                                      tags=(str(v.get("id")),))

        # Aggiorna contatore
        self.info_venditori_label.configure(text=f"Totale venditori: {len(self.venditori_data)}")

    def on_venditore_select(self, event):
        """Quando seleziono un venditore, carico dati e offerte"""
        selection = self.tree_venditori.selection()
        if not selection:
            return

        tags = self.tree_venditori.item(selection[0])['tags']
        if tags:
            self.selected_venditore_id = int(tags[0])
            self.load_dati_venditore()
            self.load_offre()

    def load_dati_venditore(self):
        """Carica dati contatto del venditore selezionato"""
        if not self.selected_venditore_id:
            return

        try:
            response = requests.get(
                f"{self.base_url}/api/dati-venditori?id_venditore={self.selected_venditore_id}"
            )
            if response.status_code == 200:
                self.dati_data = response.json()
                self.populate_dati()
        except Exception as e:
            print(f"Errore caricamento dati venditore: {e}")

    def populate_dati(self):
        """Popola tabella dati dai dati in memoria"""
        for item in self.tree_dati.get_children():
            self.tree_dati.delete(item)

        for d in self.dati_data:
            values = (
                d.get("id_dati_venditore", ""),
                d.get("mail", ""),
                d.get("fax", ""),
                d.get("telefono", ""),
                d.get("ntel_tipologia", ""),
                d.get("contatto", "")
            )
            self.tree_dati.insert("", "end", values=values,
                                 tags=(str(d.get("id_dati_venditore")),))

        # Aggiorna contatore
        self.info_dati_label.configure(text=f"Totale contatti: {len(self.dati_data)}")

    def load_offre(self):
        """Carica cosa offre il venditore selezionato"""
        if not self.selected_venditore_id:
            return

        try:
            response = requests.get(
                f"{self.base_url}/api/venditori/{self.selected_venditore_id}/offre"
            )
            if response.status_code == 200:
                self.offre_data = response.json()
                self.populate_offre()
        except Exception as e:
            print(f"Errore caricamento offerte: {e}")

    def populate_offre(self):
        """Popola tabella offerte dai dati in memoria"""
        for item in self.tree_offre.get_children():
            self.tree_offre.delete(item)

        for o in self.offre_data:
            values = (
                o.get("id", ""),
                o.get("articolo_nome", ""),
                o.get("prezzo", ""),
                o.get("provvigione", ""),
                o.get("tipologia", "")
            )
            self.tree_offre.insert("", "end", values=values,
                                  tags=(str(o.get("id")),))

        # Aggiorna contatore
        self.info_offre_label.configure(text=f"Totale offerte: {len(self.offre_data)}")

    # === METODI CRUD VENDITORI ===
    def nuovo_venditore(self):
        dialog = VenditoreDialog(self, self.api_client)
        self.wait_window(dialog)
        if dialog.result:
            self.load_venditori()

    def modifica_venditore(self):
        if not self.selected_venditore_id:
            messagebox.showwarning("Attenzione", "Seleziona un venditore")
            return
        dialog = VenditoreDialog(self, self.api_client, self.selected_venditore_id)
        self.wait_window(dialog)
        self.load_venditori()

    def elimina_venditore(self):
        if not self.selected_venditore_id:
            messagebox.showwarning("Attenzione", "Seleziona un venditore")
            return

        if messagebox.askyesno("Conferma", "Eliminare il venditore selezionato?"):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/venditori/{self.selected_venditore_id}"
                )
                if response.status_code in [200, 204]:
                    self.load_venditori()
                    messagebox.showinfo("Successo", "Venditore eliminato")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    # === METODI CRUD DATI VENDITORI ===
    def nuovo_dato_venditore(self):
        if not self.selected_venditore_id:
            messagebox.showwarning("Attenzione", "Seleziona prima un venditore")
            return
        dialog = DatiVenditoreDialog(self, self.api_client, self.selected_venditore_id)
        self.wait_window(dialog)
        if dialog.result:
            self.load_dati_venditore()

    def modifica_dato_venditore(self):
        selection = self.tree_dati.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un dato da modificare")
            return

        tags = self.tree_dati.item(selection[0])['tags']
        if not tags:
            return
        dato_id = int(tags[0])

        dialog = DatiVenditoreDialog(self, self.api_client, self.selected_venditore_id, dato_id)
        self.wait_window(dialog)
        self.load_dati_venditore()

    def elimina_dato_venditore(self):
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
                    f"{self.base_url}/api/dati-venditori/{dato_id}"
                )
                if response.status_code in [200, 204]:
                    self.load_dati_venditore()
                    messagebox.showinfo("Successo", "Dato eliminato")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    # === METODI CRUD OFFERTE ===
    def nuova_offerta(self):
        if not self.selected_venditore_id:
            messagebox.showwarning("Attenzione", "Seleziona prima un venditore")
            return
        messagebox.showinfo("TODO", "Implementare dialog nuova offerta")

    def elimina_offerta(self):
        selection = self.tree_offre.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un'offerta da eliminare")
            return

        tags = self.tree_offre.item(selection[0])['tags']
        if not tags:
            return

        offerta_id = int(tags[0])

        if messagebox.askyesno("Conferma", "Eliminare questa offerta?"):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/offre/{offerta_id}"
                )
                if response.status_code in [200, 204]:
                    self.load_offre()
                    messagebox.showinfo("Successo", "Offerta eliminata")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    # === METODI ORDINAMENTO ===
    def sort_venditori(self, col):
        """Ordina tabella venditori per colonna"""
        if self.sort_venditori_col == col:
            self.sort_venditori_reverse = not self.sort_venditori_reverse
        else:
            self.sort_venditori_col = col
            self.sort_venditori_reverse = False

        # Mappa colonne display -> chiavi API
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
            self.venditori_data.sort(
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_venditori_reverse
            )
            self.populate_venditori()

            # Aggiorna intestazioni con frecce
            venditori_cols = ("id", "azienda", "indirizzo", "cap", "citta", "stato",
                             "fax", "telefono", "piva", "italiano", "tipo_pagamento", "iva")
            for c in venditori_cols:
                text = c.replace("_", " ").title()
                if c == col:
                    text += " ↓" if self.sort_venditori_reverse else " ↑"
                self.tree_venditori.heading(c, text=text)
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
            "id": "id_dati_venditore",
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

    def sort_offre(self, col):
        """Ordina tabella offerte per colonna"""
        if self.sort_offre_col == col:
            self.sort_offre_reverse = not self.sort_offre_reverse
        else:
            self.sort_offre_col = col
            self.sort_offre_reverse = False

        col_map = {
            "id": "id",
            "articolo": "articolo_nome",
            "prezzo": "prezzo",
            "provvigione": "provvigione",
            "tipologia": "tipologia"
        }

        sort_key = col_map.get(col, col)

        try:
            self.offre_data.sort(
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_offre_reverse
            )
            self.populate_offre()

            # Aggiorna intestazioni con frecce
            offre_cols = ("id", "articolo", "prezzo", "provvigione", "tipologia")
            for c in offre_cols:
                text = c.replace("_", " ").title()
                if c == col:
                    text += " ↓" if self.sort_offre_reverse else " ↑"
                self.tree_offre.heading(c, text=text)
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
