"""
Vista per gestione Conferme Ordine
Con tabella master-detail per date consegna e fatture
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict
from datetime import datetime
from widgets import AutocompleteCombobox

class ConfermeOrdineView(ttk.Frame):
    """Vista conferme ordine con pattern master-detail"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_id: Optional[int] = None
        self.conferme = []
        self.sort_column = None
        self.sort_reverse = False

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup interfaccia master-detail"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Nuova Conferma", command=self.nuova).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Modifica", command=self.modifica).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Elimina", command=self.elimina).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📄 Stampa Conferma", command=self.stampa_conferma).pack(side=tk.LEFT, padx=2)
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
            self.tree_master.heading(col, text=col.capitalize(), command=lambda c=col: self.sort_by(c))
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

        # Toolbar date
        toolbar_date = ttk.Frame(date_frame)
        toolbar_date.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(toolbar_date, text="Aggiungi Data", command=self.aggiungi_data_consegna).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_date, text="Modifica", command=self.modifica_data_consegna).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_date, text="Elimina", command=self.elimina_data_consegna).pack(side=tk.LEFT, padx=2)

        columns_date = ("id", "data_consegna", "quantita")
        self.tree_date = ttk.Treeview(date_frame, columns=columns_date, show="tree headings", height=8)

        self.tree_date.column("#0", width=0, stretch=tk.NO)
        self.tree_date.column("id", width=50, anchor=tk.CENTER)
        self.tree_date.heading("id", text="ID", command=lambda: self.sort_date_by("id"))
        for col in columns_date[1:]:
            self.tree_date.heading(col, text=col.replace("_", " ").capitalize(), command=lambda c=col: self.sort_date_by(c))
            self.tree_date.column(col, width=100)

        self.tree_date.pack(fill=tk.BOTH, expand=True)

        # Fatture
        fatt_frame = ttk.LabelFrame(detail_paned, text="Fatture Associate", padding=5)
        detail_paned.add(fatt_frame, weight=1)

        columns_fatt = ("id", "numero", "data", "importo", "pagata")
        self.tree_fatt = ttk.Treeview(fatt_frame, columns=columns_fatt, show="tree headings", height=8)

        self.tree_fatt.column("#0", width=0, stretch=tk.NO)
        for col in columns_fatt:
            self.tree_fatt.heading(col, text=col.capitalize(), command=lambda c=col: self.sort_fatt_by(c))
            self.tree_fatt.column(col, width=100)

        self.tree_fatt.pack(fill=tk.BOTH, expand=True)

        # Variabili per ordinamento tabelle dettaglio
        self.date_data = []
        self.sort_date_column = None
        self.sort_date_reverse = False
        self.fatt_data = []
        self.sort_fatt_column = None
        self.sort_fatt_reverse = False
    
    def load_data(self):
        """Carica conferme ordine"""
        try:
            self.conferme = self.api_client.get_conferme_ordine()
            self.populate_master(self.conferme)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare:\n{str(e)}")

    def populate_master(self, data=None):
        """Popola tabella master"""
        if data is None:
            data = self.conferme

        for item in self.tree_master.get_children():
            self.tree_master.delete(item)

        for conf in data:
            values = (
                conf.get("id"),
                conf.get("numero_conferma", ""),
                conf.get("data_conferma", ""),
                conf.get("venditore_nome", f"ID: {conf.get('venditore_id', '')}"),
                conf.get("compratore_nome", f"ID: {conf.get('compratore_id', '')}"),
                conf.get("articolo_nome", f"ID: {conf.get('articolo_id', '')}"),
                conf.get("quantita", ""),
                conf.get("prezzo", "")
            )
            self.tree_master.insert("", tk.END, values=values)

    def sort_by(self, col):
        """Ordina per colonna"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        col_map = {
            "id": "id",
            "numero": "numero_conferma",
            "data": "data_conferma",
            "venditore": "venditore_id",
            "compratore": "compratore_id",
            "articolo": "articolo_id",
            "qta": "quantita",
            "prezzo": "prezzo"
        }
        sort_key = col_map.get(col, col)

        try:
            sorted_data = sorted(
                self.conferme,
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_reverse
            )
            self.populate_master(sorted_data)

            # Aggiorna intestazione con freccia
            columns = ["id", "numero", "data", "venditore", "compratore", "articolo", "qta", "prezzo"]
            for c in columns:
                text = c.capitalize()
                if c == col:
                    text += " ↓" if self.sort_reverse else " ↑"
                self.tree_master.heading(c, text=text)
        except:
            pass

    def _sort_key(self, value):
        """Chiave ordinamento"""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                return float(value.replace(',', '.').strip())
            except:
                return value.lower()
        return str(value)
    
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
        # Pulisci tabelle
        for item in self.tree_date.get_children():
            self.tree_date.delete(item)
        for item in self.tree_fatt.get_children():
            self.tree_fatt.delete(item)

        self.date_data = []
        self.fatt_data = []

        if not self.selected_id:
            return

        try:
            # Carica date consegna - CORRETTO
            response = self.api_client.get(f"/api/conferme-ordine/{self.selected_id}/date-consegna")
            date_list = response.get("date", [])  # ← Estrai la lista dal dizionario

            # Per ogni data, carica i dettagli dalla tabella t_date_consegna
            for data_str in date_list:
                # Cerca nella tabella le date consegna
                date_consegna = self.api_client.get(
                    f"/api/date-consegna/by-conferma/{self.selected_id}"
                )
                for d in date_consegna:
                    if d.get("data_consegna") == data_str:
                        self.date_data.append(d)
                        self.tree_date.insert("", tk.END, values=(
                            d.get("id", ""),
                            d.get("data_consegna", ""),
                            d.get("qta_consegna", "")
                        ))

            # Carica fatture (se esiste l'endpoint)
            try:
                fatture = self.api_client.get(f"/api/conferme-ordine/{self.selected_id}/fatture")
                self.fatt_data = fatture
                for f in fatture:
                    self.tree_fatt.insert("", tk.END, values=(
                        f.get("id", ""),
                        f.get("n_fat", ""),
                        f.get("data_fat", ""),
                        "",
                        ""
                    ))
            except:
                pass  # Endpoint fatture non ancora implementato

        except Exception as e:
            print(f"Errore caricamento dettagli: {e}")

    def sort_date_by(self, col):
        """Ordina tabella date consegna"""
        if self.sort_date_column == col:
            self.sort_date_reverse = not self.sort_date_reverse
        else:
            self.sort_date_column = col
            self.sort_date_reverse = False

        col_map = {"id": "id", "data_consegna": "data_consegna", "quantita": "qta_consegna"}
        sort_key = col_map.get(col, col)

        try:
            sorted_data = sorted(
                self.date_data,
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_date_reverse
            )

            # Pulisci e ripopola
            for item in self.tree_date.get_children():
                self.tree_date.delete(item)
            for d in sorted_data:
                self.tree_date.insert("", tk.END, values=(
                    d.get("id", ""),
                    d.get("data_consegna", ""),
                    d.get("qta_consegna", "")
                ))

            # Aggiorna intestazione con freccia
            for c in ["id", "data_consegna", "quantita"]:
                if c == "id":
                    text = "ID"
                else:
                    text = c.replace("_", " ").capitalize()
                if c == col:
                    text += " ↓" if self.sort_date_reverse else " ↑"
                self.tree_date.heading(c, text=text)
        except:
            pass

    def sort_fatt_by(self, col):
        """Ordina tabella fatture"""
        if self.sort_fatt_column == col:
            self.sort_fatt_reverse = not self.sort_fatt_reverse
        else:
            self.sort_fatt_column = col
            self.sort_fatt_reverse = False

        col_map = {"id": "id", "numero": "n_fat", "data": "data_fat", "importo": "importo", "pagata": "pagata"}
        sort_key = col_map.get(col, col)

        try:
            sorted_data = sorted(
                self.fatt_data,
                key=lambda x: self._sort_key(x.get(sort_key, "")),
                reverse=self.sort_fatt_reverse
            )

            # Pulisci e ripopola
            for item in self.tree_fatt.get_children():
                self.tree_fatt.delete(item)
            for f in sorted_data:
                self.tree_fatt.insert("", tk.END, values=(
                    f.get("id", ""),
                    f.get("n_fat", ""),
                    f.get("data_fat", ""),
                    "",
                    ""
                ))

            # Aggiorna intestazione con freccia
            for c in ["id", "numero", "data", "importo", "pagata"]:
                text = c.capitalize()
                if c == col:
                    text += " ↓" if self.sort_fatt_reverse else " ↑"
                self.tree_fatt.heading(c, text=text)
        except:
            pass
    
    def aggiungi_data_consegna(self):
        """Aggiungi data consegna"""
        if not self.selected_id:
            messagebox.showwarning("Attenzione", "Seleziona una conferma ordine")
            return
        DataConsegnaDialog(self, self.api_client, self.selected_id, callback=self.load_details)

    def modifica_data_consegna(self):
        """Modifica data consegna"""
        selection = self.tree_date.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una data da modificare")
            return

        data_id = self.tree_date.item(selection[0])["values"][0]
        DataConsegnaDialog(self, self.api_client, self.selected_id, data_id=data_id, callback=self.load_details)

    def elimina_data_consegna(self):
        """Elimina data consegna selezionata"""
        selection = self.tree_date.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una data da eliminare")
            return
        
        data_id = self.tree_date.item(selection[0])["values"][0]
        
        if messagebox.askyesno("Conferma", "Eliminare questa data di consegna?"):
            try:
                self.api_client.delete(f"/api/date-consegna/{data_id}")
                self.load_details()
            except Exception as e:
                messagebox.showerror("Errore", str(e))
    
    def nuova(self):
        """Nuova conferma ordine"""
        ConfermaDialog(self, self.api_client, callback=self.load_data)

    def modifica(self):
        """Modifica conferma ordine"""
        if not self.selected_id:
            messagebox.showwarning("Attenzione", "Seleziona una conferma ordine")
            return
        ConfermaDialog(self, self.api_client, conferma_id=self.selected_id, callback=self.load_data)

    def elimina(self):
        """Elimina conferma ordine"""
        if not self.selected_id:
            messagebox.showwarning("Attenzione", "Seleziona una conferma ordine")
            return

        if messagebox.askyesno("Conferma", "Eliminare questa conferma ordine?"):
            try:
                self.api_client.delete(f"/api/conferme-ordine/{self.selected_id}")
                messagebox.showinfo("Successo", "Conferma ordine eliminata")
                self.selected_id = None
                self.load_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    def stampa_conferma(self):
        """Stampa conferma d'ordine (genera PDF per venditore e compratore)"""
        if not self.selected_id:
            messagebox.showwarning("Attenzione", "Seleziona una conferma ordine da stampare")
            return

        # Ottieni i dati dalla riga selezionata della tabella
        selection = self.tree_master.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una conferma ordine da stampare")
            return

        try:
            # Leggi i valori dalla riga selezionata
            values = self.tree_master.item(selection[0])["values"]

            # Mappa valori dalle colonne della tabella
            # columns_master = ("id", "numero", "data", "venditore", "compratore", "articolo", "qta", "prezzo")
            conferma_display = {
                "id": values[0] if len(values) > 0 else "N/A",
                "numero": values[1] if len(values) > 1 else "N/A",
                "data": values[2] if len(values) > 2 else "N/A",
                "venditore": values[3] if len(values) > 3 else "N/A",
                "compratore": values[4] if len(values) > 4 else "N/A",
                "articolo": values[5] if len(values) > 5 else "N/A",
                "qta": values[6] if len(values) > 6 else "N/A",
                "prezzo": values[7] if len(values) > 7 else "N/A"
            }

            # Carica anche i dati completi dall'API per informazioni aggiuntive
            conferma_api = self.api_client.get(f"/api/conferme-ordine/{self.selected_id}")

            # Importa il modulo per generazione PDF (da implementare)
            import os
            import json

            # Carica dati aziendali
            config_path = os.path.join(
                os.path.dirname(__file__),
                "..", "..", "config", "company_data.json"
            )

            with open(config_path, 'r', encoding='utf-8') as f:
                company_data = json.load(f)

            # Carica date consegna per la conferma
            date_consegna = []
            for item in self.tree_date.get_children():
                date_values = self.tree_date.item(item)["values"]
                date_consegna.append({
                    "data": date_values[1] if len(date_values) > 1 else "",
                    "quantita": date_values[2] if len(date_values) > 2 else ""
                })

            # TODO: Implementare generazione PDF
            # Per ora mostra un messaggio di conferma
            date_info = "\n".join([f"  - {d['data']}: {d['quantita']}" for d in date_consegna]) if date_consegna else "  Nessuna data consegna"

            messagebox.showinfo(
                "Stampa Conferma",
                f"Funzione in fase di implementazione.\n\n"
                f"Verranno generati 2 PDF:\n"
                f"1. Conferma per Venditore: {conferma_display['venditore']}\n"
                f"2. Conferma per Compratore: {conferma_display['compratore']}\n\n"
                f"Conferma N°: {conferma_display['numero']}\n"
                f"Data: {conferma_display['data']}\n"
                f"Articolo: {conferma_display['articolo']}\n"
                f"Quantità: {conferma_display['qta']}\n"
                f"Prezzo: {conferma_display['prezzo']}\n\n"
                f"Date Consegna:\n{date_info}\n\n"
                f"Dati aggiuntivi dall'API:\n"
                f"Provvigione: {conferma_api.get('provvigione', 'N/A')}\n"
                f"Luogo consegna: {conferma_api.get('luogo_consegna', 'N/A')}\n"
                f"Condizioni pag: {conferma_api.get('condizioni_pag', 'N/A')}\n"
                f"Note: {conferma_api.get('note', 'N/A')}"
            )

            # TODO: Chiamare funzione di generazione PDF
            # from utils.pdf_generator import genera_conferma_venditore, genera_conferma_compratore
            #
            # Prepara dati completi per il PDF
            # conferma_completa = {
            #     **conferma_display,
            #     **conferma_api,
            #     "date_consegna": date_consegna
            # }
            #
            # pdf_venditore = genera_conferma_venditore(conferma_completa, company_data)
            # pdf_compratore = genera_conferma_compratore(conferma_completa, company_data)
            # messagebox.showinfo("Successo", f"PDF generati:\n{pdf_venditore}\n{pdf_compratore}")

        except FileNotFoundError:
            messagebox.showerror(
                "Errore",
                "File configurazione aziendale non trovato.\n"
                "Verifica che esista: config/company_data.json"
            )
        except json.JSONDecodeError:
            messagebox.showerror(
                "Errore",
                "Errore nella lettura del file di configurazione aziendale"
            )
        except Exception as e:
            import traceback
            messagebox.showerror("Errore", f"Errore durante la stampa:\n{str(e)}\n\n{traceback.format_exc()}")


