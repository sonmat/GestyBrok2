"""
Vista Fatture Studio con 2 tabelle dinamiche:
- t_fatture_studio (sopra, tabella principale)
- t_fat_studio_det (sotto, dettagli della fattura selezionata)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import customtkinter as ctk
from tkinter import ttk, messagebox
import requests
from views.fatture_studio_dialogs import FatturaStudioDialog, DettaglioFatturaStudioDialog


class FattureStudioView(ctk.CTkFrame):
    """Vista fatture studio con layout a 2 tabelle"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.base_url = "http://localhost:8000"
        self.selected_fattura_id = None

        # Dati e stato ordinamento
        self.fatture_data = []
        self.dettagli_data = []

        self.sort_fatture_col = None
        self.sort_fatture_reverse = False
        self.sort_dettagli_col = None
        self.sort_dettagli_reverse = False

        self.create_widgets()
        self.load_fatture()

    def create_widgets(self):
        """Crea il layout con 2 tabelle"""
        # Titolo principale
        title_label = ctk.CTkLabel(
            self,
            text="Gestione Fatture Studio",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        # Pulsanti principali per fatture
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            btn_frame,
            text="➕ Nuova Fattura",
            command=self.nuova_fattura,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="✏️ Modifica Fattura",
            command=self.modifica_fattura,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Elimina Fattura",
            command=self.elimina_fattura,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🖨️ Stampa Fattura",
            command=self.stampa_fattura,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Aggiorna",
            command=self.load_fatture,
            width=100
        ).pack(side="right", padx=5)

        # === TABELLA FATTURE STUDIO (sopra) ===
        fatture_frame = ctk.CTkFrame(self)
        fatture_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(
            fatture_frame,
            text="Lista Fatture Studio",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Treeview fatture con scrollbar
        tree_container = ctk.CTkFrame(fatture_frame)
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Colonne di t_fatture_studio
        fatture_cols = ("id_fatt_studio", "n_fat", "data_fat", "nota_acr",
                       "cliente", "t_iva", "t_pagamento", "note", "id_banca")

        self.tree_fatture = ttk.Treeview(
            tree_container,
            columns=fatture_cols,
            show="headings",
            selectmode="browse",
            height=10
        )

        for col in fatture_cols:
            self.tree_fatture.heading(
                col,
                text=col.replace("_", " ").replace("id ", "ID ").title(),
                command=lambda c=col: self.sort_fatture(c)
            )
            if col == "id_fatt_studio":
                self.tree_fatture.column(col, width=80, anchor="center")
            elif col in ["n_fat", "nota_acr"]:
                self.tree_fatture.column(col, width=100, anchor="center")
            elif col == "data_fat":
                self.tree_fatture.column(col, width=100, anchor="center")
            elif col in ["cliente", "t_iva", "t_pagamento", "id_banca"]:
                self.tree_fatture.column(col, width=150, anchor="w")
            elif col == "note":
                self.tree_fatture.column(col, width=200, anchor="w")
            else:
                self.tree_fatture.column(col, width=100, anchor="center")

        # Scrollbar per fatture
        vsb_fatture = ttk.Scrollbar(tree_container, orient="vertical",
                                    command=self.tree_fatture.yview)
        hsb_fatture = ttk.Scrollbar(tree_container, orient="horizontal",
                                   command=self.tree_fatture.xview)
        self.tree_fatture.configure(yscrollcommand=vsb_fatture.set,
                                   xscrollcommand=hsb_fatture.set)

        self.tree_fatture.grid(row=0, column=0, sticky="nsew")
        vsb_fatture.grid(row=0, column=1, sticky="ns")
        hsb_fatture.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Bind selezione
        self.tree_fatture.bind("<<TreeviewSelect>>", self.on_fattura_select)

        # === TABELLA DETTAGLI (sotto) ===
        dettagli_frame = ctk.CTkFrame(self)
        dettagli_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(
            dettagli_frame,
            text="Dettagli Fattura Selezionata",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Pulsanti gestione dettagli
        dettagli_btn_frame = ctk.CTkFrame(dettagli_frame, fg_color="transparent")
        dettagli_btn_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            dettagli_btn_frame,
            text="➕ Nuovo Dettaglio",
            command=self.nuovo_dettaglio,
            width=120
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            dettagli_btn_frame,
            text="✏️ Modifica",
            command=self.modifica_dettaglio,
            width=100
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            dettagli_btn_frame,
            text="🗑️ Elimina",
            command=self.elimina_dettaglio,
            width=100
        ).pack(side="left", padx=2)

        # Treeview dettagli
        dettagli_tree_container = ctk.CTkFrame(dettagli_frame)
        dettagli_tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Colonne di t_fat_studio_det
        dettagli_cols = ("id_fat_studio_det", "compratore", "qta", "prezzo",
                        "provvigione", "tipologia", "data_consegna")

        self.tree_dettagli = ttk.Treeview(
            dettagli_tree_container,
            columns=dettagli_cols,
            show="headings",
            selectmode="browse",
            height=8
        )

        for col in dettagli_cols:
            self.tree_dettagli.heading(
                col,
                text=col.replace("_", " ").replace("id ", "ID ").title(),
                command=lambda c=col: self.sort_dettagli(c)
            )
            if col == "id_fat_studio_det":
                self.tree_dettagli.column(col, width=80, anchor="center")
            elif col == "compratore":
                self.tree_dettagli.column(col, width=200, anchor="w")
            else:
                self.tree_dettagli.column(col, width=120, anchor="center")

        vsb_dettagli = ttk.Scrollbar(dettagli_tree_container, orient="vertical",
                                    command=self.tree_dettagli.yview)
        hsb_dettagli = ttk.Scrollbar(dettagli_tree_container, orient="horizontal",
                                    command=self.tree_dettagli.xview)
        self.tree_dettagli.configure(yscrollcommand=vsb_dettagli.set,
                                    xscrollcommand=hsb_dettagli.set)

        self.tree_dettagli.grid(row=0, column=0, sticky="nsew")
        vsb_dettagli.grid(row=0, column=1, sticky="ns")
        hsb_dettagli.grid(row=1, column=0, sticky="ew")

        dettagli_tree_container.grid_rowconfigure(0, weight=1)
        dettagli_tree_container.grid_columnconfigure(0, weight=1)

    def load_fatture(self):
        """Carica lista fatture studio"""
        try:
            response = requests.get(f"{self.base_url}/api/fatture-studio")
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
                f.get("id_fatt_studio", ""),
                f.get("n_fat", ""),
                f.get("data_fat", ""),
                f.get("nota_acr", ""),
                f.get("cliente_nome", ""),  # Nome invece di ID
                f.get("iva_desc", ""),       # Descrizione invece di ID
                f.get("pagamento_tipo", ""), # Tipo invece di ID
                f.get("note", ""),
                f.get("banca_nome", "")      # Nome invece di ID
            )
            self.tree_fatture.insert("", "end", values=values,
                                    tags=(str(f.get("id_fatt_studio")),))

    def on_fattura_select(self, event):
        """Quando seleziono una fattura, carico i dettagli"""
        selection = self.tree_fatture.selection()
        if not selection:
            return

        tags = self.tree_fatture.item(selection[0])['tags']
        if tags:
            self.selected_fattura_id = int(tags[0])
            self.load_dettagli()

    def load_dettagli(self):
        """Carica dettagli della fattura selezionata"""
        if not self.selected_fattura_id:
            return

        try:
            response = requests.get(
                f"{self.base_url}/api/fatture-studio/{self.selected_fattura_id}/dettagli"
            )
            if response.status_code == 200:
                self.dettagli_data = response.json()
                self.populate_dettagli()
        except Exception as e:
            print(f"Errore caricamento dettagli: {e}")

    def populate_dettagli(self):
        """Popola tabella dettagli dai dati in memoria"""
        for item in self.tree_dettagli.get_children():
            self.tree_dettagli.delete(item)

        for d in self.dettagli_data:
            values = (
                d.get("id_fat_studio_det", ""),
                d.get("compratore_nome", ""),  # Nome invece di ID
                d.get("qta", ""),
                d.get("prezzo", ""),
                d.get("provvigione", ""),
                d.get("tipologia", ""),
                d.get("data_consegna", "")
            )
            self.tree_dettagli.insert("", "end", values=values,
                                     tags=(str(d.get("id_fat_studio_det")),))

    # === METODI CRUD FATTURE ===
    def nuova_fattura(self):
        dialog = FatturaStudioDialog(self, self.api_client)
        self.wait_window(dialog)
        if dialog.result:
            self.load_fatture()

    def modifica_fattura(self):
        if not self.selected_fattura_id:
            messagebox.showwarning("Attenzione", "Seleziona una fattura")
            return
        dialog = FatturaStudioDialog(self, self.api_client, self.selected_fattura_id)
        self.wait_window(dialog)
        self.load_fatture()

    def elimina_fattura(self):
        if not self.selected_fattura_id:
            messagebox.showwarning("Attenzione", "Seleziona una fattura")
            return

        if messagebox.askyesno("Conferma", "Eliminare la fattura selezionata?"):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/fatture-studio/{self.selected_fattura_id}"
                )
                if response.status_code in [200, 204]:
                    self.load_fatture()
                    messagebox.showinfo("Successo", "Fattura eliminata")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    def stampa_fattura(self):
        """Stampa fattura studio (genera PDF)"""
        if not self.selected_fattura_id:
            messagebox.showwarning("Attenzione", "Seleziona una fattura da stampare")
            return

        try:
            # Trova la fattura selezionata per ottenere il numero fattura
            num_fat = None
            for fattura in self.fatture_data:
                if fattura.get('id_fatt_studio') == self.selected_fattura_id:
                    num_fat = fattura.get('n_fat', str(self.selected_fattura_id))
                    break

            if num_fat is None:
                num_fat = str(self.selected_fattura_id)

            # Dialog per scegliere la cartella di destinazione
            from tkinter import filedialog
            import os

            default_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(default_folder):
                default_folder = os.path.expanduser("~")

            download_folder = filedialog.askdirectory(
                title="Scegli dove salvare la fattura",
                initialdir=default_folder
            )

            # Se l'utente annulla, esci
            if not download_folder:
                return

            # Scarica PDF Fattura
            try:
                response = requests.get(
                    f"{self.base_url}/api/fatture-studio/{self.selected_fattura_id}/stampa",
                    stream=True
                )

                if response.status_code == 200:
                    # Estrai nome file dall'header Content-Disposition se disponibile
                    filename = f"Fattura_Studio_{num_fat}.pdf"
                    if 'content-disposition' in response.headers:
                        import re
                        cd = response.headers['content-disposition']
                        filename_match = re.findall('filename=(.+)', cd)
                        if filename_match:
                            filename = filename_match[0].strip('"')

                    filepath = os.path.join(download_folder, filename)
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    messagebox.showinfo("Successo", f"Fattura salvata in:\n{filepath}")
                    print(f"✓ PDF Fattura salvato: {filepath}")
                else:
                    messagebox.showerror("Errore", f"Errore nel generare PDF: {response.status_code}\n{response.text}")

            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvare PDF:\n{str(e)}")
                import traceback
                traceback.print_exc()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la stampa:\n{str(e)}")
            import traceback
            traceback.print_exc()

    # === METODI CRUD DETTAGLI ===
    def nuovo_dettaglio(self):
        if not self.selected_fattura_id:
            messagebox.showwarning("Attenzione", "Seleziona prima una fattura")
            return
        dialog = DettaglioFatturaStudioDialog(self, self.api_client, self.selected_fattura_id)
        self.wait_window(dialog)
        if dialog.result:
            self.load_dettagli()

    def modifica_dettaglio(self):
        selection = self.tree_dettagli.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un dettaglio da modificare")
            return

        tags = self.tree_dettagli.item(selection[0])['tags']
        if not tags:
            return
        dettaglio_id = int(tags[0])

        dialog = DettaglioFatturaStudioDialog(self, self.api_client, self.selected_fattura_id, dettaglio_id)
        self.wait_window(dialog)
        self.load_dettagli()

    def elimina_dettaglio(self):
        selection = self.tree_dettagli.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un dettaglio da eliminare")
            return

        tags = self.tree_dettagli.item(selection[0])['tags']
        if not tags:
            return

        dettaglio_id = int(tags[0])

        if messagebox.askyesno("Conferma", "Eliminare questo dettaglio?"):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/fatture-studio/dettagli/{dettaglio_id}"
                )
                if response.status_code in [200, 204]:
                    self.load_dettagli()
                    messagebox.showinfo("Successo", "Dettaglio eliminato")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    # === METODI ORDINAMENTO ===
    def sort_fatture(self, col):
        """Ordina tabella fatture per colonna"""
        if self.sort_fatture_col == col:
            self.sort_fatture_reverse = not self.sort_fatture_reverse
        else:
            self.sort_fatture_col = col
            self.sort_fatture_reverse = False

        col_map = {
            "id_fatt_studio": "id_fatt_studio",
            "n_fat": "n_fat",
            "data_fat": "data_fat",
            "nota_acr": "nota_acr",
            "cliente": "cliente_nome",
            "t_iva": "iva_desc",
            "t_pagamento": "pagamento_tipo",
            "note": "note",
            "id_banca": "banca_nome"
        }

        sort_key = col_map.get(col, col)

        try:
            self.fatture_data.sort(
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_fatture_reverse
            )
            self.populate_fatture()

            # Aggiorna intestazioni con frecce
            fatture_cols = ("id_fatt_studio", "n_fat", "data_fat", "nota_acr",
                           "cliente", "t_iva", "t_pagamento", "note", "id_banca")
            for c in fatture_cols:
                text = c.replace("_", " ").replace("id ", "ID ").title()
                if c == col:
                    text += " ↓" if self.sort_fatture_reverse else " ↑"
                self.tree_fatture.heading(c, text=text)
        except Exception as e:
            print(f"Errore ordinamento: {e}")

    def sort_dettagli(self, col):
        """Ordina tabella dettagli per colonna"""
        if self.sort_dettagli_col == col:
            self.sort_dettagli_reverse = not self.sort_dettagli_reverse
        else:
            self.sort_dettagli_col = col
            self.sort_dettagli_reverse = False

        col_map = {
            "id_fat_studio_det": "id_fat_studio_det",
            "compratore": "compratore_nome",
            "qta": "qta",
            "prezzo": "prezzo",
            "provvigione": "provvigione",
            "tipologia": "tipologia",
            "data_consegna": "data_consegna"
        }

        sort_key = col_map.get(col, col)

        try:
            self.dettagli_data.sort(
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_dettagli_reverse
            )
            self.populate_dettagli()

            # Aggiorna intestazioni con frecce
            dettagli_cols = ("id_fat_studio_det", "compratore", "qta", "prezzo",
                            "provvigione", "tipologia", "data_consegna")
            for c in dettagli_cols:
                text = c.replace("_", " ").replace("id ", "ID ").title()
                if c == col:
                    text += " ↓" if self.sort_dettagli_reverse else " ↑"
                self.tree_dettagli.heading(c, text=text)
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
