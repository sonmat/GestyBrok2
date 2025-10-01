"""
Dialog per Conferme d'Ordine e tabelle correlate
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Optional, Dict, Any
from api_client import APIClient
from widgets import AutocompleteCombobox


class ConfermaDialog(tk.Toplevel):
    """Dialog per aggiungere/modificare una conferma d'ordine"""

    def __init__(self, parent, api_client: APIClient, conferma_id: Optional[int] = None):
        super().__init__(parent)
        self.api_client = api_client
        self.conferma_id = conferma_id
        self.result = None

        self.title("Modifica Conferma" if conferma_id else "Nuova Conferma")
        self.geometry("700x800")
        self.resizable(False, False)

        # Modal
        self.transient(parent)

        self.create_widgets()

        if conferma_id:
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

        # N° Conferma *
        ttk.Label(scrollable_frame, text="N° Conferma *:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['n_conf'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['n_conf'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Data Conferma *
        ttk.Label(scrollable_frame, text="Data Conferma *:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['data_conf'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['data_conf'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        ttk.Label(scrollable_frame, text="(formato: YYYY-MM-DD)", font=("", 8), foreground="gray").grid(row=row, column=2, sticky="w", padx=5)
        row += 1

        # Compratore * (Foreign Key - AutocompleteCombobox)
        ttk.Label(scrollable_frame, text="Compratore *:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['compratore'] = AutocompleteCombobox(scrollable_frame, width=38)
        self.fields['compratore'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        self.load_compratori()
        row += 1

        # Venditore * (Foreign Key - AutocompleteCombobox)
        ttk.Label(scrollable_frame, text="Venditore *:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['venditore'] = AutocompleteCombobox(scrollable_frame, width=38)
        self.fields['venditore'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        self.load_venditori()
        row += 1

        # Articolo * (Foreign Key - AutocompleteCombobox)
        ttk.Label(scrollable_frame, text="Articolo *:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['articolo'] = AutocompleteCombobox(scrollable_frame, width=38)
        self.fields['articolo'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        self.load_articoli()
        row += 1

        # Quantità *
        ttk.Label(scrollable_frame, text="Quantità *:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['qta'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['qta'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Prezzo *
        ttk.Label(scrollable_frame, text="Prezzo *:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['prezzo'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['prezzo'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Provvigione
        ttk.Label(scrollable_frame, text="Provvigione:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['provvigione'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['provvigione'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Tipologia
        ttk.Label(scrollable_frame, text="Tipologia:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['tipologia'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['tipologia'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Luogo Consegna
        ttk.Label(scrollable_frame, text="Luogo Consegna:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['luogo_consegna'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['luogo_consegna'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Condizioni Pagamento
        ttk.Label(scrollable_frame, text="Condizioni Pagamento:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['condizioni_pag'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['condizioni_pag'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Carico
        ttk.Label(scrollable_frame, text="Carico:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['carico'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['carico'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Arrivo
        ttk.Label(scrollable_frame, text="Arrivo:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['arrivo'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['arrivo'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Email Venditore
        ttk.Label(scrollable_frame, text="Email Venditore:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['emailv'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['emailv'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # Email Compratore
        ttk.Label(scrollable_frame, text="Email Compratore:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['emailc'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['emailc'].grid(row=row, column=1, sticky="ew", pady=5, padx=5)
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

    def load_compratori(self):
        """Carica compratori per la combobox"""
        try:
            response = self.api_client.get("/api/compratori")
            if response:
                items = [(c['id'], c['azienda']) for c in response]
                self.fields['compratore'].set_completion_list(items)
        except Exception as e:
            print(f"Errore caricamento compratori: {e}")

    def load_venditori(self):
        """Carica venditori per la combobox"""
        try:
            response = self.api_client.get("/api/venditori")
            if response:
                items = [(v['id'], v['azienda']) for v in response]
                self.fields['venditore'].set_completion_list(items)
        except Exception as e:
            print(f"Errore caricamento venditori: {e}")

    def load_articoli(self):
        """Carica articoli per la combobox"""
        try:
            response = self.api_client.get("/api/articoli")
            if response:
                items = [(a['id'], a['nome']) for a in response]
                self.fields['articolo'].set_completion_list(items)
        except Exception as e:
            print(f"Errore caricamento articoli: {e}")

    def load_data(self):
        """Carica dati esistenti"""
        try:
            response = self.api_client.get(f"/api/conferme/{self.conferma_id}")
            if response:
                self.fields['n_conf'].insert(0, response.get('n_conf', ''))
                self.fields['data_conf'].insert(0, response.get('data_conf', ''))

                # Imposta combobox con ID
                if response.get('compratore'):
                    self.fields['compratore'].set_by_id(response['compratore'])
                if response.get('venditore'):
                    self.fields['venditore'].set_by_id(response['venditore'])
                if response.get('articolo'):
                    self.fields['articolo'].set_by_id(response['articolo'])

                self.fields['qta'].insert(0, response.get('qta', ''))
                self.fields['prezzo'].insert(0, response.get('prezzo', ''))
                self.fields['provvigione'].insert(0, response.get('provvigione', ''))
                self.fields['tipologia'].insert(0, response.get('tipologia', ''))
                self.fields['luogo_consegna'].insert(0, response.get('luogo_consegna', ''))
                self.fields['condizioni_pag'].insert(0, response.get('condizioni_pag', ''))
                self.fields['carico'].insert(0, response.get('carico', ''))
                self.fields['arrivo'].insert(0, response.get('arrivo', ''))
                self.fields['emailv'].insert(0, response.get('emailv', ''))
                self.fields['emailc'].insert(0, response.get('emailc', ''))
                self.fields['note'].insert("1.0", response.get('note', ''))
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento dati: {e}")

    def save(self):
        """Salva i dati"""
        # Validazione
        if not self.fields['n_conf'].get().strip():
            messagebox.showwarning("Attenzione", "Il numero conferma è obbligatorio")
            return
        if not self.fields['data_conf'].get().strip():
            messagebox.showwarning("Attenzione", "La data conferma è obbligatoria")
            return

        compratore_id = self.fields['compratore'].get_selected_id()
        if not compratore_id:
            messagebox.showwarning("Attenzione", "Il compratore è obbligatorio")
            return

        venditore_id = self.fields['venditore'].get_selected_id()
        if not venditore_id:
            messagebox.showwarning("Attenzione", "Il venditore è obbligatorio")
            return

        articolo_id = self.fields['articolo'].get_selected_id()
        if not articolo_id:
            messagebox.showwarning("Attenzione", "L'articolo è obbligatorio")
            return

        if not self.fields['qta'].get().strip():
            messagebox.showwarning("Attenzione", "La quantità è obbligatoria")
            return
        if not self.fields['prezzo'].get().strip():
            messagebox.showwarning("Attenzione", "Il prezzo è obbligatorio")
            return

        # Prepara dati
        data = {
            'n_conf': self.fields['n_conf'].get().strip(),
            'data_conf': self.fields['data_conf'].get().strip(),
            'compratore': compratore_id,
            'venditore': venditore_id,
            'articolo': articolo_id,
            'qta': self.fields['qta'].get().strip(),
            'prezzo': self.fields['prezzo'].get().strip(),
            'provvigione': self.fields['provvigione'].get().strip(),
            'tipologia': self.fields['tipologia'].get().strip(),
            'luogo_consegna': self.fields['luogo_consegna'].get().strip(),
            'condizioni_pag': self.fields['condizioni_pag'].get().strip(),
            'carico': self.fields['carico'].get().strip(),
            'arrivo': self.fields['arrivo'].get().strip(),
            'emailv': self.fields['emailv'].get().strip(),
            'emailc': self.fields['emailc'].get().strip(),
            'note': self.fields['note'].get("1.0", "end-1c").strip(),
        }

        try:
            if self.conferma_id:
                # Update
                self.api_client.put(f"/api/conferme/{self.conferma_id}", data)
            else:
                # Create
                response = self.api_client.post("/api/conferme", data)
                self.result = response

            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio: {e}")


class DataConsegnaDialog(tk.Toplevel):
    """Dialog per aggiungere/modificare una data di consegna"""

    def __init__(self, parent, api_client: APIClient, id_conferma: int, data_id: Optional[int] = None):
        super().__init__(parent)
        self.api_client = api_client
        self.id_conferma = id_conferma
        self.data_id = data_id
        self.result = None

        self.title("Modifica Data Consegna" if data_id else "Nuova Data Consegna")
        self.geometry("500x250")
        self.resizable(False, False)

        # Modal
        self.transient(parent)

        self.create_widgets()

        if data_id:
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

        # Data Consegna *
        ttk.Label(frame, text="Data Consegna *:").grid(row=row, column=0, sticky="w", pady=10, padx=5)
        self.fields['data_consegna'] = ttk.Entry(frame, width=30)
        self.fields['data_consegna'].grid(row=row, column=1, sticky="ew", pady=10, padx=5)
        ttk.Label(frame, text="(formato: YYYY-MM-DD)", font=("", 8), foreground="gray").grid(row=row, column=2, sticky="w", padx=5)
        row += 1

        # Quantità Consegna *
        ttk.Label(frame, text="Quantità Consegna *:").grid(row=row, column=0, sticky="w", pady=10, padx=5)
        self.fields['qta_consegna'] = ttk.Entry(frame, width=30)
        self.fields['qta_consegna'].grid(row=row, column=1, sticky="ew", pady=10, padx=5)
        row += 1

        frame.columnconfigure(1, weight=1)

        # Bottoni
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Salva", command=self.save).pack(side=tk.RIGHT)

    def load_data(self):
        """Carica dati esistenti"""
        try:
            response = self.api_client.get(f"/api/date-consegna?id_conferma={self.id_conferma}")
            if response:
                # Trova il record specifico
                data_record = next((d for d in response if d.get('id_data_consegna') == self.data_id), None)
                if data_record:
                    self.fields['data_consegna'].insert(0, data_record.get('data_consegna', ''))
                    self.fields['qta_consegna'].insert(0, data_record.get('qta_consegna', ''))
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento dati: {e}")

    def save(self):
        """Salva i dati"""
        # Validazione
        if not self.fields['data_consegna'].get().strip():
            messagebox.showwarning("Attenzione", "La data consegna è obbligatoria")
            return
        if not self.fields['qta_consegna'].get().strip():
            messagebox.showwarning("Attenzione", "La quantità consegna è obbligatoria")
            return

        # Prepara dati
        data = {
            'id_conferma': self.id_conferma,
            'data_consegna': self.fields['data_consegna'].get().strip(),
            'qta_consegna': self.fields['qta_consegna'].get().strip(),
        }

        try:
            if self.data_id:
                # Update
                self.api_client.put(f"/api/date-consegna/{self.data_id}", data)
            else:
                # Create
                response = self.api_client.post("/api/date-consegna", data)
                self.result = response

            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio: {e}")
