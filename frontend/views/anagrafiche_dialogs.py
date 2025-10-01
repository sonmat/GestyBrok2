"""
Dialog per gestione Anagrafiche (Venditori, Compratori e relativi Dati)
Con autocompletamento per combobox
"""
import tkinter as tk
from tkinter import ttk, messagebox
from widgets import AutocompleteCombobox


# ==================== VENDITORI ====================

class VenditoreDialog(tk.Toplevel):
    """Dialog per creare/modificare venditore"""

    def __init__(self, parent, api_client, venditore_id=None, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.venditore_id = venditore_id
        self.callback = callback
        self.result = None

        self.title("Modifica Venditore" if venditore_id else "Nuovo Venditore")
        self.geometry("600x650")

        self.setup_ui()

        if venditore_id:
            self.load_venditore()

    def setup_ui(self):
        """Setup form"""
        # Crea scrollable frame
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        main_frame = ttk.Frame(scrollable_frame, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Carica dati per combobox
        try:
            iva_list = self.api_client.get("/api/iva")
            self.iva_dict = {f"{i.get('descrizione', '')} ({i.get('iva', '')}%)": i.get('id') for i in iva_list}

            pag_list = self.api_client.get("/api/pagamenti")
            self.pag_dict = {p.get('tipo', ''): p.get('id') for p in pag_list}
        except:
            self.iva_dict = {}
            self.pag_dict = {}

        self.vars = {}
        row = 0

        # Azienda *
        ttk.Label(main_frame, text="Azienda:*").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["azienda"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["azienda"], width=50).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Indirizzo
        ttk.Label(main_frame, text="Indirizzo:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["indirizzo"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["indirizzo"], width=50).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # CAP
        ttk.Label(main_frame, text="CAP:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["cap"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["cap"], width=20).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Città
        ttk.Label(main_frame, text="Città:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["citta"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["citta"], width=50).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Stato
        ttk.Label(main_frame, text="Stato:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["stato"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["stato"], width=50).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Telefono
        ttk.Label(main_frame, text="Telefono:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["telefono"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["telefono"], width=30).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Fax
        ttk.Label(main_frame, text="Fax:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["fax"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["fax"], width=30).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # P.IVA
        ttk.Label(main_frame, text="P.IVA:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["piva"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["piva"], width=30).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Italiano
        ttk.Label(main_frame, text="Italiano:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["italiano"] = tk.StringVar(value="Si")
        italiano_combo = ttk.Combobox(main_frame, textvariable=self.vars["italiano"], values=["Si", "No"], width=15, state="readonly")
        italiano_combo.grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Tipo Pagamento (combobox con autocompletamento)
        ttk.Label(main_frame, text="Tipo Pagamento:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.tipo_pag_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.tipo_pag_var, values=list(self.pag_dict.keys()), width=47).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # IVA (combobox con autocompletamento)
        ttk.Label(main_frame, text="IVA:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.iva_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.iva_var, values=list(self.iva_dict.keys()), width=47).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Pulsanti
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def load_venditore(self):
        """Carica dati venditore per modifica"""
        try:
            response = self.api_client.get(f"/api/venditori/{self.venditore_id}")
            v = response

            self.vars["azienda"].set(v.get("azienda", ""))
            self.vars["indirizzo"].set(v.get("indirizzo", ""))
            self.vars["cap"].set(v.get("cap", ""))
            self.vars["citta"].set(v.get("citta", ""))
            self.vars["stato"].set(v.get("stato", ""))
            self.vars["telefono"].set(v.get("telefono", ""))
            self.vars["fax"].set(v.get("fax", ""))
            self.vars["piva"].set(v.get("partita_iva", ""))
            self.vars["italiano"].set("Si" if v.get("italiano") else "No")

            # TODO: caricare tipo_pagamento e iva se presenti
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare il venditore: {str(e)}")
            self.destroy()

    def salva(self):
        """Salva venditore"""
        if not self.vars["azienda"].get():
            messagebox.showwarning("Attenzione", "Il campo Azienda è obbligatorio")
            return

        data = {
            "azienda": self.vars["azienda"].get(),
            "indirizzo": self.vars["indirizzo"].get() or None,
            "cap": self.vars["cap"].get() or None,
            "citta": self.vars["citta"].get() or None,
            "stato": self.vars["stato"].get() or None,
            "telefono": self.vars["telefono"].get() or None,
            "fax": self.vars["fax"].get() or None,
            "piva": self.vars["piva"].get() or None,
            "italiano": self.vars["italiano"].get(),
            "tipo_pagamento": self.tipo_pag_var.get() or None,
            "iva": self.iva_var.get() or None
        }

        try:
            if self.venditore_id:
                response = self.api_client.put(f"/api/venditori/{self.venditore_id}", data=data)
                messagebox.showinfo("Successo", "Venditore aggiornato")
            else:
                response = self.api_client.post("/api/venditori", data=data)
                messagebox.showinfo("Successo", "Venditore creato")

            self.result = response
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il salvataggio: {str(e)}")


class DatiVenditoreDialog(tk.Toplevel):
    """Dialog per creare/modificare dati contatto venditore"""

    def __init__(self, parent, api_client, venditore_id, dato_id=None, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.venditore_id = venditore_id
        self.dato_id = dato_id
        self.callback = callback
        self.result = None

        self.title("Modifica Dato Venditore" if dato_id else "Nuovo Dato Venditore")
        self.geometry("500x350")

        self.setup_ui()

        if dato_id:
            self.load_dato()

    def setup_ui(self):
        """Setup form"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.vars = {}
        row = 0

        # Mail
        ttk.Label(main_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars["mail"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["mail"], width=40).grid(row=row, column=1, pady=5)
        row += 1

        # Fax
        ttk.Label(main_frame, text="Fax:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars["fax"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["fax"], width=40).grid(row=row, column=1, pady=5)
        row += 1

        # Telefono
        ttk.Label(main_frame, text="Telefono:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars["telefono"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["telefono"], width=40).grid(row=row, column=1, pady=5)
        row += 1

        # Tipologia telefono
        ttk.Label(main_frame, text="Tipologia Tel:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars["ntel_tipologia"] = tk.StringVar()
        tipo_combo = ttk.Combobox(main_frame, textvariable=self.vars["ntel_tipologia"],
                                  values=["Fisso", "Mobile", "Ufficio", "Altro"], width=37)
        tipo_combo.grid(row=row, column=1, pady=5)
        row += 1

        # Contatto
        ttk.Label(main_frame, text="Contatto:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars["contatto"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["contatto"], width=40).grid(row=row, column=1, pady=5)
        row += 1

        # Pulsanti
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def load_dato(self):
        """Carica dati per modifica"""
        try:
            response = self.api_client.get(f"/api/dati-venditori/{self.dato_id}")
            d = response

            self.vars["mail"].set(d.get("mail", ""))
            self.vars["fax"].set(d.get("fax", ""))
            self.vars["telefono"].set(d.get("telefono", ""))
            self.vars["ntel_tipologia"].set(d.get("ntel_tipologia", ""))
            self.vars["contatto"].set(d.get("contatto", ""))
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare il dato: {str(e)}")
            self.destroy()

    def salva(self):
        """Salva dato venditore"""
        data = {
            "id_venditore": self.venditore_id,
            "mail": self.vars["mail"].get() or None,
            "fax": self.vars["fax"].get() or None,
            "telefono": self.vars["telefono"].get() or None,
            "ntel_tipologia": self.vars["ntel_tipologia"].get() or None,
            "contatto": self.vars["contatto"].get() or None
        }

        try:
            if self.dato_id:
                response = self.api_client.put(f"/api/dati-venditori/{self.dato_id}", data=data)
                messagebox.showinfo("Successo", "Dato aggiornato")
            else:
                response = self.api_client.post("/api/dati-venditori", data=data)
                messagebox.showinfo("Successo", "Dato creato")

            self.result = response
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il salvataggio: {str(e)}")


# ==================== COMPRATORI ====================

class CompratoreDialog(tk.Toplevel):
    """Dialog per creare/modificare compratore"""

    def __init__(self, parent, api_client, compratore_id=None, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.compratore_id = compratore_id
        self.callback = callback
        self.result = None

        self.title("Modifica Compratore" if compratore_id else "Nuovo Compratore")
        self.geometry("600x650")

        self.setup_ui()

        if compratore_id:
            self.load_compratore()

    def setup_ui(self):
        """Setup form"""
        # Crea scrollable frame
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        main_frame = ttk.Frame(scrollable_frame, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Carica dati per combobox
        try:
            iva_list = self.api_client.get("/api/iva")
            self.iva_dict = {f"{i.get('descrizione', '')} ({i.get('iva', '')}%)": i.get('id') for i in iva_list}

            pag_list = self.api_client.get("/api/pagamenti")
            self.pag_dict = {p.get('tipo', ''): p.get('id') for p in pag_list}
        except:
            self.iva_dict = {}
            self.pag_dict = {}

        self.vars = {}
        row = 0

        # Azienda *
        ttk.Label(main_frame, text="Azienda:*").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["azienda"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["azienda"], width=50).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Indirizzo
        ttk.Label(main_frame, text="Indirizzo:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["indirizzo"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["indirizzo"], width=50).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # CAP
        ttk.Label(main_frame, text="CAP:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["cap"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["cap"], width=20).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Città
        ttk.Label(main_frame, text="Città:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["citta"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["citta"], width=50).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Stato
        ttk.Label(main_frame, text="Stato:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["stato"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["stato"], width=50).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Telefono
        ttk.Label(main_frame, text="Telefono:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["telefono"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["telefono"], width=30).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Fax
        ttk.Label(main_frame, text="Fax:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["fax"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["fax"], width=30).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # P.IVA
        ttk.Label(main_frame, text="P.IVA:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["piva"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["piva"], width=30).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Italiano
        ttk.Label(main_frame, text="Italiano:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.vars["italiano"] = tk.StringVar(value="Si")
        italiano_combo = ttk.Combobox(main_frame, textvariable=self.vars["italiano"], values=["Si", "No"], width=15, state="readonly")
        italiano_combo.grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Tipo Pagamento (combobox con autocompletamento)
        ttk.Label(main_frame, text="Tipo Pagamento:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.tipo_pag_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.tipo_pag_var, values=list(self.pag_dict.keys()), width=47).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # IVA (combobox con autocompletamento)
        ttk.Label(main_frame, text="IVA:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.iva_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.iva_var, values=list(self.iva_dict.keys()), width=47).grid(row=row, column=1, pady=3, sticky=tk.W)
        row += 1

        # Pulsanti
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def load_compratore(self):
        """Carica dati compratore per modifica"""
        try:
            response = self.api_client.get(f"/api/compratori/{self.compratore_id}")
            c = response

            self.vars["azienda"].set(c.get("azienda", ""))
            self.vars["indirizzo"].set(c.get("indirizzo", ""))
            self.vars["cap"].set(c.get("cap", ""))
            self.vars["citta"].set(c.get("citta", ""))
            self.vars["stato"].set(c.get("stato", ""))
            self.vars["telefono"].set(c.get("telefono", ""))
            self.vars["fax"].set(c.get("fax", ""))
            self.vars["piva"].set(c.get("partita_iva", ""))
            self.vars["italiano"].set("Si" if c.get("italiano") else "No")

            # TODO: caricare tipo_pagamento e iva se presenti
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare il compratore: {str(e)}")
            self.destroy()

    def salva(self):
        """Salva compratore"""
        if not self.vars["azienda"].get():
            messagebox.showwarning("Attenzione", "Il campo Azienda è obbligatorio")
            return

        data = {
            "azienda": self.vars["azienda"].get(),
            "indirizzo": self.vars["indirizzo"].get() or None,
            "cap": self.vars["cap"].get() or None,
            "citta": self.vars["citta"].get() or None,
            "stato": self.vars["stato"].get() or None,
            "telefono": self.vars["telefono"].get() or None,
            "fax": self.vars["fax"].get() or None,
            "piva": self.vars["piva"].get() or None,
            "italiano": self.vars["italiano"].get(),
            "tipo_pagamento": self.tipo_pag_var.get() or None,
            "iva": self.iva_var.get() or None
        }

        try:
            if self.compratore_id:
                response = self.api_client.put(f"/api/compratori/{self.compratore_id}", data=data)
                messagebox.showinfo("Successo", "Compratore aggiornato")
            else:
                response = self.api_client.post("/api/compratori", data=data)
                messagebox.showinfo("Successo", "Compratore creato")

            self.result = response
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il salvataggio: {str(e)}")


class DatiCompratoreDialog(tk.Toplevel):
    """Dialog per creare/modificare dati contatto compratore"""

    def __init__(self, parent, api_client, compratore_id, dato_id=None, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.compratore_id = compratore_id
        self.dato_id = dato_id
        self.callback = callback
        self.result = None

        self.title("Modifica Dato Compratore" if dato_id else "Nuovo Dato Compratore")
        self.geometry("500x350")

        self.setup_ui()

        if dato_id:
            self.load_dato()

    def setup_ui(self):
        """Setup form"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.vars = {}
        row = 0

        # Mail
        ttk.Label(main_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars["mail"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["mail"], width=40).grid(row=row, column=1, pady=5)
        row += 1

        # Fax
        ttk.Label(main_frame, text="Fax:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars["fax"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["fax"], width=40).grid(row=row, column=1, pady=5)
        row += 1

        # Telefono
        ttk.Label(main_frame, text="Telefono:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars["telefono"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["telefono"], width=40).grid(row=row, column=1, pady=5)
        row += 1

        # Tipologia telefono
        ttk.Label(main_frame, text="Tipologia Tel:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars["ntel_tipologia"] = tk.StringVar()
        tipo_combo = ttk.Combobox(main_frame, textvariable=self.vars["ntel_tipologia"],
                                  values=["Fisso", "Mobile", "Ufficio", "Altro"], width=37)
        tipo_combo.grid(row=row, column=1, pady=5)
        row += 1

        # Contatto
        ttk.Label(main_frame, text="Contatto:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars["contatto"] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vars["contatto"], width=40).grid(row=row, column=1, pady=5)
        row += 1

        # Pulsanti
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def load_dato(self):
        """Carica dati per modifica"""
        try:
            response = self.api_client.get(f"/api/dati-compratori/{self.dato_id}")
            d = response

            self.vars["mail"].set(d.get("mail", ""))
            self.vars["fax"].set(d.get("fax", ""))
            self.vars["telefono"].set(d.get("telefono", ""))
            self.vars["ntel_tipologia"].set(d.get("ntel_tipologia", ""))
            self.vars["contatto"].set(d.get("contatto", ""))
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare il dato: {str(e)}")
            self.destroy()

    def salva(self):
        """Salva dato compratore"""
        data = {
            "id_compratore": self.compratore_id,
            "mail": self.vars["mail"].get() or None,
            "fax": self.vars["fax"].get() or None,
            "telefono": self.vars["telefono"].get() or None,
            "ntel_tipologia": self.vars["ntel_tipologia"].get() or None,
            "contatto": self.vars["contatto"].get() or None
        }

        try:
            if self.dato_id:
                response = self.api_client.put(f"/api/dati-compratori/{self.dato_id}", data=data)
                messagebox.showinfo("Successo", "Dato aggiornato")
            else:
                response = self.api_client.post("/api/dati-compratori", data=data)
                messagebox.showinfo("Successo", "Dato creato")

            self.result = response
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il salvataggio: {str(e)}")
