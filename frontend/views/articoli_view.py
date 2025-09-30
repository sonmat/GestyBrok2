"""
Vista per gestione Articoli
Pattern MVC con separazione logica/presentazione
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict
from datetime import datetime


class ArticoliView(ttk.Frame):
    """Vista per gestione articoli"""
    
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_id: Optional[int] = None
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Configura interfaccia"""
        # Pannello principale diviso in 3 sezioni
        # Top: Toolbar
        # Center: Tabella
        # Bottom: Form dettaglio
        
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            toolbar,
            text="➕ Nuovo",
            command=self.nuovo_articolo
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar,
            text="✏️ Modifica",
            command=self.modifica_articolo
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar,
            text="🗑️ Elimina",
            command=self.elimina_articolo
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(
            toolbar,
            text="🔄 Aggiorna",
            command=self.load_data
        ).pack(side=tk.LEFT, padx=2)
        
        # Ricerca
        ttk.Label(toolbar, text="Cerca:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_data())
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=2)
        
        # Frame centrale per tabella
        table_frame = ttk.LabelFrame(self, text="Lista Articoli", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tabella con scrollbar
        self.setup_table(table_frame)
        
        # Frame dettaglio in basso
        self.detail_frame = ttk.LabelFrame(self, text="Dettaglio Articolo", padding=10)
        self.detail_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.setup_detail_form()
    
    def setup_table(self, parent):
        """Configura tabella articoli"""
        # Frame con scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar verticale
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Scrollbar orizzontale
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("id", "codice", "nome", "um", "tipo", "famiglia", "attivo")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse"
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configurazione colonne
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("codice", width=100, anchor=tk.W)
        self.tree.column("nome", width=300, anchor=tk.W)
        self.tree.column("um", width=80, anchor=tk.CENTER)
        self.tree.column("tipo", width=100, anchor=tk.W)
        self.tree.column("famiglia", width=100, anchor=tk.W)
        self.tree.column("attivo", width=60, anchor=tk.CENTER)
        
        # Headers
        self.tree.heading("id", text="ID", command=lambda: self.sort_by("id"))
        self.tree.heading("codice", text="Codice", command=lambda: self.sort_by("codice"))
        self.tree.heading("nome", text="Nome Articolo", command=lambda: self.sort_by("nome"))
        self.tree.heading("um", text="U.M.", command=lambda: self.sort_by("um"))
        self.tree.heading("tipo", text="Tipo", command=lambda: self.sort_by("tipo"))
        self.tree.heading("famiglia", text="Famiglia", command=lambda: self.sort_by("famiglia"))
        self.tree.heading("attivo", text="Attivo", command=lambda: self.sort_by("attivo"))
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Binding selezione
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Binding doppio click per modifica
        self.tree.bind("<Double-1>", lambda e: self.modifica_articolo())
        
        # Tag per riga alternata
        self.tree.tag_configure("oddrow", background="#f0f0f0")
        self.tree.tag_configure("evenrow", background="white")
        self.tree.tag_configure("inactive", foreground="gray")
    
    def setup_detail_form(self):
        """Form per dettagli articolo"""
        # Grid layout per form
        form_frame = ttk.Frame(self.detail_frame)
        form_frame.pack(fill=tk.X, expand=True)
        
        # Variabili
        self.form_vars = {
            "id": tk.StringVar(),
            "codice": tk.StringVar(),
            "nome": tk.StringVar(),
            "unita_misura": tk.StringVar(),
            "tipo_id": tk.StringVar(),
            "famiglia_id": tk.StringVar(),
            "descrizione": tk.StringVar(),
            "attivo": tk.BooleanVar(value=True)
        }
        
        # Row 0
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.form_vars["id"], state="readonly", width=10).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        ttk.Label(form_frame, text="Codice:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.form_vars["codice"], width=20).grid(
            row=0, column=3, sticky=tk.W, padx=5, pady=5
        )
        
        # Row 1
        ttk.Label(form_frame, text="Nome:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.form_vars["nome"], width=50).grid(
            row=1, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5
        )
        
        # Row 2
        ttk.Label(form_frame, text="U.M.:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.form_vars["unita_misura"], width=15).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        ttk.Checkbutton(
            form_frame,
            text="Attivo",
            variable=self.form_vars["attivo"]
        ).grid(row=2, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Row 3
        ttk.Label(form_frame, text="Descrizione:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=5)
        desc_text = tk.Text(form_frame, height=3, width=50)
        desc_text.grid(row=3, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.desc_text = desc_text
        
        # Bottoni salva/annulla
        btn_frame = ttk.Frame(self.detail_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="💾 Salva",
            command=self.salva_articolo
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="❌ Annulla",
            command=self.annulla_modifica
        ).pack(side=tk.LEFT, padx=5)
        
        # Disabilita form inizialmente
        self.set_form_state(False)
    
    def set_form_state(self, enabled: bool):
        """Abilita/disabilita form"""
        state = "normal" if enabled else "disabled"
        for widget in self.detail_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Entry, ttk.Checkbutton)):
                        child.config(state=state)
        self.desc_text.config(state=state)
    
    def load_data(self):
        """Carica dati da API"""
        try:
            self.articoli = self.api_client.get_articoli()
            self.populate_table(self.articoli)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare i dati:\n{str(e)}")
    
    def populate_table(self, data: List[Dict]):
        """Popola tabella con dati"""
        # Pulisci tabella
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Inserisci dati
        for idx, articolo in enumerate(data):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            if not articolo.get("attivo", True):
                tag = "inactive"
            
            values = (
                articolo.get("id", ""),
                articolo.get("codice", ""),
                articolo.get("nome", ""),
                articolo.get("unita_misura", ""),
                articolo.get("tipo_id", ""),
                articolo.get("famiglia_id", ""),
                "Sì" if articolo.get("attivo", True) else "No"
            )
            self.tree.insert("", tk.END, values=values, tags=(tag,))
    
    def filter_data(self):
        """Filtra dati in base a ricerca"""
        search_term = self.search_var.get().lower()
        if not search_term:
            self.populate_table(self.articoli)
            return
        
        filtered = [
            a for a in self.articoli
            if search_term in a.get("nome", "").lower()
            or search_term in a.get("codice", "").lower()
        ]
        self.populate_table(filtered)
    
    def sort_by(self, column: str):
        """Ordina tabella per colonna"""
        # TODO: Implementa ordinamento
        pass
    
    def on_select(self, event):
        """Gestisce selezione riga"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item["values"]
        
        if values:
            self.selected_id = values[0]
            self.load_detail(self.selected_id)
    
    def load_detail(self, articolo_id: int):
        """Carica dettaglio articolo"""
        try:
            articolo = self.api_client.get_articolo(articolo_id)
            self.populate_form(articolo)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare dettaglio:\n{str(e)}")
    
    def populate_form(self, data: Dict):
        """Popola form con dati"""
        self.form_vars["id"].set(data.get("id", ""))
        self.form_vars["codice"].set(data.get("codice", ""))
        self.form_vars["nome"].set(data.get("nome", ""))
        self.form_vars["unita_misura"].set(data.get("unita_misura", ""))
        self.form_vars["tipo_id"].set(data.get("tipo_id", ""))
        self.form_vars["famiglia_id"].set(data.get("famiglia_id", ""))
        self.form_vars["attivo"].set(data.get("attivo", True))
        
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", data.get("descrizione", ""))
    
    def clear_form(self):
        """Pulisce form"""
        for var in self.form_vars.values():
            if isinstance(var, tk.BooleanVar):
                var.set(True)
            else:
                var.set("")
        self.desc_text.delete("1.0", tk.END)
    
    def nuovo_articolo(self):
        """Prepara form per nuovo articolo"""
        self.selected_id = None
        self.clear_form()
        self.set_form_state(True)
    
    def modifica_articolo(self):
        """Abilita modifica articolo selezionato"""
        if not self.selected_id:
            messagebox.showwarning("Attenzione", "Seleziona un articolo da modificare")
            return
        self.set_form_state(True)
    
    def salva_articolo(self):
        """Salva articolo (crea o aggiorna)"""
        # Validazione
        if not self.form_vars["nome"].get():
            messagebox.showwarning("Attenzione", "Il nome è obbligatorio")
            return
        
        # Prepara dati
        data = {
            "nome": self.form_vars["nome"].get(),
            "codice": self.form_vars["codice"].get() or None,
            "unita_misura": self.form_vars["unita_misura"].get() or None,
            "tipo_id": int(self.form_vars["tipo_id"].get()) if self.form_vars["tipo_id"].get() else None,
            "famiglia_id": int(self.form_vars["famiglia_id"].get()) if self.form_vars["famiglia_id"].get() else None,
            "descrizione": self.desc_text.get("1.0", tk.END).strip() or None,
            "attivo": self.form_vars["attivo"].get()
        }
        
        try:
            if self.selected_id:
                # Update
                self.api_client.update_articolo(self.selected_id, data)
                messagebox.showinfo("Successo", "Articolo aggiornato con successo")
            else:
                # Create
                self.api_client.create_articolo(data)
                messagebox.showinfo("Successo", "Articolo creato con successo")
            
            self.load_data()
            self.set_form_state(False)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare:\n{str(e)}")
    
    def elimina_articolo(self):
        """Elimina articolo selezionato"""
        if not self.selected_id:
            messagebox.showwarning("Attenzione", "Seleziona un articolo da eliminare")
            return
        
        if not messagebox.askyesno("Conferma", "Sei sicuro di voler eliminare questo articolo?"):
            return
        
        try:
            self.api_client.delete_articolo(self.selected_id)
            messagebox.showinfo("Successo", "Articolo eliminato con successo")
            self.selected_id = None
            self.clear_form()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile eliminare:\n{str(e)}")
    
    def annulla_modifica(self):
        """Annulla modifica corrente"""
        if self.selected_id:
            self.load_detail(self.selected_id)
        else:
            self.clear_form()
        self.set_form_state(False)
