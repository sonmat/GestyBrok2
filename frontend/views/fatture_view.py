"""
Vista per gestione Fatture
Con funzionalità generazione automatica
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict
from datetime import datetime


class FattureView(ttk.Frame):
    """Vista fatture con generazione automatica"""
    
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_id: Optional[int] = None
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup interfaccia"""
        # Toolbar con filtri
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            toolbar,
            text="⚙️ Genera Fatture",
            command=self.apri_dialog_genera
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar, text="Aggiorna", command=self.load_data).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Filtri data
        ttk.Label(toolbar, text="Da:").pack(side=tk.LEFT, padx=5)
        self.data_da_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.data_da_var, width=12).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(toolbar, text="A:").pack(side=tk.LEFT, padx=5)
        self.data_a_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.data_a_var, width=12).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar, text="Filtra", command=self.filtra_date).pack(side=tk.LEFT, padx=5)
        
        # Tabella fatture
        table_frame = ttk.LabelFrame(self, text="Fatture", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("id", "numero", "data", "cliente_id", "importo_tot", "pagata", "data_pag")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="tree headings")
        
        # Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Configurazione colonne
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("numero", width=150)
        self.tree.column("data", width=100, anchor=tk.CENTER)
        self.tree.column("cliente_id", width=100, anchor=tk.CENTER)
        self.tree.column("importo_tot", width=120, anchor=tk.E)
        self.tree.column("pagata", width=80, anchor=tk.E)
