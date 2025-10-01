"""
Widget riutilizzabili: Combobox con autocomplete e DatePicker
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import calendar


class AutocompleteCombobox(ttk.Combobox):
    """Combobox con autocompletamento mentre si scrive - usando il metodo del tuo vecchio codice"""

    def __init__(self, parent, textvariable=None, values=None, width=None, **kwargs):
        if textvariable:
            kwargs['textvariable'] = textvariable
        if width:
            kwargs['width'] = width

        super().__init__(parent, **kwargs)

        self._completion_list = values or []
        self._id_map = {}  # Mappa nome -> id per tuple (id, nome)

        if values:
            self._set_values(values)

        # Bind per autocompletamento
        self.bind('<KeyRelease>', self._on_keyrelease)

    def _set_values(self, values):
        """Imposta valori - gestisce sia liste semplici che tuple (id, nome)"""
        if not values:
            self['values'] = []
            return

        # Controlla se sono tuple (id, nome)
        if values and isinstance(values[0], (tuple, list)) and len(values[0]) == 2:
            # Estrai i nomi e crea mappa id
            display_values = []
            self._id_map = {}
            for id_val, name_val in values:
                display_values.append(name_val)
                self._id_map[name_val] = id_val
            self['values'] = display_values
        else:
            # Lista semplice di stringhe
            self['values'] = values

    def set_completion_list(self, completion_list):
        """Aggiorna lista valori - gestisce tuple (id, nome) o stringhe"""
        self._completion_list = completion_list
        self._set_values(completion_list)

    def get_selected_id(self):
        """Ottieni l'ID della selezione corrente (per tuple)"""
        current_value = self.get()
        return self._id_map.get(current_value, None)

    def set_by_id(self, id_value):
        """Imposta valore tramite ID (per tuple)"""
        for name, id_val in self._id_map.items():
            if id_val == id_value:
                self.set(name)
                return True
        return False

    def _on_keyrelease(self, event):
        """Gestisce rilascio tasto - filtra i valori"""
        # Ignora tasti speciali
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return', 'Tab'):
            return

        value = self.get()

        # Filtra i risultati
        if value == '':
            data = self._completion_list  # Se vuoto, mostra tutti
        else:
            data = []
            for item in self._completion_list:
                # Gestisci tuple (id, nome)
                if isinstance(item, (tuple, list)) and len(item) == 2:
                    search_text = str(item[1])  # Cerca nel nome
                else:
                    search_text = str(item)

                if value.lower() in search_text.lower():  # Filtra per contenimento
                    data.append(item)

        # Aggiorna i valori della combobox
        self._set_values(data)

        # Apri il dropdown solo se ci sono risultati
        if data:
            self.event_generate('<Down>')

            # TRUCCO: riporta il focus sulla combobox dopo un breve delay
            # in modo da poter continuare a scrivere
            # Delay aumentato a 100ms per dare tempo al dropdown di aprirsi
            self.after(100, lambda: self.focus_set())

    def grid(self, **kwargs):
        """Override grid per compatibilità"""
        super().grid(**kwargs)
        return self

    def pack(self, **kwargs):
        """Override pack per compatibilità"""
        super().pack(**kwargs)
        return self


class DateEntry(ttk.Frame):
    """Campo data con picker"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        
        self.date_var = tk.StringVar()
        
        # Entry per scrivere manualmente
        self.entry = ttk.Entry(self, textvariable=self.date_var, width=12)
        self.entry.pack(side=tk.LEFT)
        self.entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Bottone calendario
        self.btn = ttk.Button(self, text="📅", width=3, command=self.show_calendar)
        self.btn.pack(side=tk.LEFT, padx=(2, 0))
    
    def show_calendar(self):
        """Mostra calendar picker"""
        CalendarDialog(self, callback=self.set_date)
    
    def set_date(self, date_str):
        """Imposta data selezionata"""
        self.date_var.set(date_str)
    
    def get(self):
        """Ottieni valore data"""
        return self.date_var.get()
    
    def set(self, value):
        """Imposta valore"""
        self.date_var.set(value)


class CalendarDialog(tk.Toplevel):
    """Dialog calendario per selezionare data"""
    
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        
        self.title("Seleziona Data")
        self.geometry("300x320")
        self.resizable(False, False)
        
        # Data corrente
        self.today = datetime.now()
        self.current_month = self.today.month
        self.current_year = self.today.year
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup calendario"""
        # Frame header con navigazione
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(header, text="◀", width=3, command=self.prev_month).pack(side=tk.LEFT)
        
        self.month_label = ttk.Label(header, text="", font=("Arial", 12, "bold"))
        self.month_label.pack(side=tk.LEFT, expand=True)
        
        ttk.Button(header, text="▶", width=3, command=self.next_month).pack(side=tk.RIGHT)
        
        # Frame calendario
        cal_frame = ttk.Frame(self)
        cal_frame.pack(padx=10, pady=5)
        
        # Header giorni settimana
        days = ["Lu", "Ma", "Me", "Gi", "Ve", "Sa", "Do"]
        for i, day in enumerate(days):
            ttk.Label(cal_frame, text=day, width=4, anchor=tk.CENTER, font=("Arial", 9, "bold")).grid(row=0, column=i, padx=1, pady=2)
        
        # Bottoni giorni
        self.day_buttons = []
        for row in range(6):
            week = []
            for col in range(7):
                btn = tk.Button(cal_frame, text="", width=4, command=lambda r=row, c=col: self.select_day(r, c))
                btn.grid(row=row+1, column=col, padx=1, pady=1)
                week.append(btn)
            self.day_buttons.append(week)
        
        # Bottone oggi
        ttk.Button(self, text="Oggi", command=self.select_today).pack(pady=10)
        
        self.update_calendar()
    
    def update_calendar(self):
        """Aggiorna visualizzazione calendario"""
        # Aggiorna label mese/anno
        month_name = calendar.month_name[self.current_month]
        self.month_label.config(text=f"{month_name} {self.current_year}")
        
        # Ottieni calendario mese
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Resetta tutti i bottoni
        for week in self.day_buttons:
            for btn in week:
                btn.config(text="", state=tk.DISABLED, bg="SystemButtonFace")
        
        # Popola giorni
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day != 0:
                    btn = self.day_buttons[week_idx][day_idx]
                    btn.config(text=str(day), state=tk.NORMAL)
                    
                    # Evidenzia oggi
                    if (day == self.today.day and 
                        self.current_month == self.today.month and 
                        self.current_year == self.today.year):
                        btn.config(bg="lightblue")
                    else:
                        btn.config(bg="SystemButtonFace")
    
    def prev_month(self):
        """Mese precedente"""
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar()
    
    def next_month(self):
        """Mese successivo"""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.update_calendar()
    
    def select_day(self, row, col):
        """Seleziona giorno"""
        day = self.day_buttons[row][col].cget("text")
        if day:
            date_str = f"{int(day):02d}/{self.current_month:02d}/{self.current_year}"
            if self.callback:
                self.callback(date_str)
            self.destroy()
    
    def select_today(self):
        """Seleziona oggi"""
        date_str = self.today.strftime("%d/%m/%Y")
        if self.callback:
            self.callback(date_str)
        self.destroy()