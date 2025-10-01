"""
Sistema di tabelle dinamiche auto-generate dal database
Legge lo schema delle tabelle e genera automaticamente colonne e form
"""
import customtkinter as ctk
from tkinter import ttk
import requests
from typing import Dict, List, Optional, Any
import sqlite3
from datetime import datetime


class DatabaseSchemaReader:
    """Legge lo schema delle tabelle dal database"""

    @staticmethod
    def get_table_columns(db_path: str, table_name: str) -> List[Dict[str, Any]]:
        """
        Legge le colonne di una tabella dal database SQLite

        Returns:
            Lista di dict con: name, type, notnull, default_value, pk
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Ottieni info colonne
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()

        conn.close()

        columns = []
        for col in columns_info:
            columns.append({
                'name': col[1],
                'type': col[2],
                'notnull': col[3],
                'default_value': col[4],
                'pk': col[5]
            })

        return columns

    @staticmethod
    def get_column_display_name(column_name: str) -> str:
        """Converte nome_colonna in Nome Colonna per display"""
        # Rimuovi prefissi comuni
        name = column_name.replace('id_', '').replace('n_', 'N. ')

        # Capitalizza e sostituisci underscore
        words = name.split('_')
        return ' '.join(word.capitalize() for word in words)

    @staticmethod
    def should_show_column(column_name: str, is_detail_table: bool = False) -> bool:
        """Determina se una colonna deve essere mostrata nella tabella"""
        # Nelle tabelle principali nascondi ID
        if not is_detail_table and column_name.startswith('id_'):
            return False

        # Nelle tabelle di dettaglio nascondi solo la PK
        if is_detail_table and (column_name.startswith('id_dati_') or column_name.startswith('id_')):
            # Mostra foreign key ma non primary key
            if 'id_venditore' in column_name or 'id_compratore' in column_name:
                return False  # Nascondi anche FK (è implicita)

        return True


class DynamicTableView(ctk.CTkFrame):
    """
    Tabella generica auto-generata dal database
    """

    def __init__(
        self,
        parent,
        api_endpoint: str,
        table_name: str,
        db_path: str,
        detail_table_config: Optional[Dict] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.api_endpoint = api_endpoint
        self.table_name = table_name
        self.db_path = db_path
        self.detail_table_config = detail_table_config
        self.base_url = "http://localhost:8000"

        # Leggi schema dal database
        self.columns = DatabaseSchemaReader.get_table_columns(db_path, table_name)
        self.visible_columns = [col for col in self.columns
                               if DatabaseSchemaReader.should_show_column(col['name'])]

        self.pk_column = next((col['name'] for col in self.columns if col['pk'] == 1), None)

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        """Crea i widget dell'interfaccia"""
        # Titolo
        title = self.table_name.replace('t_', '').replace('_', ' ').title()
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        # Frame pulsanti
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            btn_frame,
            text="➕ Nuovo",
            command=self.add_record,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="✏️ Modifica",
            command=self.edit_record,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Elimina",
            command=self.delete_record,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Aggiorna",
            command=self.load_data,
            width=100
        ).pack(side="right", padx=5)

        # Crea splitter per tabella principale e dettaglio
        if self.detail_table_config:
            # Frame principale orizzontale
            main_container = ctk.CTkFrame(self, fg_color="transparent")
            main_container.pack(fill="both", expand=True, padx=10, pady=5)

            # Tabella principale (sinistra)
            left_frame = ctk.CTkFrame(main_container)
            left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
            self.create_main_table(left_frame)

            # Tabella dettaglio (destra)
            right_frame = ctk.CTkFrame(main_container)
            right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
            self.create_detail_table(right_frame)
        else:
            # Solo tabella principale
            table_frame = ctk.CTkFrame(self)
            table_frame.pack(fill="both", expand=True, padx=10, pady=5)
            self.create_main_table(table_frame)

    def create_main_table(self, parent):
        """Crea la tabella principale"""
        # Definisci colonne da mostrare
        display_cols = [col['name'] for col in self.visible_columns]
        display_names = [DatabaseSchemaReader.get_column_display_name(col['name'])
                        for col in self.visible_columns]

        # Crea Treeview
        self.tree = ttk.Treeview(
            parent,
            columns=display_cols,
            show="headings",
            selectmode="browse"
        )

        # Configura colonne
        for col_name, display_name in zip(display_cols, display_names):
            self.tree.heading(col_name, text=display_name)
            # Larghezza dinamica in base al tipo
            col_info = next(c for c in self.columns if c['name'] == col_name)
            if 'TEXT' in col_info['type']:
                width = 150
            else:
                width = 100
            self.tree.column(col_name, width=width, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind selezione per aggiornare tabella dettaglio
        if self.detail_table_config:
            self.tree.bind("<<TreeviewSelect>>", self.on_main_table_select)

    def create_detail_table(self, parent):
        """Crea la tabella dei dati di dettaglio"""
        if not self.detail_table_config:
            return

        detail_table = self.detail_table_config['table_name']
        detail_api = self.detail_table_config['api_endpoint']

        # Titolo
        title = detail_table.replace('t_dati_', 'Dati ').replace('_', ' ').title()
        ctk.CTkLabel(
            parent,
            text=title,
            font=("Arial", 16, "bold")
        ).pack(pady=5)

        # Pulsanti gestione dettaglio
        detail_btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        detail_btn_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            detail_btn_frame,
            text="➕ Nuovo Dato",
            command=self.add_detail_record,
            width=100
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            detail_btn_frame,
            text="✏️ Modifica",
            command=self.edit_detail_record,
            width=100
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            detail_btn_frame,
            text="🗑️ Elimina",
            command=self.delete_detail_record,
            width=100
        ).pack(side="left", padx=2)

        # Leggi schema tabella dettaglio
        detail_columns = DatabaseSchemaReader.get_table_columns(self.db_path, detail_table)
        visible_detail_cols = [col for col in detail_columns
                              if DatabaseSchemaReader.should_show_column(col['name'], is_detail_table=True)]

        display_cols = [col['name'] for col in visible_detail_cols]
        display_names = [DatabaseSchemaReader.get_column_display_name(col['name'])
                        for col in visible_detail_cols]

        # Crea Treeview dettaglio
        self.detail_tree = ttk.Treeview(
            parent,
            columns=display_cols,
            show="headings",
            selectmode="browse",
            height=10
        )

        for col_name, display_name in zip(display_cols, display_names):
            self.detail_tree.heading(col_name, text=display_name)
            self.detail_tree.column(col_name, width=120, anchor="center")

        # Scrollbar
        detail_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=detail_scrollbar.set)

        self.detail_tree.pack(side="left", fill="both", expand=True, padx=(5, 0))
        detail_scrollbar.pack(side="right", fill="y")

        # Salva info dettaglio
        self.detail_columns = detail_columns
        self.visible_detail_columns = visible_detail_cols
        self.detail_pk_column = next((col['name'] for col in detail_columns if col['pk'] == 1), None)

    def on_main_table_select(self, event):
        """Gestisce selezione nella tabella principale e aggiorna dettaglio"""
        selection = self.tree.selection()
        if not selection:
            # Pulisci tabella dettaglio
            if hasattr(self, 'detail_tree'):
                for item in self.detail_tree.get_children():
                    self.detail_tree.delete(item)
            return

        # Ottieni PK dai tags
        tags = self.tree.item(selection[0])['tags']
        pk_value = None
        if tags and len(tags) > 0:
            try:
                pk_value = int(tags[0])
            except:
                pk_value = tags[0]

        # Carica dati dettaglio
        if pk_value is not None:
            self.load_detail_data(pk_value)

    def load_data(self):
        """Carica i dati dalla API"""
        # Pulisci tabella
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            response = requests.get(f"{self.base_url}{self.api_endpoint}")
            if response.status_code == 200:
                data = response.json()

                # Mappa nomi colonne API -> nomi colonne DB
                for record in data:
                    # Estrai valori solo per colonne visibili
                    values = []
                    for col in self.visible_columns:
                        col_name = col['name']
                        # Prova vari possibili mapping (es. id_venditore può essere "id" nell'API)
                        value = record.get(col_name, '')
                        if value == '' and col_name.startswith('id_'):
                            # Prova senza prefisso id_
                            value = record.get('id', '')
                        values.append(value)

                    # Memorizza PK anche se nascosta (prova sia con nome originale che con "id")
                    pk_value = record.get(self.pk_column) or record.get('id')
                    self.tree.insert("", "end", values=values, tags=(str(pk_value),))
        except Exception as e:
            print(f"Errore caricamento dati: {e}")

    def load_detail_data(self, parent_id):
        """Carica dati della tabella di dettaglio"""
        if not self.detail_table_config or not hasattr(self, 'detail_tree'):
            return

        # Pulisci tabella dettaglio
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)

        if not parent_id:
            return

        try:
            # Ottieni FK column name
            fk_column = self.detail_table_config['fk_column']
            detail_api = self.detail_table_config['api_endpoint']

            # Carica dati filtrati (l'API supporta filtro via query param)
            response = requests.get(f"{self.base_url}{detail_api}?{fk_column}={parent_id}")
            if response.status_code == 200:
                data = response.json()

                for record in data:
                    # Estrai valori per colonne visibili
                    values = []
                    for col in self.visible_detail_columns:
                        col_name = col['name']
                        value = record.get(col_name, '')
                        # Gestisci mapping id
                        if value == '' and col_name.startswith('id_') and col_name != fk_column:
                            value = record.get('id', '')
                        values.append(value)

                    pk_value = record.get(self.detail_pk_column) or record.get('id')
                    self.detail_tree.insert("", "end", values=values, tags=(str(pk_value),))
        except Exception as e:
            print(f"Errore caricamento dettaglio: {e}")

    def get_selected_record(self):
        """Ottiene il record selezionato"""
        selection = self.tree.selection()
        if not selection:
            return None

        item = self.tree.item(selection[0])
        values = item['values']
        tags = self.tree.item(selection[0])['tags']

        # Ricostruisci dizionario completo
        record = {}
        for col, val in zip(self.visible_columns, values):
            record[col['name']] = val

        # Aggiungi PK (sempre dai tags)
        if tags and len(tags) > 0:
            try:
                record[self.pk_column] = int(tags[0])
            except:
                record[self.pk_column] = tags[0]

        return record

    def add_record(self):
        """Aggiunge un nuovo record"""
        dialog = DynamicRecordDialog(
            self,
            title=f"Nuovo {self.table_name}",
            columns=self.columns,
            pk_column=self.pk_column,
            api_endpoint=self.api_endpoint,
            base_url=self.base_url
        )
        self.wait_window(dialog)
        self.load_data()

    def edit_record(self):
        """Modifica il record selezionato"""
        record = self.get_selected_record()
        if not record:
            return

        dialog = DynamicRecordDialog(
            self,
            title=f"Modifica {self.table_name}",
            columns=self.columns,
            pk_column=self.pk_column,
            api_endpoint=self.api_endpoint,
            base_url=self.base_url,
            record_data=record
        )
        self.wait_window(dialog)
        self.load_data()

    def delete_record(self):
        """Elimina il record selezionato"""
        record = self.get_selected_record()
        if not record:
            return

        pk_value = record.get(self.pk_column)
        if not pk_value:
            return

        try:
            response = requests.delete(f"{self.base_url}{self.api_endpoint}/{pk_value}")
            if response.status_code == 200:
                self.load_data()
        except Exception as e:
            print(f"Errore eliminazione: {e}")

    def add_detail_record(self):
        """Aggiunge un record alla tabella dettaglio"""
        if not self.detail_table_config:
            return

        # Ottieni ID del record principale selezionato
        record = self.get_selected_record()
        if not record:
            return

        parent_id = record.get(self.pk_column)

        dialog = DynamicRecordDialog(
            self,
            title=f"Nuovo {self.detail_table_config['table_name']}",
            columns=self.detail_columns,
            pk_column=self.detail_pk_column,
            api_endpoint=self.detail_table_config['api_endpoint'],
            base_url=self.base_url,
            default_values={self.detail_table_config['fk_column']: parent_id}
        )
        self.wait_window(dialog)
        self.load_detail_data(parent_id)

    def edit_detail_record(self):
        """Modifica record dettaglio"""
        if not hasattr(self, 'detail_tree'):
            return

        selection = self.detail_tree.selection()
        if not selection:
            return

        item = self.detail_tree.item(selection[0])
        values = item['values']
        tags = self.detail_tree.item(selection[0])['tags']

        # Ricostruisci record
        record = {}
        for col, val in zip(self.visible_detail_columns, values):
            record[col['name']] = val
        if tags:
            record[self.detail_pk_column] = tags[0]

        # Ottieni parent_id
        main_record = self.get_selected_record()
        parent_id = main_record.get(self.pk_column) if main_record else None

        dialog = DynamicRecordDialog(
            self,
            title=f"Modifica {self.detail_table_config['table_name']}",
            columns=self.detail_columns,
            pk_column=self.detail_pk_column,
            api_endpoint=self.detail_table_config['api_endpoint'],
            base_url=self.base_url,
            record_data=record
        )
        self.wait_window(dialog)
        if parent_id:
            self.load_detail_data(parent_id)

    def delete_detail_record(self):
        """Elimina record dettaglio"""
        if not hasattr(self, 'detail_tree'):
            return

        selection = self.detail_tree.selection()
        if not selection:
            return

        tags = self.detail_tree.item(selection[0])['tags']
        if not tags:
            return

        pk_value = tags[0]

        try:
            response = requests.delete(
                f"{self.base_url}{self.detail_table_config['api_endpoint']}/{pk_value}"
            )
            if response.status_code == 200:
                # Ricarica dettaglio
                main_record = self.get_selected_record()
                if main_record:
                    parent_id = main_record.get(self.pk_column)
                    self.load_detail_data(parent_id)
        except Exception as e:
            print(f"Errore eliminazione dettaglio: {e}")


