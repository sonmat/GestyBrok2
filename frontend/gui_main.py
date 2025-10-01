"""
Frontend GUI con Tkinter per GestyBrok
Architettura MVC pattern
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from typing import Optional
import os
from PIL import Image, ImageTk

from api_client import APIClient
from views.articoli_view import ArticoliView
from views.venditori_view import VenditoriView
from views.compratori_view import CompratorView
from views.conferme_view import ConfermeOrdineView
from views.fatture_view import FattureView
from views.fatture_studio_view_new import FattureStudioView
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

        # Header con logo
        self.setup_header(main_container)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Crea le viste
        self.create_views()

    def setup_header(self, parent):
        """Configura header con logo"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Carica e mostra il logo
        logo_path = os.path.join(os.path.dirname(__file__), "Logo.png")
        if os.path.exists(logo_path):
            try:
                # Carica immagine e ridimensiona
                image = Image.open(logo_path)
                # Ridimensiona mantenendo proporzioni (altezza max 80px)
                width, height = image.size
                max_height = 80
                if height > max_height:
                    ratio = max_height / height
                    new_width = int(width * ratio)
                    image = image.resize((new_width, max_height), Image.Resampling.LANCZOS)

                self.logo_image = ImageTk.PhotoImage(image)
                logo_label = ttk.Label(header_frame, image=self.logo_image)
                logo_label.pack(side=tk.LEFT, padx=(0, 20))
            except Exception as e:
                print(f"Errore caricamento logo: {e}")

        # Titolo applicazione
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            title_frame,
            text="GestyBrok 2.0",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(anchor=tk.W)

        subtitle_label = ttk.Label(
            title_frame,
            text="Gestione Trading",
            font=("Helvetica", 12)
        )
        subtitle_label.pack(anchor=tk.W)
    
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
        
        self.compratori_view = CompratorView(anagrafiche_notebook, self.api_client)
        anagrafiche_notebook.add(self.compratori_view, text="Compratori")
        
        # Aggiungi IVA, Pagamenti, Banche
        from views.anagrafiche_support import IvaView, PagamentiView, BancheView
        
        self.iva_view = IvaView(anagrafiche_notebook, self.api_client)
        anagrafiche_notebook.add(self.iva_view, text="IVA")
        
        self.pagamenti_view = PagamentiView(anagrafiche_notebook, self.api_client)
        anagrafiche_notebook.add(self.pagamenti_view, text="Pagamenti")
        
        self.banche_view = BancheView(anagrafiche_notebook, self.api_client)
        anagrafiche_notebook.add(self.banche_view, text="Banche")
        
        # Vista Conferme Ordine
        self.conferme_view = ConfermeOrdineView(self.notebook, self.api_client)
        self.notebook.add(self.conferme_view, text="📝 Conferme Ordine")

        # Vista Fatture
        self.fatture_view = FattureView(self.notebook, self.api_client)
        self.notebook.add(self.fatture_view, text="💰 Fatture")

        # Vista Fatture Studio
        self.fatture_studio_view = FattureStudioView(self.notebook, self.api_client)
        self.notebook.add(self.fatture_studio_view, text="📄 Fatture Studio")

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