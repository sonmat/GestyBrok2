"""
Vista per gestione Compratori
Pattern simile a VenditoriView
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict


class CompratoriView(ttk.Frame):
    """Vista per gestione compratori - implementazione semplificata"""
    
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_id: Optional[int] = None
        
        # Label informativa
        info_label = ttk.Label(
            self,
            text="Vista Compratori - Implementazione simile a Venditori",
            font=("Arial", 12, "bold"),
            padding=20
        )
        info_label.pack()
        
        # Toolbar base
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Nuovo", command=self.nuovo).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Aggiorna", command=self.load_data).pack(side=tk.LEFT, padx=2)
        
        # Tabella
        columns = ("id", "azienda", "piva", "citta", "telefono")
        self.tree = ttk.Treeview(self, columns=columns, show="tree headings")
        
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=150)
        
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.load_data()
    
    def load_data(self):
        """Carica compratori"""
        try:
            self.compratori = self.api_client.get_compratori()
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for c in self.compratori:
                values = (
                    c.get("id"),
                    c.get("azienda"),
                    c.get("partita_iva", ""),
                    c.get("citta", ""),
                    c.get("telefono", "")
                )
                self.tree.insert("", tk.END, values=values)
        except Exception as e:
            messagebox.showerror("Errore", str(e))
    
    def nuovo(self):
        """Crea nuovo compratore"""
        messagebox.showinfo("Info", "Funzione da implementare")
