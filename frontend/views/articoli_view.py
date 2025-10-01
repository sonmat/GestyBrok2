"""
Vista Articoli COMPLETA con chi cerca e chi offre
"""
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from typing import Optional, List, Dict
from widgets import AutocompleteCombobox


class ArticoliView(ttk.Frame):
    """Vista articoli con tabelle chi cerca e chi offre"""
    
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_id: Optional[int] = None
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup interfaccia"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Nuovo", command=self.nuovo).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Modifica", command=self.modifica).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Elimina", command=self.elimina).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Aggiorna", command=self.load_data).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(toolbar, text="Gestisci Tipologie", command=self.apri_tipologie).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Gestisci Famiglie", command=self.apri_famiglie).pack(side=tk.LEFT, padx=2)
        
        # Ricerca
        ttk.Label(toolbar, text="Cerca:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_data())
        ttk.Entry(toolbar, textvariable=self.search_var, width=30).pack(side=tk.LEFT)
        
        # PanedWindow verticale: tabella articoli sopra, dettagli sotto
        paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame superiore: Tabella articoli
        top_frame = ttk.LabelFrame(paned, text="Lista Articoli", padding=5)
        paned.add(top_frame, weight=2)
        
        columns = ("id", "nome", "um", "tipo", "famiglia")
        self.tree = ttk.Treeview(top_frame, columns=columns, show="tree headings", height=10)
        
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("nome", width=300)
        self.tree.column("um", width=80, anchor=tk.CENTER)
        self.tree.column("tipo", width=150)
        self.tree.column("famiglia", width=150)
        
        # Headers con ordinamento
        self.sort_reverse = False
        self.sort_column = None
        
        for col in columns:
            self.tree.heading(col, text=col.upper(), command=lambda c=col: self.sort_by(c))
        
        vsb = ttk.Scrollbar(top_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Info totale record
        self.info_articoli_label = ttk.Label(top_frame, text="Totale articoli: 0", font=("Arial", 10, "italic"))
        self.info_articoli_label.pack(pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Frame inferiore: Chi offre + Chi cerca
        bottom_frame = ttk.Frame(paned)
        paned.add(bottom_frame, weight=1)
        
        # PanedWindow orizzontale
        detail_paned = ttk.PanedWindow(bottom_frame, orient=tk.HORIZONTAL)
        detail_paned.pack(fill=tk.BOTH, expand=True)
        
        # Chi offre (Venditori)
        offre_frame = ttk.LabelFrame(detail_paned, text="Chi Offre (Venditori)", padding=5)
        detail_paned.add(offre_frame, weight=1)
        
        cols_offre = ("venditore", "prezzo", "provvigione", "tipologia")
        self.tree_offre = ttk.Treeview(offre_frame, columns=cols_offre, show="tree headings", height=8)
        
        self.tree_offre.column("#0", width=0, stretch=tk.NO)
        for col in cols_offre:
            self.tree_offre.heading(col, text=col.capitalize())
            self.tree_offre.column(col, width=120)
        
        self.tree_offre.pack(fill=tk.BOTH, expand=True)

        # Info totale record offre
        self.info_offre_label = ttk.Label(offre_frame, text="Totale offerte: 0", font=("Arial", 9, "italic"))
        self.info_offre_label.pack(pady=2)

        # Chi cerca (Compratori)
        cerca_frame = ttk.LabelFrame(detail_paned, text="Chi Cerca (Compratori)", padding=5)
        detail_paned.add(cerca_frame, weight=1)
        
        cols_cerca = ("compratore", "note")
        self.tree_cerca = ttk.Treeview(cerca_frame, columns=cols_cerca, show="tree headings", height=8)
        
        self.tree_cerca.column("#0", width=0, stretch=tk.NO)
        for col in cols_cerca:
            self.tree_cerca.heading(col, text=col.capitalize())
            self.tree_cerca.column(col, width=200)

        self.tree_cerca.pack(fill=tk.BOTH, expand=True)

        # Info totale record cerca
        self.info_cerca_label = ttk.Label(cerca_frame, text="Totale ricerche: 0", font=("Arial", 9, "italic"))
        self.info_cerca_label.pack(pady=2)

    def load_data(self):
        """Carica articoli"""
        try:
            self.articoli = self.api_client.get_articoli()
            self.populate_table(self.articoli)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare:\n{str(e)}")
    
    def populate_table(self, data: List[Dict]):
        """Popola tabella"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for a in data:
            values = (
                a.get("id"),
                a.get("nome", ""),
                a.get("unita_misura", ""),
                a.get("tipo_id", ""),
                a.get("famiglia_id", "")
            )
            self.tree.insert("", tk.END, values=values)

        # Aggiorna contatore
        self.info_articoli_label.config(text=f"Totale articoli: {len(data)}")
    
    def filter_data(self):
        """Filtra"""
        search = self.search_var.get().lower()
        if not search:
            self.populate_table(self.articoli)
            return
        
        filtered = [a for a in self.articoli if search in a.get("nome", "").lower()]
        self.populate_table(filtered)
    
    def sort_by(self, col):
        """Ordina tabella per colonna"""
        # Cambia direzione se clicchi sulla stessa colonna
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        
        # Mappa nomi colonne
        col_map = {"id": "id", "nome": "nome", "um": "unita_misura", "tipo": "tipo_id", "famiglia": "famiglia_id"}
        sort_key = col_map.get(col, col)
        
        # Ordina
        try:
            sorted_data = sorted(
                self.articoli,
                key=lambda x: x.get(sort_key, ""),
                reverse=self.sort_reverse
            )
            self.populate_table(sorted_data)
            
            # Aggiorna intestazione con freccia
            for c in ["id", "nome", "um", "tipo", "famiglia"]:
                text = c.upper()
                if c == col:
                    text += " ↓" if self.sort_reverse else " ↑"
                self.tree.heading(c, text=text)
        except:
            pass
    
    def on_select(self, event):
        """Selezione articolo - carica chi offre e chi cerca"""
        selection = self.tree.selection()
        if not selection:
            return
        
        values = self.tree.item(selection[0])["values"]
        if values:
            self.selected_id = values[0]
            self.load_offre_cerca()
    
    def load_offre_cerca(self):
        """Carica chi offre e chi cerca per articolo selezionato"""
        # Pulisci tabelle
        for item in self.tree_offre.get_children():
            self.tree_offre.delete(item)
        for item in self.tree_cerca.get_children():
            self.tree_cerca.delete(item)

        if not self.selected_id:
            self.info_offre_label.config(text="Totale offerte: 0")
            self.info_cerca_label.config(text="Totale ricerche: 0")
            return

        try:
            # Chi offre
            offre = self.api_client.get(f"/api/articoli/{self.selected_id}/offre")
            for o in offre:
                self.tree_offre.insert("", tk.END, values=(
                    o.get("venditore_nome", ""),
                    o.get("prezzo", ""),
                    o.get("provvigione", ""),
                    o.get("tipologia", "")
                ))
            self.info_offre_label.config(text=f"Totale offerte: {len(offre)}")

            # Chi cerca
            cerca = self.api_client.get(f"/api/articoli/{self.selected_id}/cerca")
            for c in cerca:
                self.tree_cerca.insert("", tk.END, values=(
                    c.get("compratore_nome", ""),
                    c.get("note", "")
                ))
            self.info_cerca_label.config(text=f"Totale ricerche: {len(cerca)}")
        except Exception as e:
            print(f"Errore caricamento dettagli: {e}")
    
    def nuovo(self):
        """Nuovo articolo"""
        ArticoloDialog(self, self.api_client, callback=self.load_data)
    
    def modifica(self):
        """Modifica articolo"""
        if not self.selected_id:
            messagebox.showwarning("Attenzione", "Seleziona un articolo")
            return
        ArticoloDialog(self, self.api_client, articolo_id=self.selected_id, callback=self.load_data)
    
    def elimina(self):
        """Elimina articolo"""
        if not self.selected_id:
            messagebox.showwarning("Attenzione", "Seleziona un articolo")
            return
        
        if messagebox.askyesno("Conferma", "Eliminare questo articolo?"):
            try:
                self.api_client.delete_articolo(self.selected_id)
                messagebox.showinfo("Successo", "Articolo eliminato")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))
    
    def apri_tipologie(self):
        """Apri gestione tipologie"""
        TipologieDialog(self, self.api_client)
    
    def apri_famiglie(self):
        """Apri gestione famiglie"""
        FamiglieDialog(self, self.api_client)


class ArticoloDialog(tk.Toplevel):
    """Dialog per creare/modificare articolo"""
    
    def __init__(self, parent, api_client, articolo_id=None, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.articolo_id = articolo_id
        self.callback = callback
        
        self.title("Modifica Articolo" if articolo_id else "Nuovo Articolo")
        self.geometry("500x300")
        
        self.setup_ui()
        
        if articolo_id:
            self.load_articolo()
    
    def setup_ui(self):
        """Setup form"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Carica tipologie e famiglie per combobox
        try:
            self.tipologie = self.api_client.get("/api/tipologie")
            self.famiglie = self.api_client.get("/api/famiglie")
        except:
            self.tipologie = []
            self.famiglie = []
        
        # Form
        ttk.Label(main_frame, text="Nome:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nome_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.nome_var, width=40).grid(row=0, column=1, pady=5)
        
        ttk.Label(main_frame, text="Unità Misura:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.um_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.um_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Tipologia:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.tipo_var = tk.StringVar()
        tipo_combo = AutocompleteCombobox(main_frame, textvariable=self.tipo_var, values=self.tipologie, width=37)
        tipo_combo.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Famiglia:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.famiglia_var = tk.StringVar()
        fam_combo = AutocompleteCombobox(main_frame, textvariable=self.famiglia_var, values=self.famiglie, width=37)
        fam_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Bottoni
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_articolo(self):
        """Carica dati articolo"""
        try:
            a = self.api_client.get_articolo(self.articolo_id)
            self.nome_var.set(a.get("nome", ""))
            self.um_var.set(a.get("unita_misura", ""))
            self.tipo_var.set(a.get("tipo_id", ""))
            self.famiglia_var.set(a.get("famiglia_id", ""))
        except Exception as e:
            messagebox.showerror("Errore", str(e))
            self.destroy()
    
    def salva(self):
        """Salva articolo"""
        if not self.nome_var.get():
            messagebox.showwarning("Attenzione", "Il nome è obbligatorio")
            return
        
        data = {
            "nome": self.nome_var.get(),
            "unita_misura": self.um_var.get() or None,
            "tipo_id": self.tipo_var.get() or None,
            "famiglia_id": self.famiglia_var.get() or None,
            "attivo": True
        }
        
        try:
            if self.articolo_id:
                self.api_client.update_articolo(self.articolo_id, data)
            else:
                self.api_client.create_articolo(data)
            
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", str(e))


class TipologieDialog(tk.Toplevel):
    """Dialog gestione tipologie"""
    
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        
        self.title("Gestione Tipologie Prodotti")
        self.geometry("600x400")
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup UI"""
        toolbar = ttk.Frame(self, padding=10)
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="Nuova Tipologia", command=self.nuova).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Elimina", command=self.elimina).pack(side=tk.LEFT, padx=5)
        
        # Lista tipologie
        self.listbox = tk.Listbox(self, font=("Arial", 11))
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def load_data(self):
        """Carica tipologie"""
        try:
            tipologie = self.api_client.get("/api/tipologie")
            self.listbox.delete(0, tk.END)
            for t in tipologie:
                self.listbox.insert(tk.END, t)
        except:
            pass
    
    def nuova(self):
        """Nuova tipologia"""
        nome = tk.simpledialog.askstring("Nuova Tipologia", "Nome tipologia:")
        if nome:
            try:
                self.api_client.post("/api/tipologie", data={"nome": nome})
                self.load_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))
    
    def elimina(self):
        """Elimina tipologia"""
        sel = self.listbox.curselection()
        if not sel:
            return
        nome = self.listbox.get(sel[0])
        if messagebox.askyesno("Conferma", f"Eliminare '{nome}'?"):
            try:
                self.api_client.delete(f"/api/tipologie/{nome}")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))


class FamiglieDialog(tk.Toplevel):
    """Dialog gestione famiglie - identico a tipologie"""
    
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        
        self.title("Gestione Famiglie Prodotti")
        self.geometry("600x400")
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup UI"""
        toolbar = ttk.Frame(self, padding=10)
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="Nuova Famiglia", command=self.nuova).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Elimina", command=self.elimina).pack(side=tk.LEFT, padx=5)
        
        self.listbox = tk.Listbox(self, font=("Arial", 11))
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def load_data(self):
        """Carica famiglie"""
        try:
            famiglie = self.api_client.get("/api/famiglie")
            self.listbox.delete(0, tk.END)
            for f in famiglie:
                self.listbox.insert(tk.END, f)
        except:
            pass
    
    def nuova(self):
        """Nuova famiglia"""
        nome = tk.simpledialog.askstring("Nuova Famiglia", "Nome famiglia:")
        if nome:
            try:
                self.api_client.post("/api/famiglie", data={"nome": nome})
                self.load_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))
    
    def elimina(self):
        """Elimina famiglia"""
        sel = self.listbox.curselection()
        if not sel:
            return
        nome = self.listbox.get(sel[0])
        if messagebox.askyesno("Conferma", f"Eliminare '{nome}'?"):
            try:
                self.api_client.delete(f"/api/famiglie/{nome}")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))