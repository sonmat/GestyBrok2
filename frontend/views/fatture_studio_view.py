"""
Vista per gestione Fatture Studio
Con tabella master-detail per i dettagli fattura
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict
from datetime import datetime
from widgets import AutocompleteCombobox


class FattureStudioView(ttk.Frame):
    """Vista fatture studio con pattern master-detail"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_id: Optional[int] = None

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup interfaccia master-detail"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Nuova Fattura", command=self.nuova_fattura).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Aggiorna", command=self.load_data).pack(side=tk.LEFT, padx=2)

        # PanedWindow per divisione verticale
        paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame superiore: Fatture Studio (Master)
        top_frame = ttk.LabelFrame(paned, text="Fatture Studio", padding=10)
        paned.add(top_frame, weight=2)

        # Tabella fatture studio
        columns_master = ("id", "n_fat", "data_fat", "cliente", "iva", "pagamento", "banca", "note")
        self.tree_master = ttk.Treeview(top_frame, columns=columns_master, show="tree headings", height=12)

        self.tree_master.column("#0", width=0, stretch=tk.NO)
        self.tree_master.heading("id", text="ID")
        self.tree_master.column("id", width=50, anchor=tk.CENTER)
        self.tree_master.heading("n_fat", text="N. Fattura")
        self.tree_master.column("n_fat", width=100)
        self.tree_master.heading("data_fat", text="Data")
        self.tree_master.column("data_fat", width=100)
        self.tree_master.heading("cliente", text="Cliente")
        self.tree_master.column("cliente", width=200)
        self.tree_master.heading("iva", text="IVA")
        self.tree_master.column("iva", width=100)
        self.tree_master.heading("pagamento", text="Pagamento")
        self.tree_master.column("pagamento", width=120)
        self.tree_master.heading("banca", text="Banca")
        self.tree_master.column("banca", width=150)
        self.tree_master.heading("note", text="Note")
        self.tree_master.column("note", width=150)

        # Scrollbar
        vsb_master = ttk.Scrollbar(top_frame, orient="vertical", command=self.tree_master.yview)
        self.tree_master.configure(yscrollcommand=vsb_master.set)

        self.tree_master.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb_master.pack(side=tk.RIGHT, fill=tk.Y)

        # Info totale record
        self.info_master_label = ttk.Label(top_frame, text="Totale fatture: 0", font=("Arial", 10, "italic"))
        self.info_master_label.pack(pady=5)

        self.tree_master.bind("<<TreeviewSelect>>", self.on_master_select)

        # Frame inferiore: Dettagli Fattura (Detail)
        bottom_frame = ttk.LabelFrame(paned, text="Dettagli Fattura", padding=10)
        paned.add(bottom_frame, weight=1)

        # Toolbar dettagli
        toolbar_det = ttk.Frame(bottom_frame)
        toolbar_det.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(toolbar_det, text="Aggiungi Dettaglio", command=self.aggiungi_dettaglio).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_det, text="Elimina", command=self.elimina_dettaglio).pack(side=tk.LEFT, padx=2)

        # Tabella dettagli
        columns_detail = ("id", "compratore", "qta", "prezzo", "provvigione", "tipologia", "data_consegna")
        self.tree_detail = ttk.Treeview(bottom_frame, columns=columns_detail, show="tree headings", height=8)

        self.tree_detail.column("#0", width=0, stretch=tk.NO)
        self.tree_detail.heading("id", text="ID")
        self.tree_detail.column("id", width=50, anchor=tk.CENTER)
        self.tree_detail.heading("compratore", text="Compratore")
        self.tree_detail.column("compratore", width=200)
        self.tree_detail.heading("qta", text="Quantità")
        self.tree_detail.column("qta", width=100)
        self.tree_detail.heading("prezzo", text="Prezzo")
        self.tree_detail.column("prezzo", width=100)
        self.tree_detail.heading("provvigione", text="Provvigione")
        self.tree_detail.column("provvigione", width=100)
        self.tree_detail.heading("tipologia", text="Tipologia")
        self.tree_detail.column("tipologia", width=120)
        self.tree_detail.heading("data_consegna", text="Data Consegna")
        self.tree_detail.column("data_consegna", width=120)

        vsb_detail = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.tree_detail.yview)
        self.tree_detail.configure(yscrollcommand=vsb_detail.set)

        self.tree_detail.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb_detail.pack(side=tk.RIGHT, fill=tk.Y)

        # Info totale record dettagli
        self.info_detail_label = ttk.Label(bottom_frame, text="Totale dettagli: 0", font=("Arial", 10, "italic"))
        self.info_detail_label.pack(pady=5)

    def load_data(self):
        """Carica fatture studio"""
        try:
            response = self.api_client.get("/api/fatture-studio")
            self.fatture = response if isinstance(response, list) else []
            self.populate_master()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare fatture:\n{str(e)}")
            self.fatture = []

    def populate_master(self):
        """Popola tabella master"""
        for item in self.tree_master.get_children():
            self.tree_master.delete(item)

        for fatt in self.fatture:
            values = (
                fatt.get("id_fatt_studio", ""),
                fatt.get("n_fat", ""),
                fatt.get("data_fat", ""),
                self.get_cliente_name(fatt.get("cliente")),
                self.get_iva_desc(fatt.get("t_iva")),
                self.get_pagamento_desc(fatt.get("t_pagamento")),
                self.get_banca_name(fatt.get("id_banca")),
                fatt.get("note", "")
            )
            self.tree_master.insert("", tk.END, values=values)

        # Aggiorna contatore
        self.info_master_label.config(text=f"Totale fatture: {len(self.fatture)}")

    def get_cliente_name(self, cliente_id):
        """Ottieni nome cliente (venditore)"""
        if not cliente_id:
            return ""
        try:
            venditore = self.api_client.get(f"/api/venditori/{cliente_id}")
            return venditore.get("azienda", f"ID: {cliente_id}")
        except:
            return f"ID: {cliente_id}"

    def get_iva_desc(self, iva_id):
        """Ottieni descrizione IVA"""
        if not iva_id:
            return ""
        try:
            iva = self.api_client.get(f"/api/iva/{iva_id}")
            return f"{iva.get('descrizione', '')} ({iva.get('iva', '')}%)"
        except:
            return f"ID: {iva_id}"

    def get_pagamento_desc(self, pag_id):
        """Ottieni tipo pagamento"""
        if not pag_id:
            return ""
        try:
            pag = self.api_client.get(f"/api/pagamenti/{pag_id}")
            return pag.get("tipo_pagamento", f"ID: {pag_id}")
        except:
            return f"ID: {pag_id}"

    def get_banca_name(self, banca_id):
        """Ottieni nome banca"""
        if not banca_id:
            return ""
        try:
            banca = self.api_client.get(f"/api/banche/{banca_id}")
            return banca.get("nome_banca", f"ID: {banca_id}")
        except:
            return f"ID: {banca_id}"

    def on_master_select(self, event):
        """Gestisce selezione master - aggiorna detail"""
        selection = self.tree_master.selection()
        if not selection:
            return

        values = self.tree_master.item(selection[0])["values"]
        if values:
            self.selected_id = values[0]
            self.load_details()

    def load_details(self):
        """Carica dettagli per fattura selezionata"""
        # Pulisci tabella
        for item in self.tree_detail.get_children():
            self.tree_detail.delete(item)

        if not self.selected_id:
            self.info_detail_label.config(text="Totale dettagli: 0")
            return

        try:
            print(f"DEBUG FRONTEND: Caricamento dettagli per fattura {self.selected_id}")
            dettagli = self.api_client.get(f"/api/fatture-studio/{self.selected_id}/dettagli")
            print(f"DEBUG FRONTEND: Ricevuti {len(dettagli)} dettagli")
            print(f"DEBUG FRONTEND: Dettagli = {dettagli}")

            for det in dettagli:
                # Usa compratore_nome se disponibile, altrimenti fallback
                compratore_display = det.get("compratore_nome", "") or self.get_compratore_name(det.get("compratore"))

                values = (
                    det.get("id_fat_studio_det", ""),
                    compratore_display,
                    det.get("qta", ""),
                    det.get("prezzo", ""),
                    det.get("provvigione", ""),
                    det.get("tipologia", ""),
                    det.get("data_consegna", "")
                )
                print(f"DEBUG FRONTEND: Inserisco riga: {values}")
                self.tree_detail.insert("", tk.END, values=values)

            # Aggiorna contatore
            self.info_detail_label.config(text=f"Totale dettagli: {len(dettagli)}")
            print(f"DEBUG FRONTEND: Dettagli caricati con successo")
        except Exception as e:
            print(f"ERRORE caricamento dettagli: {e}")
            import traceback
            traceback.print_exc()
            self.info_detail_label.config(text="Totale dettagli: 0")

    def get_compratore_name(self, compratore_id):
        """Ottieni nome compratore"""
        if not compratore_id:
            return ""
        try:
            compratore = self.api_client.get(f"/api/compratori/{compratore_id}")
            return compratore.get("azienda", f"ID: {compratore_id}")
        except:
            return f"ID: {compratore_id}"

    def nuova_fattura(self):
        """Nuova fattura studio"""
        FatturaStudioDialog(self, self.api_client, callback=self.load_data)

    def aggiungi_dettaglio(self):
        """Aggiungi dettaglio a fattura"""
        if not self.selected_id:
            messagebox.showwarning("Attenzione", "Seleziona una fattura")
            return
        DettaglioFatturaDialog(self, self.api_client, self.selected_id, callback=self.load_details)

    def elimina_dettaglio(self):
        """Elimina dettaglio selezionato"""
        selection = self.tree_detail.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un dettaglio da eliminare")
            return

        det_id = self.tree_detail.item(selection[0])["values"][0]

        if messagebox.askyesno("Conferma", "Eliminare questo dettaglio?"):
            try:
                self.api_client.delete(f"/api/fatture-studio/dettagli/{det_id}")
                self.load_details()
            except Exception as e:
                messagebox.showerror("Errore", str(e))


