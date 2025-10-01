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
from tkinter import ttk, messagebox, filedialog
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

        # Info totale record
        self.info_conferme_label = ctk.CTkLabel(
            conferme_frame,
            text="Totale conferme: 0",
            font=("Arial", 10, "italic")
        )
        self.info_conferme_label.pack(pady=5)

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

        # Info totale record date
        self.info_date_label = ctk.CTkLabel(
            date_frame,
            text="Totale date: 0",
            font=("Arial", 9, "italic")
        )
        self.info_date_label.pack(pady=2)

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

        # Info totale record fatture
        self.info_fatture_label = ctk.CTkLabel(
            fatture_frame,
            text="Totale fatture: 0",
            font=("Arial", 9, "italic")
        )
        self.info_fatture_label.pack(pady=2)

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

        # Aggiorna contatore
        self.info_conferme_label.configure(text=f"Totale conferme: {len(self.conferme_data)}")

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

        # Aggiorna contatore
        self.info_date_label.configure(text=f"Totale date: {len(self.date_data)}")

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
            # Converti tutti i valori in stringhe, gestendo None/NULL
            values = (
                str(f.get("id_fattura", "")) if f.get("id_fattura") is not None else "",
                str(f.get("n_fat", "")) if f.get("n_fat") not in [None, ""] else "",
                str(f.get("data_fat", "")) if f.get("data_fat") not in [None, ""] else "",
                str(f.get("nota_acr", "")) if f.get("nota_acr") not in [None, ""] else "",
                str(f.get("articolo", "")) if f.get("articolo") not in [None, ""] else "",
                str(f.get("qta", "")) if f.get("qta") not in [None, ""] else "",
                str(f.get("prezzo", "")) if f.get("prezzo") not in [None, ""] else "",
                str(f.get("iva_perc", "")) if f.get("iva_perc") not in [None, ""] else "",
                str(f.get("data_consegna", "")) if f.get("data_consegna") not in [None, ""] else "",
                "Sì" if f.get("compilato") == 1 else ("No" if f.get("compilato") == 0 else ""),
                "Sì" if f.get("fatturata") == 1 else ("No" if f.get("fatturata") == 0 else "")
            )
            self.tree_fatture.insert("", "end", values=values,
                                    tags=(str(f.get("id_fattura")),))

        # Aggiorna contatore
        self.info_fatture_label.configure(text=f"Totale fatture: {len(self.fatture_data)}")

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

            num_conf = conferma_display.get('n_conf', str(self.selected_conferma_id))

            # Dialog per scegliere la cartella di destinazione
            default_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(default_folder):
                default_folder = os.path.expanduser("~")

            download_folder = filedialog.askdirectory(
                title="Scegli dove salvare le conferme d'ordine",
                initialdir=default_folder
            )

            # Se l'utente annulla, esci
            if not download_folder:
                return

            # Scarica PDF Venditore
            try:
                response_v = requests.get(
                    f"{self.base_url}/api/conferme-ordine/{self.selected_conferma_id}/stampa-venditore",
                    stream=True
                )

                if response_v.status_code == 200:
                    # Estrai nome file dall'header Content-Disposition se disponibile
                    filename_v = f"Conferma_Venditore_{num_conf}.pdf"
                    if 'content-disposition' in response_v.headers:
                        import re
                        cd = response_v.headers['content-disposition']
                        filename_match = re.findall('filename=(.+)', cd)
                        if filename_match:
                            filename_v = filename_match[0].strip('"')

                    filepath_v = os.path.join(download_folder, filename_v)
                    with open(filepath_v, 'wb') as f:
                        for chunk in response_v.iter_content(chunk_size=8192):
                            f.write(chunk)

                    print(f"✓ PDF Venditore salvato: {filepath_v}")
                else:
                    messagebox.showerror("Errore", f"Errore nel generare PDF Venditore: {response_v.status_code}")
                    return

            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvare PDF Venditore:\n{str(e)}")
                return

            # Scarica PDF Compratore
            try:
                response_c = requests.get(
                    f"{self.base_url}/api/conferme-ordine/{self.selected_conferma_id}/stampa-compratore",
                    stream=True
                )

                if response_c.status_code == 200:
                    # Estrai nome file dall'header Content-Disposition se disponibile
                    filename_c = f"Conferma_Compratore_{num_conf}.pdf"
                    if 'content-disposition' in response_c.headers:
                        import re
                        cd = response_c.headers['content-disposition']
                        filename_match = re.findall('filename=(.+)', cd)
                        if filename_match:
                            filename_c = filename_match[0].strip('"')

                    filepath_c = os.path.join(download_folder, filename_c)
                    with open(filepath_c, 'wb') as f:
                        for chunk in response_c.iter_content(chunk_size=8192):
                            f.write(chunk)

                    print(f"✓ PDF Compratore salvato: {filepath_c}")
                else:
                    messagebox.showerror("Errore", f"Errore nel generare PDF Compratore: {response_c.status_code}")
                    return

            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvare PDF Compratore:\n{str(e)}")
                return

            # Mostra messaggio di successo con opzione per aprire la cartella
            result = messagebox.askyesno(
                "Stampa Completata",
                f"Conferme d'ordine generate con successo!\n\n"
                f"📄 PDF Venditore: {filename_v}\n"
                f"📄 PDF Compratore: {filename_c}\n\n"
                f"📂 Salvati in:\n{download_folder}\n\n"
                f"Conferma N°: {num_conf}\n"
                f"Venditore: {conferma_display.get('venditore', 'N/A')}\n"
                f"Compratore: {conferma_display.get('compratore', 'N/A')}\n\n"
                f"Vuoi aprire la cartella di destinazione?"
            )

            # Se l'utente vuole aprire la cartella
            if result:
                import subprocess
                import platform

                try:
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', download_folder])
                    elif platform.system() == 'Windows':  # Windows
                        os.startfile(download_folder)
                    else:  # Linux
                        subprocess.run(['xdg-open', download_folder])
                except Exception as e:
                    messagebox.showerror("Errore", f"Impossibile aprire la cartella:\n{str(e)}")

            # Opzionale: apri i PDF con il visualizzatore predefinito
            # NOTA: Commentato per evitare warning su alcuni sistemi Linux
            # I PDF vengono comunque salvati correttamente nella cartella Download
            # import subprocess
            # import platform

            # try:
            #     if platform.system() == 'Darwin':  # macOS
            #         subprocess.run(['open', filepath_v])
            #         subprocess.run(['open', filepath_c])
            #     elif platform.system() == 'Windows':  # Windows
            #         os.startfile(filepath_v)
            #         os.startfile(filepath_c)
            #     else:  # Linux
            #         subprocess.run(['xdg-open', filepath_v])
            #         subprocess.run(['xdg-open', filepath_c])
            # except:
            #     # Se non riesce ad aprire i file, non è un problema critico
            #     pass

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
