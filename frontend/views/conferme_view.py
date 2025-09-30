"""
Vista per gestione Conferme Ordine
Con tabella master-detail per date consegna e fatture
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict


class ConfermeOrdineView(ttk.Frame):
    """Vista conferme ordine con pattern master-detail"""
    
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
        
        ttk.Button(toolbar, text="Nuova Conferma", command=self.nuova).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Aggiorna", command=self.load_data).pack(side=tk.LEFT, padx=2)
        
        # PanedWindow per divisione verticale
        paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame superiore: Conferme ordine (Master)
        top_frame = ttk.LabelFrame(paned, text="Conferme Ordine", padding=10)
        paned.add(top_frame, weight=2)
        
        # Tabella conferme
        columns_master = ("id", "numero", "data", "venditore", "compratore", "articolo", "qta", "prezzo")
        self.tree_master = ttk.Treeview(top_frame, columns=columns_master, show="tree headings", height=10)
        
        self.tree_master.column("#0", width=0, stretch=tk.NO)
        for col in columns_master:
            self.tree_master.heading(col, text=col.capitalize())
            self.tree_master.column(col, width=100)
        
        # Scrollbar
        vsb_master = ttk.Scrollbar(top_frame, orient="vertical", command=self.tree_master.yview)
        self.tree_master.configure(yscrollcommand=vsb_master.set)
        
        self.tree_master.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb_master.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_master.bind("<<TreeviewSelect>>", self.on_master_select)
        
        # Frame inferiore: Date consegna e Fatture (Detail)
        bottom_frame = ttk.Frame(paned)
        paned.add(bottom_frame, weight=1)
        
        # PanedWindow orizzontale per dettagli
        detail_paned = ttk.PanedWindow(bottom_frame, orient=tk.HORIZONTAL)
        detail_paned.pack(fill=tk.BOTH, expand=True)
        
        # Date consegna
        date_frame = ttk.LabelFrame(detail_paned, text="Date Consegna", padding=5)
        detail_paned.add(date_frame, weight=1)
        
        columns_date = ("id", "data_consegna", "quantita")
        self.tree_date = ttk.Treeview(date_frame, columns=columns_date, show="tree headings", height=8)
        
        self.tree_date.column("#0", width=0, stretch=tk.NO)
        for col in columns_date:
            self.tree_date.heading(col, text=col.replace("_", " ").capitalize())
            self.tree_date.column(col, width=100)
        
        self.tree_date.pack(fill=tk.BOTH, expand=True)
        
        # Fatture
        fatt_frame = ttk.LabelFrame(detail_paned, text="Fatture Associate", padding=5)
        detail_paned.add(fatt_frame, weight=1)
        
        columns_fatt = ("id", "numero", "data", "importo", "pagata")
        self.tree_fatt = ttk.Treeview(fatt_frame, columns=columns_fatt, show="tree headings", height=8)
        
        self.tree_fatt.column("#0", width=0, stretch=tk.NO)
        for col in columns_fatt:
            self.tree_fatt.heading(col, text=col.capitalize())
            self.tree_fatt.column(col, width=100)
        
        self.tree_fatt.pack(fill=tk.BOTH, expand=True)
    
    def load_data(self):
        """Carica conferme ordine"""
        try:
            self.conferme = self.api_client.get_conferme_ordine()
            self.populate_master()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare:\n{str(e)}")
    
    def populate_master(self):
        """Popola tabella master"""
        for item in self.tree_master.get_children():
            self.tree_master.delete(item)
        
        for conf in self.conferme:
            values = (
                conf.get("id"),
                conf.get("numero_conferma", ""),
                conf.get("data_conferma", ""),
                f"ID: {conf.get('venditore_id', '')}",
                f"ID: {conf.get('compratore_id', '')}",
                f"ID: {conf.get('articolo_id', '')}",
                conf.get("quantita", ""),
                conf.get("prezzo", "")
            )
            self.tree_master.insert("", tk.END, values=values)
    
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
        """Carica dettagli per conferma selezionata"""
        # In una implementazione completa, qui faresti chiamate API separate
        # per caricare date_consegna e fatture filtrate per conferma_id
        
        # Per ora mostra placeholder
        for item in self.tree_date.get_children():
            self.tree_date.delete(item)
        
        for item in self.tree_fatt.get_children():
            self.tree_fatt.delete(item)
        
        # Esempio dati mock
        self.tree_date.insert("", tk.END, values=(1, "2024-01-15", "100 kg"))
        self.tree_fatt.insert("", tk.END, values=(1, "F/001/2024", "2024-01-31", "€1,000", "No"))
    
    def nuova(self):
        """Nuova conferma ordine"""
        messagebox.showinfo("Info", "Dialog per nuova conferma da implementare")