class FatturaStudioDialog(tk.Toplevel):
    """Dialog per creare fattura studio"""

    def __init__(self, parent, api_client, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.callback = callback

        self.title("Nuova Fattura Studio")
        self.geometry("600x500")

        self.setup_ui()

    def setup_ui(self):
        """Setup form"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Carica dati per combobox
        try:
            venditori = self.api_client.get_venditori()
            self.venditori_dict = {v['azienda']: v['id'] for v in venditori}

            iva_list = self.api_client.get("/api/iva")
            self.iva_dict = {f"{i['descrizione']} ({i['iva']}%)": i['id_iva'] for i in iva_list}

            pag_list = self.api_client.get("/api/pagamenti")
            self.pag_dict = {p['tipo_pagamento']: p['id_pagamento'] for p in pag_list}

            banche_list = self.api_client.get("/api/banche")
            self.banche_dict = {b['nome_banca']: b['id_banca'] for b in banche_list}
        except Exception as e:
            print(f"Errore caricamento dati: {e}")
            self.venditori_dict = {}
            self.iva_dict = {}
            self.pag_dict = {}
            self.banche_dict = {}

        row = 0

        # Numero fattura
        ttk.Label(main_frame, text="N. Fattura:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.n_fat_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.n_fat_var, width=30).grid(row=row, column=1, pady=5)
        row += 1

        # Data fattura
        ttk.Label(main_frame, text="Data Fattura:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.data_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        ttk.Entry(main_frame, textvariable=self.data_var, width=15).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="(gg/mm/aaaa)", foreground="gray").grid(row=row, column=2, sticky=tk.W, padx=5)
        row += 1

        # Nota accredito
        ttk.Label(main_frame, text="Nota Accredito:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.nota_acr_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.nota_acr_var, width=30).grid(row=row, column=1, pady=5)
        row += 1

        # Cliente (venditore)
        ttk.Label(main_frame, text="Cliente:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cliente_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.cliente_var,
                           values=list(self.venditori_dict.keys()), width=40).grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        # IVA
        ttk.Label(main_frame, text="IVA:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.iva_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.iva_var,
                           values=list(self.iva_dict.keys()), width=40).grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        # Pagamento
        ttk.Label(main_frame, text="Tipo Pagamento:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.pag_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.pag_var,
                           values=list(self.pag_dict.keys()), width=40).grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        # Banca
        ttk.Label(main_frame, text="Banca:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.banca_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.banca_var,
                           values=list(self.banche_dict.keys()), width=40).grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        # Note
        ttk.Label(main_frame, text="Note:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.note_text = tk.Text(main_frame, width=40, height=4)
        self.note_text.grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        # Bottoni
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)

        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def salva(self):
        """Salva fattura studio"""
        # Validazione
        if not self.n_fat_var.get():
            messagebox.showwarning("Attenzione", "Numero fattura obbligatorio")
            return
        if not self.cliente_var.get():
            messagebox.showwarning("Attenzione", "Seleziona un cliente")
            return
        if not self.iva_var.get():
            messagebox.showwarning("Attenzione", "Seleziona IVA")
            return
        if not self.pag_var.get():
            messagebox.showwarning("Attenzione", "Seleziona tipo pagamento")
            return

        # Recupera ID
        cliente_id = self.venditori_dict.get(self.cliente_var.get())
        iva_id = self.iva_dict.get(self.iva_var.get())
        pag_id = self.pag_dict.get(self.pag_var.get())
        banca_id = self.banche_dict.get(self.banca_var.get()) if self.banca_var.get() else None

        if not all([cliente_id, iva_id, pag_id]):
            messagebox.showerror("Errore", "Seleziona valori validi dalle liste")
            return

        data = {
            "n_fat": int(self.n_fat_var.get()),
            "data_fat": self.data_var.get(),
            "nota_acr": int(self.nota_acr_var.get()) if self.nota_acr_var.get() else None,
            "cliente": cliente_id,
            "t_iva": iva_id,
            "t_pagamento": pag_id,
            "note": self.note_text.get("1.0", tk.END).strip() or None,
            "id_banca": banca_id
        }

        try:
            self.api_client.post("/api/fatture-studio", data=data)
            messagebox.showinfo("Successo", "Fattura studio creata")
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", str(e))


class DettaglioFatturaDialog(tk.Toplevel):
    """Dialog per aggiungere dettaglio fattura"""

    def __init__(self, parent, api_client, fattura_id, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.fattura_id = fattura_id
        self.callback = callback

        self.title("Nuovo Dettaglio Fattura")
        self.geometry("500x450")

        self.setup_ui()

    def setup_ui(self):
        """Setup form"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Carica compratori
        try:
            compratori = self.api_client.get_compratori()
            self.compratori_dict = {c['azienda']: c['id'] for c in compratori}
        except:
            self.compratori_dict = {}

        row = 0

        # Compratore
        ttk.Label(main_frame, text="Compratore:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.comp_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.comp_var,
                           values=list(self.compratori_dict.keys()), width=40).grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        # Quantità
        ttk.Label(main_frame, text="Quantità:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.qta_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.qta_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Prezzo
        ttk.Label(main_frame, text="Prezzo:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.prezzo_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.prezzo_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Provvigione
        ttk.Label(main_frame, text="Provvigione:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.prov_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.prov_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Tipologia
        ttk.Label(main_frame, text="Tipologia:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tipo_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.tipo_var, width=30).grid(row=row, column=1, pady=5)
        row += 1

        # Data consegna
        ttk.Label(main_frame, text="Data Consegna:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.data_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.data_var, width=15).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="(gg/mm/aaaa)", foreground="gray").grid(row=row, column=2, sticky=tk.W, padx=5)
        row += 1

        # Bottoni
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)

        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def salva(self):
        """Salva dettaglio fattura"""
        # Validazione
        if not self.comp_var.get():
            messagebox.showwarning("Attenzione", "Seleziona un compratore")
            return
        if not self.qta_var.get() or not self.prezzo_var.get():
            messagebox.showwarning("Attenzione", "Quantità e Prezzo sono obbligatori")
            return

        compratore_id = self.compratori_dict.get(self.comp_var.get())
        if not compratore_id:
            messagebox.showerror("Errore", "Seleziona un compratore valido")
            return

        data = {
            "id_fat_studio": self.fattura_id,
            "compratore": compratore_id,
            "qta": int(self.qta_var.get()),
            "prezzo": float(self.prezzo_var.get()),
            "provvigione": float(self.prov_var.get()) if self.prov_var.get() else None,
            "tipologia": self.tipo_var.get() or None,
            "data_consegna": self.data_var.get() or None
        }

        try:
            self.api_client.post("/api/fatture-studio/dettagli", data=data)
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", str(e))
