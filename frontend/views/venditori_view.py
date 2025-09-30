"""
Vista per gestione Venditori
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict


class VenditoriView(ttk.Frame):
    """Vista per gestione venditori"""
    
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_id: Optional[int] = None
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Configura interfaccia"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Nuovo", command=self.nuovo).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Modifica", command=self.modifica).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Elimina", command=self.elimina).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Aggiorna", command=self.load_data).pack(side=tk.LEFT, padx=2)
        
        # Ricerca
        ttk.Label(toolbar, text="Cerca:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_data())
        ttk.Entry(toolbar, textvariable=self.search_var, width=30).pack(side=tk.LEFT)
        
        # Tabella
        table_frame = ttk.LabelFrame(self, text="Lista Venditori", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview
        columns = ("id", "codice", "azienda", "piva", "citta", "telefono", "italiano", "attivo")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="tree headings", selectmode="browse")
        
        # Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Configurazione colonne
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("codice", width=80)
        self.tree.column("azienda", width=250)
        self.tree.column("piva", width=120)
        self.tree.column("citta", width=150)
        self.tree.column("telefono", width=120)
        self.tree.column("italiano", width=70, anchor=tk.CENTER)
        self.tree.column("attivo", width=70, anchor=tk.CENTER)
        
        # Headers
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", lambda e: self.modifica())
        
        # Form dettaglio
        self.detail_frame = ttk.LabelFrame(self, text="Dettaglio Venditore", padding=10)
        self.detail_frame.pack(fill=tk.X, padx=5, pady=5)
        self.setup_form()
    
    def setup_form(self):
        """Setup form dettaglio"""
        form = ttk.Frame(self.detail_frame)
        form.pack(fill=tk.X)
        
        # Variabili
        self.form_vars = {
            "id": tk.StringVar(),
            "codice": tk.StringVar(),
            "azienda": tk.StringVar(),
            "partita_iva": tk.StringVar(),
            "indirizzo": tk.StringVar(),
            "cap": tk.StringVar(),
            "citta": tk.StringVar(),
            "telefono": tk.StringVar(),
            "email": tk.StringVar(),
            "italiano": tk.BooleanVar(value=True),
            "attivo": tk.BooleanVar(value=True)
        }
        
        # Layout form (2 colonne)
        row = 0
        ttk.Label(form, text="ID:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Entry(form, textvariable=self.form_vars["id"], state="readonly", width=10).grid(row=row, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(form, text="Codice:").grid(row=row, column=2, sticky=tk.W, padx=5, pady=3)
        ttk.Entry(form, textvariable=self.form_vars["codice"], width=20).grid(row=row, column=3, sticky=tk.W, padx=5, pady=3)
        
        row += 1
        ttk.Label(form, text="Azienda:*").grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Entry(form, textvariable=self.form_vars["azienda"], width=40).grid(row=row, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=3)
        
        row += 1
        ttk.Label(form, text="P.IVA:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Entry(form, textvariable=self.form_vars["partita_iva"], width=20).grid(row=row, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(form, text="Email:").grid(row=row, column=2, sticky=tk.W, padx=5, pady=3)
        ttk.Entry(form, textvariable=self.form_vars["email"], width=30).grid(row=row, column=3, sticky=tk.EW, padx=5, pady=3)
        
        row += 1
        ttk.Label(form, text="Indirizzo:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Entry(form, textvariable=self.form_vars["indirizzo"], width=40).grid(row=row, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=3)
        
        row += 1
        ttk.Label(form, text="CAP:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Entry(form, textvariable=self.form_vars["cap"], width=10).grid(row=row, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(form, text="Città:").grid(row=row, column=2, sticky=tk.W, padx=5, pady=3)
        ttk.Entry(form, textvariable=self.form_vars["citta"], width=25).grid(row=row, column=3, sticky=tk.EW, padx=5, pady=3)
        
        row += 1
        ttk.Label(form, text="Telefono:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Entry(form, textvariable=self.form_vars["telefono"], width=20).grid(row=row, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Checkbutton(form, text="Italiano", variable=self.form_vars["italiano"]).grid(row=row, column=2, sticky=tk.W, padx=5, pady=3)
        ttk.Checkbutton(form, text="Attivo", variable=self.form_vars["attivo"]).grid(row=row, column=3, sticky=tk.W, padx=5, pady=3)
        
        # Bottoni
        btn_frame = ttk.Frame(self.detail_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.annulla).pack(side=tk.LEFT, padx=5)
        
        self.set_form_state(False)
    
    def set_form_state(self, enabled: bool):
        """Abilita/disabilita form"""
        state = "normal" if enabled else "disabled"
        for widget in self.detail_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Entry, ttk.Checkbutton)) and child.cget("state") != "readonly":
                        child.config(state=state)
    
    def load_data(self):
        """Carica dati"""
        try:
            self.venditori = self.api_client.get_venditori()
            self.populate_table(self.venditori)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare i dati:\n{str(e)}")
    
    def populate_table(self, data: List[Dict]):
        """Popola tabella"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for idx, v in enumerate(data):
            values = (
                v.get("id", ""),
                v.get("codice", ""),
                v.get("azienda", ""),
                v.get("partita_iva", ""),
                v.get("citta", ""),
                v.get("telefono", ""),
                "Si" if v.get("italiano", False) else "No",
                "Si" if v.get("attivo", True) else "No"
            )
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=values, tags=(tag,))
        
        self.tree.tag_configure("oddrow", background="#f0f0f0")
        self.tree.tag_configure("evenrow", background="white")
    
    def filter_data(self):
        """Filtra dati"""
        search_term = self.search_var.get().lower()
        if not search_term:
            self.populate_table(self.venditori)
            return
        
        filtered = [
            v for v in self.venditori
            if search_term in v.get("azienda", "").lower()
            or search_term in v.get("codice", "").lower()
            or search_term in v.get("citta", "").lower()
        ]
        self.populate_table(filtered)
    
    def on_select(self, event):
        """Gestisce selezione"""
        selection = self.tree.selection()
        if not selection:
            return
        
        values = self.tree.item(selection[0])["values"]
        if values:
            self.selected_id = values[0]
            self.load_detail(self.selected_id)
    
    def load_detail(self, venditore_id: int):
        """Carica dettaglio"""
        venditore = next((v for v in self.venditori if v["id"] == venditore_id), None)
        if venditore:
            self.populate_form(venditore)
    
    def populate_form(self, data: Dict):
        """Popola form"""
        for key, var in self.form_vars.items():
            value = data.get(key, "")
            if isinstance(var, tk.BooleanVar):
                var.set(bool(value))
            else:
                var.set(value if value is not None else "")
    
    def clear_form(self):
        """Pulisce form"""
        for var in self.form_vars.values():
            if isinstance(var, tk.BooleanVar):
                var.set(True)
            else:
                var.set("")
    
    def nuovo(self):
        """Nuovo venditore"""
        self.selected_id = None
        self.clear_form()
        self.set_form_state(True)
    
    def modifica(self):
        """Modifica venditore"""
        if not self.selected_id:
            messagebox.showwarning("Attenzione", "Seleziona un venditore")
            return
        self.set_form_state(True)
    
    def salva(self):
        """Salva venditore"""
        if not self.form_vars["azienda"].get():
            messagebox.showwarning("Attenzione", "L'azienda è obbligatoria")
            return
        
        data = {
            "codice": self.form_vars["codice"].get() or None,
            "azienda": self.form_vars["azienda"].get(),
            "partita_iva": self.form_vars["partita_iva"].get() or None,
            "indirizzo": self.form_vars["indirizzo"].get() or None,
            "cap": self.form_vars["cap"].get() or None,
            "citta": self.form_vars["citta"].get() or None,
            "telefono": self.form_vars["telefono"].get() or None,
            "email": self.form_vars["email"].get() or None,
            "italiano": self.form_vars["italiano"].get(),
            "attivo": self.form_vars["attivo"].get()
        }
        
        try:
            if self.selected_id:
                self.api_client.update_venditore(self.selected_id, data)
                messagebox.showinfo("Successo", "Venditore aggiornato")
            else:
                self.api_client.create_venditore(data)
                messagebox.showinfo("Successo", "Venditore creato")
            
            self.load_data()
            self.set_form_state(False)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare:\n{str(e)}")
    
    def elimina(self):
        """Elimina venditore"""
        if not self.selected_id:
            messagebox.showwarning("Attenzione", "Seleziona un venditore")
            return
        
        if not messagebox.askyesno("Conferma", "Confermi l'eliminazione?"):
            return
        
        try:
            self.api_client.delete_venditore(self.selected_id)
            messagebox.showinfo("Successo", "Venditore eliminato")
            self.selected_id = None
            self.clear_form()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile eliminare:\n{str(e)}")
    
    def annulla(self):
        """Annulla modifica"""
        if self.selected_id:
            self.load_detail(self.selected_id)
        else:
            self.clear_form()
        self.set_form_state(False)
