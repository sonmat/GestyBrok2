"""
Dialog per Fatture Studio e Dettagli
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Optional, Dict, Any
from api_client import APIClient
from widgets import AutocompleteCombobox


class FatturaStudioDialog(tk.Toplevel):
    """Dialog per aggiungere/modificare una fattura studio"""

    def __init__(self, parent, api_client: APIClient, fattura_id: Optional[int] = None):
        super().__init__(parent)
        self.api_client = api_client
        self.fattura_id = fattura_id
        self.result = None

        self.title("Modifica Fattura Studio" if fattura_id else "Nuova Fattura Studio")
        self.geometry("700x600")
        self.resizable(False, False)

        # Modal
        self.transient(parent)

        self.create_widgets()

        if fattura_id:
            self.load_data()

        # Centro finestra
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        # Grab dopo che la finestra è visibile
        self.grab_set()

    def create_widgets(self):
        """Crea i widget del dialog"""
        # Container principale con scrollbar
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas e scrollbar
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Campi del form
        self.fields = {}
        row = 0

        # N° Fattura
        ttk.Label(scrollable_frame, text="N° Fattura:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['n_fat'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['n_fat'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Data Fattura
        ttk.Label(scrollable_frame, text="Data Fattura:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['data_fat'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['data_fat'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        ttk.Label(scrollable_frame, text="(formato: YYYY-MM-DD)", font=("", 8), foreground="gray").grid(row=row, column=2, sticky="w", padx=5)
        row += 1

        # Nota/Accredito
        ttk.Label(scrollable_frame, text="Nota/Accredito:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['nota_acr'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['nota_acr'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Cliente (Venditore) * (Foreign Key - AutocompleteCombobox)
        ttk.Label(scrollable_frame, text="Cliente (Venditore) *:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['cliente'] = AutocompleteCombobox(scrollable_frame, width=38)
        self.fields['cliente'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        self.load_venditori()
        row += 1

        # IVA (Foreign Key - AutocompleteCombobox)
        ttk.Label(scrollable_frame, text="IVA:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['t_iva'] = AutocompleteCombobox(scrollable_frame, width=38)
        self.fields['t_iva'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        self.load_iva()
        row += 1

        # Tipo Pagamento (Foreign Key - AutocompleteCombobox)
        ttk.Label(scrollable_frame, text="Tipo Pagamento:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['t_pagamento'] = AutocompleteCombobox(scrollable_frame, width=38)
        self.fields['t_pagamento'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        self.load_pagamenti()
        row += 1

        # Banca (Foreign Key - AutocompleteCombobox)
        ttk.Label(scrollable_frame, text="Banca:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['id_banca'] = AutocompleteCombobox(scrollable_frame, width=38)
        self.fields['id_banca'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        self.load_banche()
        row += 1

        # Note (Text area)
        ttk.Label(scrollable_frame, text="Note:").grid(row=row, column=0, sticky="nw", pady=5, padx=5)
        self.fields['note'] = tk.Text(scrollable_frame, width=40, height=4)
        self.fields['note'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        scrollable_frame.columnconfigure(1, weight=1)

        # Bottoni
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Salva", command=self.save).pack(side=tk.RIGHT)

    def load_venditori(self):
        """Carica venditori per la combobox"""
        try:
            response = self.api_client.get("/api/venditori")
            if response:
                items = [(v['id'], v['azienda']) for v in response]
                self.fields['cliente'].set_completion_list(items)
        except Exception as e:
            print(f"Errore caricamento venditori: {e}")

    def load_iva(self):
        """Carica tipi IVA per la combobox"""
        try:
            response = self.api_client.get("/api/iva")
            if response:
                items = [(i['id_iva'], i['descrizione']) for i in response]
                self.fields['t_iva'].set_completion_list(items)
        except Exception as e:
            print(f"Errore caricamento IVA: {e}")

    def load_pagamenti(self):
        """Carica tipi pagamento per la combobox"""
        try:
            response = self.api_client.get("/api/pagamenti")
            if response:
                items = [(p['id_pagamento'], p['tipo_pagamento']) for p in response]
                self.fields['t_pagamento'].set_completion_list(items)
        except Exception as e:
            print(f"Errore caricamento pagamenti: {e}")

    def load_banche(self):
        """Carica banche per la combobox"""
        try:
            response = self.api_client.get("/api/banche")
            if response:
                items = [(b['id_banca'], b['nome_banca']) for b in response]
                self.fields['id_banca'].set_completion_list(items)
        except Exception as e:
            print(f"Errore caricamento banche: {e}")

    def load_data(self):
        """Carica dati esistenti"""
        try:
            response = self.api_client.get(f"/api/fatture-studio/{self.fattura_id}")
            if response:
                self.fields['n_fat'].insert(0, str(response.get('n_fat', '')))
                self.fields['data_fat'].insert(0, str(response.get('data_fat', '')))
                self.fields['nota_acr'].insert(0, str(response.get('nota_acr', '')))

                # Imposta combobox con ID
                if response.get('cliente'):
                    self.fields['cliente'].set_by_id(response['cliente'])
                if response.get('t_iva'):
                    self.fields['t_iva'].set_by_id(response['t_iva'])
                if response.get('t_pagamento'):
                    self.fields['t_pagamento'].set_by_id(response['t_pagamento'])
                if response.get('id_banca'):
                    self.fields['id_banca'].set_by_id(response['id_banca'])

                self.fields['note'].insert("1.0", str(response.get('note', '')))
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento dati: {e}")

    def save(self):
        """Salva i dati"""
        # Validazione
        cliente_id = self.fields['cliente'].get_selected_id()
        if not cliente_id:
            messagebox.showwarning("Attenzione", "Il cliente è obbligatorio")
            return

        # Prepara dati
        data = {
            'n_fat': self.fields['n_fat'].get().strip() or None,
            'data_fat': self.fields['data_fat'].get().strip() or None,
            'nota_acr': self.fields['nota_acr'].get().strip() or None,
            'cliente': cliente_id,
            't_iva': self.fields['t_iva'].get_selected_id(),
            't_pagamento': self.fields['t_pagamento'].get_selected_id(),
            'id_banca': self.fields['id_banca'].get_selected_id(),
            'note': self.fields['note'].get("1.0", "end-1c").strip() or None,
        }

        try:
            if self.fattura_id:
                # Update
                self.api_client.put(f"/api/fatture-studio/{self.fattura_id}", data)
            else:
                # Create
                response = self.api_client.post("/api/fatture-studio", data)
                self.result = response

            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio: {e}")


class DettaglioFatturaStudioDialog(tk.Toplevel):
    """Dialog per aggiungere/modificare un dettaglio fattura studio"""

    def __init__(self, parent, api_client: APIClient, id_fat_studio: int, dettaglio_id: Optional[int] = None):
        super().__init__(parent)
        self.api_client = api_client
        self.id_fat_studio = id_fat_studio
        self.dettaglio_id = dettaglio_id
        self.result = None

        self.title("Modifica Dettaglio" if dettaglio_id else "Nuovo Dettaglio")
        self.geometry("600x450")
        self.resizable(False, False)

        # Modal
        self.transient(parent)

        self.create_widgets()

        if dettaglio_id:
            self.load_data()

        # Centro finestra
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        # Grab dopo che la finestra è visibile
        self.grab_set()

    def create_widgets(self):
        """Crea i widget del dialog"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        self.fields = {}
        row = 0

        # Compratore * (Foreign Key - AutocompleteCombobox)
        ttk.Label(frame, text="Compratore *:").grid(row=row, column=0, sticky="w", pady=10, padx=5)
        self.fields['compratore'] = AutocompleteCombobox(frame, width=38)
        self.fields['compratore'].grid(row=row, column=1, sticky="ew", pady=10, padx=5)
        self.load_compratori()
        row += 1

        # Quantità
        ttk.Label(frame, text="Quantità:").grid(row=row, column=0, sticky="w", pady=10, padx=5)
        self.fields['qta'] = ttk.Entry(frame, width=40)
        self.fields['qta'].grid(row=row, column=1, sticky="ew", pady=10, padx=5)
        row += 1

        # Prezzo
        ttk.Label(frame, text="Prezzo:").grid(row=row, column=0, sticky="w", pady=10, padx=5)
        self.fields['prezzo'] = ttk.Entry(frame, width=40)
        self.fields['prezzo'].grid(row=row, column=1, sticky="ew", pady=10, padx=5)
        row += 1

        # Provvigione
        ttk.Label(frame, text="Provvigione:").grid(row=row, column=0, sticky="w", pady=10, padx=5)
        self.fields['provvigione'] = ttk.Entry(frame, width=40)
        self.fields['provvigione'].grid(row=row, column=1, sticky="ew", pady=10, padx=5)
        row += 1

        # Tipologia
        ttk.Label(frame, text="Tipologia:").grid(row=row, column=0, sticky="w", pady=10, padx=5)
        self.fields['tipologia'] = ttk.Entry(frame, width=40)
        self.fields['tipologia'].grid(row=row, column=1, sticky="ew", pady=10, padx=5)
        row += 1

        # Data Consegna
        ttk.Label(frame, text="Data Consegna:").grid(row=row, column=0, sticky="w", pady=10, padx=5)
        self.fields['data_consegna'] = ttk.Entry(frame, width=40)
        self.fields['data_consegna'].grid(row=row, column=1, sticky="ew", pady=10, padx=5)
        ttk.Label(frame, text="(formato: YYYY-MM-DD)", font=("", 8), foreground="gray").grid(row=row, column=2, sticky="w", padx=5)
        row += 1

        frame.columnconfigure(1, weight=1)

        # Bottoni
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Salva", command=self.save).pack(side=tk.RIGHT)

    def load_compratori(self):
        """Carica compratori per la combobox"""
        try:
            response = self.api_client.get("/api/compratori")
            if response:
                items = [(c['id'], c['azienda']) for c in response]
                self.fields['compratore'].set_completion_list(items)
        except Exception as e:
            print(f"Errore caricamento compratori: {e}")

    def load_data(self):
        """Carica dati esistenti"""
        try:
            response = self.api_client.get(f"/api/fatture-studio/{self.id_fat_studio}/dettagli")
            if response:
                # Trova il record specifico
                dettaglio_record = next((d for d in response if d.get('id_fat_studio_det') == self.dettaglio_id), None)
                if dettaglio_record:
                    if dettaglio_record.get('compratore'):
                        self.fields['compratore'].set_by_id(dettaglio_record['compratore'])
                    self.fields['qta'].insert(0, str(dettaglio_record.get('qta', '')))
                    self.fields['prezzo'].insert(0, str(dettaglio_record.get('prezzo', '')))
                    self.fields['provvigione'].insert(0, str(dettaglio_record.get('provvigione', '')))
                    self.fields['tipologia'].insert(0, str(dettaglio_record.get('tipologia', '')))
                    self.fields['data_consegna'].insert(0, str(dettaglio_record.get('data_consegna', '')))
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento dati: {e}")

    def save(self):
        """Salva i dati"""
        # Validazione
        compratore_id = self.fields['compratore'].get_selected_id()
        if not compratore_id:
            messagebox.showwarning("Attenzione", "Il compratore è obbligatorio")
            return

        # Prepara dati
        data = {
            'id_fat_studio': self.id_fat_studio,
            'compratore': compratore_id,
            'qta': self.fields['qta'].get().strip() or None,
            'prezzo': self.fields['prezzo'].get().strip() or None,
            'provvigione': self.fields['provvigione'].get().strip() or None,
            'tipologia': self.fields['tipologia'].get().strip() or None,
            'data_consegna': self.fields['data_consegna'].get().strip() or None,
        }

        try:
            if self.dettaglio_id:
                # Update
                self.api_client.put(f"/api/fatture-studio/dettagli/{self.dettaglio_id}", data)
            else:
                # Create
                response = self.api_client.post("/api/fatture-studio/dettagli", data)
                self.result = response

            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio: {e}")
