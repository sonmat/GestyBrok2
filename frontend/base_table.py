"""
Classe base per tabelle con ordinamento e filtro
Da salvare in frontend/base_table.py
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable, Optional


class SortableTable(ttk.Frame):
    """Tabella riutilizzabile con ordinamento e filtro"""
    
    def __init__(self, parent, columns: List[tuple], height: int = 10):
        """
        columns: lista di tuple (id_colonna, label, width, anchor)
        esempio: [("id", "ID", 50, tk.CENTER), ("nome", "Nome", 200, tk.W)]
        """
        super().__init__(parent)
        self.columns = columns
        self.data = []
        self.sort_column = None
        self.sort_reverse = False
        
        self.setup_ui(height)
    
    def setup_ui(self, height):
        """Setup tabella"""
        # Frame per tree e scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Estrai ID colonne
        col_ids = [c[0] for c in self.columns]
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=col_ids,
            show="tree headings",
            height=height,
            selectmode="browse"
        )
        
        # Scrollbar verticale
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Scrollbar orizzontale
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscrollcommand=hsb.set)
        
        # Configura colonne
        self.tree.column("#0", width=0, stretch=tk.NO)
        
        for col_id, label, width, anchor in self.columns:
            self.tree.column(col_id, width=width, anchor=anchor)
            self.tree.heading(
                col_id,
                text=label,
                command=lambda c=col_id: self.sort_by(c)
            )
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tag per righe alternate
        self.tree.tag_configure("oddrow", background="#f0f0f0")
        self.tree.tag_configure("evenrow", background="white")
    
    def populate(self, data: List[Dict]):
        """Popola tabella con dati"""
        self.data = data
        self._refresh_display()
    
    def _refresh_display(self):
        """Aggiorna visualizzazione tabella"""
        # Pulisci
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Inserisci dati
        for idx, row in enumerate(self.data):
            values = [row.get(col[0], "") for col in self.columns]
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=values, tags=(tag,))
    
    def sort_by(self, col_id):
        """Ordina per colonna"""
        # Alterna direzione se stessa colonna
        if self.sort_column == col_id:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col_id
            self.sort_reverse = False
        
        # Ordina dati
        try:
            self.data.sort(
                key=lambda x: self._sort_key(x.get(col_id, "")),
                reverse=self.sort_reverse
            )
            self._refresh_display()
            
            # Aggiorna intestazioni con frecce
            for col in self.columns:
                label = col[1]
                if col[0] == col_id:
                    label += " ↓" if self.sort_reverse else " ↑"
                self.tree.heading(col[0], text=label)
        except:
            pass
    
    def _sort_key(self, value):
        """Chiave ordinamento - gestisce numeri e stringhe"""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            # Prova a convertire in numero
            try:
                return float(value.replace(',', '.').replace('€', '').strip())
            except:
                return value.lower()
        return str(value)
    
    def filter(self, search_term: str, search_columns: List[str] = None):
        """Filtra dati"""
        if not search_term:
            self._refresh_display()
            return
        
        search_term = search_term.lower()
        
        # Se non specificate, cerca in tutte le colonne
        if not search_columns:
            search_columns = [c[0] for c in self.columns]
        
        filtered = [
            row for row in self.data
            if any(
                search_term in str(row.get(col, "")).lower()
                for col in search_columns
            )
        ]
        
        # Salva dati originali, mostra filtrati
        original_data = self.data
        self.data = filtered
        self._refresh_display()
        self.data = original_data
    
    def get_selection(self) -> Optional[Dict]:
        """Ottieni riga selezionata"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        values = self.tree.item(selection[0])["values"]
        if not values:
            return None
        
        # Costruisci dizionario
        result = {}
        for idx, col in enumerate(self.columns):
            result[col[0]] = values[idx]
        return result
    
    def bind_selection(self, callback: Callable):
        """Bind evento selezione"""
        self.tree.bind("<<TreeviewSelect>>", callback)
    
    def bind_double_click(self, callback: Callable):
        """Bind doppio click"""
        self.tree.bind("<Double-1>", callback)