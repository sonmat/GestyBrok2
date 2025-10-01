"""
Viste per IVA, Pagamenti, Banche
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class IvaView(ttk.Frame):
    """Vista gestione IVA"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_id = None
        self.iva_data = []
        self.sort_column = None
        self.sort_reverse = False

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup UI"""
        # Toolbar
        toolbar = ttk.Frame(self, padding=10)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="Nuova IVA", command=self.nuova).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Elimina", command=self.elimina).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Aggiorna", command=self.load_data).pack(side=tk.LEFT, padx=5)

        # Tabella
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("id", "descrizione", "percentuale")
        self.tree = ttk.Treeview(frame, columns=columns, show="tree headings")

        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("descrizione", width=300)
        self.tree.column("percentuale", width=100, anchor=tk.CENTER)

        self.tree.heading("id", text="ID", command=lambda: self.sort_by("id"))
        self.tree.heading("descrizione", text="Descrizione", command=lambda: self.sort_by("descrizione"))
        self.tree.heading("percentuale", text="Percentuale %", command=lambda: self.sort_by("percentuale"))

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def load_data(self):
        """Carica dati"""
        try:
            self.iva_data = self.api_client.get("/api/iva")
            self.populate_table(self.iva_data)
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def populate_table(self, data):
        """Popola tabella"""
        self.tree.delete(*self.tree.get_children())

        for iva in data:
            self.tree.insert("", tk.END, values=(
                iva.get("id", ""),
                iva.get("descrizione", ""),
                iva.get("iva", "")
            ))

    def sort_by(self, col):
        """Ordina per colonna"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        col_map = {"id": "id", "descrizione": "descrizione", "percentuale": "iva"}
        sort_key = col_map.get(col, col)

        try:
            sorted_data = sorted(
                self.iva_data,
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_reverse
            )
            self.populate_table(sorted_data)

            # Aggiorna intestazione con freccia
            for c in ["id", "descrizione", "percentuale"]:
                text = {"id": "ID", "descrizione": "Descrizione", "percentuale": "Percentuale %"}[c]
                if c == col:
                    text += " ↓" if self.sort_reverse else " ↑"
                self.tree.heading(c, text=text)
        except:
            pass

    def _sort_key(self, value):
        """Chiave ordinamento"""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                return float(value.replace(',', '.').replace('%', '').strip())
            except:
                return value.lower()
        return str(value)
    
    def nuova(self):
        """Nuova IVA"""
        dialog = IvaDialog(self, self.api_client, callback=self.load_data)
    
    def elimina(self):
        """Elimina IVA"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attenzione", "Seleziona un'IVA")
            return
        
        iva_id = self.tree.item(sel[0])["values"][0]
        
        if messagebox.askyesno("Conferma", "Eliminare questa IVA?"):
            try:
                self.api_client.delete(f"/api/iva/{iva_id}")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))


class IvaDialog(tk.Toplevel):
    """Dialog IVA"""
    
    def __init__(self, parent, api_client, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.callback = callback
        
        self.title("Nuova IVA")
        self.geometry("400x200")
        
        main = ttk.Frame(self, padding=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main, text="Descrizione:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.desc_var, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(main, text="Percentuale:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.perc_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.perc_var, width=30).grid(row=1, column=1, pady=5)
        
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def salva(self):
        """Salva"""
        data = {
            "descrizione": self.desc_var.get(),
            "iva": self.perc_var.get()
        }
        
        try:
            self.api_client.post("/api/iva", data=data)
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", str(e))


class PagamentiView(ttk.Frame):
    """Vista gestione Pagamenti"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.pagamenti_data = []
        self.sort_column = None
        self.sort_reverse = False

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup UI"""
        toolbar = ttk.Frame(self, padding=10)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="Nuovo Pagamento", command=self.nuovo).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Elimina", command=self.elimina).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Aggiorna", command=self.load_data).pack(side=tk.LEFT, padx=5)

        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("id", "tipo")
        self.tree = ttk.Treeview(frame, columns=columns, show="tree headings")

        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("id", width=100, anchor=tk.CENTER)
        self.tree.column("tipo", width=400)

        self.tree.heading("id", text="ID", command=lambda: self.sort_by("id"))
        self.tree.heading("tipo", text="Tipo Pagamento", command=lambda: self.sort_by("tipo"))

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def load_data(self):
        """Carica dati"""
        try:
            self.pagamenti_data = self.api_client.get("/api/pagamenti")
            self.populate_table(self.pagamenti_data)
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def populate_table(self, data):
        """Popola tabella"""
        self.tree.delete(*self.tree.get_children())

        for p in data:
            self.tree.insert("", tk.END, values=(
                p.get("id", ""),
                p.get("tipo", "")
            ))

    def sort_by(self, col):
        """Ordina per colonna"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        col_map = {"id": "id", "tipo": "tipo"}
        sort_key = col_map.get(col, col)

        try:
            sorted_data = sorted(
                self.pagamenti_data,
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_reverse
            )
            self.populate_table(sorted_data)

            # Aggiorna intestazione con freccia
            for c in ["id", "tipo"]:
                text = {"id": "ID", "tipo": "Tipo Pagamento"}[c]
                if c == col:
                    text += " ↓" if self.sort_reverse else " ↑"
                self.tree.heading(c, text=text)
        except:
            pass

    def _sort_key(self, value):
        """Chiave ordinamento"""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            return value.lower()
        return str(value)
    
    def nuovo(self):
        """Nuovo pagamento"""
        tipo = simpledialog.askstring("Nuovo Pagamento", "Tipo di pagamento:")
        if tipo:
            try:
                self.api_client.post("/api/pagamenti", data={"tipo_pagamento": tipo})
                self.load_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))
    
    def elimina(self):
        """Elimina pagamento"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attenzione", "Seleziona un pagamento")
            return
        
        pag_id = self.tree.item(sel[0])["values"][0]
        
        if messagebox.askyesno("Conferma", "Eliminare?"):
            try:
                self.api_client.delete(f"/api/pagamenti/{pag_id}")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))


class BancheView(ttk.Frame):
    """Vista gestione Banche"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.banche_data = []
        self.sort_column = None
        self.sort_reverse = False

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup UI"""
        toolbar = ttk.Frame(self, padding=10)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="Nuova Banca", command=self.nuova).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Elimina", command=self.elimina).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Aggiorna", command=self.load_data).pack(side=tk.LEFT, padx=5)

        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("id", "nome", "iban", "bic")
        self.tree = ttk.Treeview(frame, columns=columns, show="tree headings")

        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("nome", width=250)
        self.tree.column("iban", width=250)
        self.tree.column("bic", width=150)

        for col in columns:
            self.tree.heading(col, text=col.upper(), command=lambda c=col: self.sort_by(c))

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def load_data(self):
        """Carica dati"""
        try:
            self.banche_data = self.api_client.get("/api/banche")
            self.populate_table(self.banche_data)
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def populate_table(self, data):
        """Popola tabella"""
        self.tree.delete(*self.tree.get_children())

        for b in data:
            self.tree.insert("", tk.END, values=(
                b.get("id", ""),
                b.get("nome", ""),
                b.get("iban", ""),
                b.get("bic", "")
            ))

    def sort_by(self, col):
        """Ordina per colonna"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        col_map = {"id": "id", "nome": "nome", "iban": "iban", "bic": "bic"}
        sort_key = col_map.get(col, col)

        try:
            sorted_data = sorted(
                self.banche_data,
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_reverse
            )
            self.populate_table(sorted_data)

            # Aggiorna intestazione con freccia
            for c in ["id", "nome", "iban", "bic"]:
                text = c.upper()
                if c == col:
                    text += " ↓" if self.sort_reverse else " ↑"
                self.tree.heading(c, text=text)
        except:
            pass

    def _sort_key(self, value):
        """Chiave ordinamento"""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            return value.lower()
        return str(value)
    
    def nuova(self):
        """Nuova banca"""
        BancaDialog(self, self.api_client, callback=self.load_data)
    
    def elimina(self):
        """Elimina banca"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attenzione", "Seleziona una banca")
            return
        
        banca_id = self.tree.item(sel[0])["values"][0]
        
        if messagebox.askyesno("Conferma", "Eliminare?"):
            try:
                self.api_client.delete(f"/api/banche/{banca_id}")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))


class BancaDialog(tk.Toplevel):
    """Dialog Banca"""
    
    def __init__(self, parent, api_client, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.callback = callback
        
        self.title("Nuova Banca")
        self.geometry("400x250")
        
        main = ttk.Frame(self, padding=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        fields = [("nome", "Nome Banca:"), ("iban", "IBAN:"), ("bic", "BIC/SWIFT:")]
        self.vars = {}
        
        for i, (key, label) in enumerate(fields):
            ttk.Label(main, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            self.vars[key] = tk.StringVar()
            ttk.Entry(main, textvariable=self.vars[key], width=30).grid(row=i, column=1, pady=5)
        
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def salva(self):
        """Salva"""
        data = {
            "nome_banca": self.vars["nome"].get(),
            "iban": self.vars["iban"].get(),
            "bic": self.vars["bic"].get()
        }
        
        try:
            self.api_client.post("/api/banche", data=data)
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", str(e))