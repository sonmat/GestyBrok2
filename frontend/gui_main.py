"""
Frontend GUI con Tkinter per GestyBrok
Architettura MVC pattern
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from typing import Optional

from api_client import APIClient
from views.articoli_view import ArticoliView
from views.venditori_view import VenditoriView
from views.compratori_view import CompratoriView
from views.conferme_view import ConfermeOrdineView
from views.fatture_view import FattureView
from views.report_view import ReportView


class GestyBrokApp(ThemedTk):
    """Applicazione principale"""
    
    def __init__(self):
        super().__init__()
        
        # Configurazione finestra
        self.set_theme("arc")
        self.title("GestyBrok 2.0 - Gestione Trading")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        # API Client
        self.api_client = APIClient(base_url="http://127.0.0.1:8000")
        
        # Verifica connessione
        if not self.check_connection():
            messagebox.showerror(
                "Errore Connessione",
                "Impossibile connettersi al server.\n"
                "Assicurati che il backend sia in esecuzione su http://127.0.0.1:8000"
            )
            self.quit()
            return
        
        # Setup UI
        self.setup_ui()
        
        # Status bar
        self.setup_statusbar()
    
    def check_connection(self) -> bool:
        """Verifica connessione al backend"""
        try:
            response = self.api_client.get("/health")
            return response.get("status") == "healthy"
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def setup_ui(self):
        """Configura interfaccia principale"""
        # Container principale
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crea le viste
        self.create_views()
    
    def create_views(self):
        """Crea tutte le viste dell'applicazione"""
        # Vista Anagrafiche (sottotab)
        anagrafiche_frame = ttk.Frame(self.notebook)
        self.notebook.add(anagrafiche_frame, text="📋 Anagrafiche")
        
        anagrafiche_notebook = ttk.Notebook(anagrafiche_frame)
        anagrafiche_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Sottotab Anagrafiche
        self.articoli_view = ArticoliView(anagrafiche_notebook, self.api_client)
        anagrafiche_notebook.add(self.articoli_view, text="Articoli")
        
        self.venditori_view = VenditoriView(anagrafiche_notebook, self.api_client)
        anagrafiche_notebook.add(self.venditori_view, text="Venditori")
        
        self.compratori_view = CompratoriView(anagrafiche_notebook, self.api_client)
        anagrafiche_notebook.add(self.compratori_view, text="Compratori")
        
        # Vista Operazioni
        self.conferme_view = ConfermeOrdineView(self.notebook, self.api_client)
        self.notebook.add(self.conferme_view, text="📝 Conferme Ordine")
        
        # Vista Fatture
        self.fatture_view = FattureView(self.notebook, self.api_client)
        self.notebook.add(self.fatture_view, text="💰 Fatture")
        
        # Vista Report
        self.report_view = ReportView(self.notebook, self.api_client)
        self.notebook.add(self.report_view, text="📊 Report")
    
    def setup_statusbar(self):
        """Barra di stato in basso"""
        statusbar = ttk.Frame(self, relief=tk.SUNKEN)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(
            statusbar,
            text="✓ Connesso al server",
            padding=(10, 5)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Info versione
        version_label = ttk.Label(
            statusbar,
            text="v2.0.0",
            padding=(10, 5)
        )
        version_label.pack(side=tk.RIGHT)
    
    def update_status(self, message: str):
        """Aggiorna messaggio nella status bar"""
        self.status_label.config(text=message)
        self.update_idletasks()


def main():
    """Entry point dell'applicazione"""
    app = GestyBrokApp()
    app.mainloop()


if __name__ == "__main__":
    main()