class DynamicRecordDialog(ctk.CTkToplevel):
    """Dialog per inserimento/modifica record con campi auto-generati"""

    def __init__(
        self,
        parent,
        title: str,
        columns: List[Dict],
        pk_column: str,
        api_endpoint: str,
        base_url: str,
        record_data: Optional[Dict] = None,
        default_values: Optional[Dict] = None
    ):
        super().__init__(parent)

        self.title(title)
        self.geometry("500x600")

        self.columns = columns
        self.pk_column = pk_column
        self.api_endpoint = api_endpoint
        self.base_url = base_url
        self.record_data = record_data
        self.default_values = default_values or {}

        self.entries = {}

        self.create_widgets()

        # Centra finestra
        self.transient(parent)
        self.grab_set()

    def create_widgets(self):
        """Crea i widget del form"""
        # Scrollable frame per campi
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Genera campo per ogni colonna (esclusa PK se auto-increment)
        for col in self.columns:
            col_name = col['name']

            # Salta PK se è auto-increment
            if col['pk'] == 1 and not self.record_data:
                continue

            # Label
            display_name = DatabaseSchemaReader.get_column_display_name(col_name)
            label = ctk.CTkLabel(
                scroll_frame,
                text=display_name,
                anchor="w"
            )
            label.pack(fill="x", pady=(10, 0))

            # Entry
            entry = ctk.CTkEntry(scroll_frame)
            entry.pack(fill="x", pady=(0, 5))

            # Popola con dati esistenti o default
            if self.record_data and col_name in self.record_data:
                entry.insert(0, str(self.record_data[col_name]))
            elif col_name in self.default_values:
                entry.insert(0, str(self.default_values[col_name]))
                entry.configure(state="disabled")  # FK non modificabile

            self.entries[col_name] = entry

        # Pulsanti
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Salva",
            command=self.save_record,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Annulla",
            command=self.destroy,
            width=100
        ).pack(side="right", padx=5)

    def save_record(self):
        """Salva il record via API"""
        data = {}

        for col_name, entry in self.entries.items():
            value = entry.get()
            # Converti tipo se necessario
            col_info = next(c for c in self.columns if c['name'] == col_name)

            if value == '':
                data[col_name] = None
            elif 'INTEGER' in col_info['type']:
                try:
                    data[col_name] = int(value)
                except:
                    data[col_name] = None
            else:
                data[col_name] = value

        try:
            if self.record_data:
                # Update
                pk_value = self.record_data[self.pk_column]
                response = requests.put(
                    f"{self.base_url}{self.api_endpoint}/{pk_value}",
                    json=data
                )
            else:
                # Create
                response = requests.post(
                    f"{self.base_url}{self.api_endpoint}",
                    json=data
                )

            if response.status_code in [200, 201]:
                self.destroy()
        except Exception as e:
            print(f"Errore salvataggio: {e}")