class ConfermaDialog(tk.Toplevel):
    """Dialog per creare/modificare conferma ordine"""

    def __init__(self, parent, api_client, conferma_id=None, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.conferma_id = conferma_id
        self.callback = callback

        self.title("Modifica Conferma Ordine" if conferma_id else "Nuova Conferma Ordine")
        self.geometry("600x500")

        self.setup_ui()

        if conferma_id:
            self.load_conferma()
    
    def setup_ui(self):
        """Setup form"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Carica dati per combobox
        try:
            venditori = self.api_client.get_venditori()
            self.venditori_dict = {v['azienda']: v['id'] for v in venditori}
            
            compratori = self.api_client.get_compratori()
            self.compratori_dict = {c['azienda']: c['id'] for c in compratori}
            
            articoli = self.api_client.get_articoli()
            self.articoli_dict = {a['nome']: a['id'] for a in articoli}
        except:
            self.venditori_dict = {}
            self.compratori_dict = {}
            self.articoli_dict = {}
        
        row = 0
        
        # Numero conferma
        ttk.Label(main_frame, text="N. Conferma:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.n_conf_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.n_conf_var, width=30).grid(row=row, column=1, pady=5)
        row += 1
        
        # Data conferma
        ttk.Label(main_frame, text="Data Conferma:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.data_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        ttk.Entry(main_frame, textvariable=self.data_var, width=15).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="(gg/mm/aaaa)", foreground="gray").grid(row=row, column=2, sticky=tk.W, padx=5)
        row += 1
        
        # Venditore
        ttk.Label(main_frame, text="Venditore:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vend_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.vend_var, values=list(self.venditori_dict.keys()), width=40).grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        # Compratore
        ttk.Label(main_frame, text="Compratore:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.comp_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.comp_var, values=list(self.compratori_dict.keys()), width=40).grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        # Articolo
        ttk.Label(main_frame, text="Articolo:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.art_var = tk.StringVar()
        AutocompleteCombobox(main_frame, textvariable=self.art_var, values=list(self.articoli_dict.keys()), width=40).grid(row=row, column=1, columnspan=2, pady=5)
        row += 1
        
        # Quantità
        ttk.Label(main_frame, text="Quantità:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.qta_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.qta_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Prezzo
        ttk.Label(main_frame, text="Prezzo:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.prezzo_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.prezzo_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Provvigione
        ttk.Label(main_frame, text="Provvigione:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.prov_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.prov_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Tipologia
        ttk.Label(main_frame, text="Tipologia:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tipo_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.tipo_var, width=30).grid(row=row, column=1, pady=5)
        row += 1
        
        # Note
        ttk.Label(main_frame, text="Note:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.note_text = tk.Text(main_frame, width=40, height=4)
        self.note_text.grid(row=row, column=1, columnspan=2, pady=5)
        row += 1
        
        # Bottoni
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)

        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def load_conferma(self):
        """Carica dati conferma esistente"""
        try:
            conf = self.api_client.get(f"/api/conferme-ordine/{self.conferma_id}")

            self.n_conf_var.set(conf.get("numero_conferma", ""))
            self.data_var.set(conf.get("data_conferma", ""))

            # Trova il nome del venditore/compratore/articolo
            vend_id = conf.get("venditore_id")
            comp_id = conf.get("compratore_id")
            art_id = conf.get("articolo_id")

            # Cerca nei dizionari
            for nome, id_val in self.venditori_dict.items():
                if id_val == vend_id:
                    self.vend_var.set(nome)
                    break

            for nome, id_val in self.compratori_dict.items():
                if id_val == comp_id:
                    self.comp_var.set(nome)
                    break

            for nome, id_val in self.articoli_dict.items():
                if id_val == art_id:
                    self.art_var.set(nome)
                    break

            self.qta_var.set(str(conf.get("quantita", "")))
            self.prezzo_var.set(str(conf.get("prezzo", "")))
            self.prov_var.set(str(conf.get("provvigione", "")))
            self.tipo_var.set(conf.get("tipologia", ""))
            self.note_text.delete("1.0", tk.END)
            self.note_text.insert("1.0", conf.get("note", ""))

        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare conferma:\n{str(e)}")
            self.destroy()

    def salva(self):
        """Salva conferma ordine"""
        # Validazione
        if not self.vend_var.get():
            messagebox.showwarning("Attenzione", "Seleziona un venditore")
            return
        if not self.comp_var.get():
            messagebox.showwarning("Attenzione", "Seleziona un compratore")
            return
        if not self.art_var.get():
            messagebox.showwarning("Attenzione", "Seleziona un articolo")
            return
        if not self.qta_var.get() or not self.prezzo_var.get():
            messagebox.showwarning("Attenzione", "Quantità e Prezzo sono obbligatori")
            return

        # Recupera ID
        venditore_id = self.venditori_dict.get(self.vend_var.get())
        compratore_id = self.compratori_dict.get(self.comp_var.get())
        articolo_id = self.articoli_dict.get(self.art_var.get())

        if not all([venditore_id, compratore_id, articolo_id]):
            messagebox.showerror("Errore", "Seleziona valori validi dalle liste")
            return

        data = {
            "numero_conferma": self.n_conf_var.get() or None,
            "data_conferma": self.data_var.get(),
            "venditore_id": venditore_id,
            "compratore_id": compratore_id,
            "articolo_id": articolo_id,
            "quantita": float(self.qta_var.get()),
            "prezzo": float(self.prezzo_var.get()),
            "provvigione": float(self.prov_var.get()) if self.prov_var.get() else None,
            "tipologia": self.tipo_var.get() or None,
            "note": self.note_text.get("1.0", tk.END).strip() or None
        }

        try:
            if self.conferma_id:
                # Modifica
                self.api_client.put(f"/api/conferme-ordine/{self.conferma_id}", data=data)
                messagebox.showinfo("Successo", "Conferma ordine aggiornata")
            else:
                # Crea nuova
                self.api_client.post("/api/conferme-ordine", data=data)
                messagebox.showinfo("Successo", "Conferma ordine creata")

            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", str(e))


class DataConsegnaDialog(tk.Toplevel):
    """Dialog per aggiungere/modificare data consegna"""

    def __init__(self, parent, api_client, conferma_id, data_id=None, callback=None):
        super().__init__(parent)
        self.api_client = api_client
        self.conferma_id = conferma_id
        self.data_id = data_id
        self.callback = callback

        self.title("Modifica Data Consegna" if data_id else "Nuova Data Consegna")
        self.geometry("400x200")

        self.setup_ui()

        if data_id:
            self.load_data()

    def setup_ui(self):
        """Setup form"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Data Consegna:*").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.data_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        ttk.Entry(main_frame, textvariable=self.data_var, width=15).grid(row=0, column=1, pady=10, sticky=tk.W)
        ttk.Label(main_frame, text="(gg/mm/aaaa)", foreground="gray").grid(row=0, column=2, sticky=tk.W, padx=5)

        ttk.Label(main_frame, text="Quantità:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.qta_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.qta_var, width=20).grid(row=1, column=1, pady=10, sticky=tk.W)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=20)

        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        """Carica dati esistenti"""
        try:
            data = self.api_client.get(f"/api/date-consegna/{self.data_id}")
            self.data_var.set(data.get("data_consegna", ""))
            self.qta_var.set(data.get("qta_consegna", ""))
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare data consegna:\n{str(e)}")
            self.destroy()

    def salva(self):
        """Salva data consegna"""
        data = {
            "conferma_id": self.conferma_id,
            "data_consegna": self.data_var.get(),
            "qta_consegna": self.qta_var.get() or None
        }

        try:
            if self.data_id:
                # Modifica
                self.api_client.put(f"/api/date-consegna/{self.data_id}", data=data)
                messagebox.showinfo("Successo", "Data consegna aggiornata")
            else:
                # Crea nuova
                self.api_client.post("/api/date-consegna", data=data)
                messagebox.showinfo("Successo", "Data consegna creata")

            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", str(e))