"""
Client per comunicazione con Backend API
"""
import requests
from typing import Optional, Dict, List, Any
from requests.exceptions import RequestException


class APIClient:
    """Client HTTP per interagire con FastAPI backend"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _handle_response(self, response: requests.Response) -> Any:
        """Gestisce risposta HTTP"""
        try:
            response.raise_for_status()
            return response.json() if response.content else None
        except RequestException as e:
            error_msg = f"Errore API: {str(e)}"
            if response.content:
                try:
                    error_detail = response.json().get("detail", str(e))
                    error_msg = f"Errore API: {error_detail}"
                except:
                    pass
            raise Exception(error_msg)
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """GET request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """POST request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data)
        return self._handle_response(response)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """PUT request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(url, json=data)
        return self._handle_response(response)
    
    def delete(self, endpoint: str) -> Any:
        """DELETE request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(url)
        return self._handle_response(response)
    
    # ==================== ARTICOLI ====================
    def get_articoli(self, **filters) -> List[Dict]:
        """Recupera lista articoli"""
        return self.get("/api/articoli", params=filters)
    
    def get_articolo(self, articolo_id: int) -> Dict:
        """Recupera singolo articolo"""
        return self.get(f"/api/articoli/{articolo_id}")
    
    def create_articolo(self, data: Dict) -> Dict:
        """Crea nuovo articolo"""
        return self.post("/api/articoli", data=data)
    
    def update_articolo(self, articolo_id: int, data: Dict) -> Dict:
        """Aggiorna articolo"""
        return self.put(f"/api/articoli/{articolo_id}", data=data)
    
    def delete_articolo(self, articolo_id: int) -> None:
        """Elimina articolo"""
        self.delete(f"/api/articoli/{articolo_id}")
    
    # ==================== VENDITORI ====================
    def get_venditori(self, **filters) -> List[Dict]:
        """Recupera lista venditori"""
        return self.get("/api/venditori", params=filters)
    
    def create_venditore(self, data: Dict) -> Dict:
        """Crea nuovo venditore"""
        return self.post("/api/venditori", data=data)
    
    def update_venditore(self, venditore_id: int, data: Dict) -> Dict:
        """Aggiorna venditore"""
        return self.put(f"/api/venditori/{venditore_id}", data=data)
    
    def delete_venditore(self, venditore_id: int) -> None:
        """Elimina venditore"""
        self.delete(f"/api/venditori/{venditore_id}")
    
    # ==================== COMPRATORI ====================
    def get_compratori(self, **filters) -> List[Dict]:
        """Recupera lista compratori"""
        return self.get("/api/compratori", params=filters)
    
    def create_compratore(self, data: Dict) -> Dict:
        """Crea nuovo compratore"""
        return self.post("/api/compratori", data=data)
    
    def update_compratore(self, compratore_id: int, data: Dict) -> Dict:
        """Aggiorna compratore"""
        return self.put(f"/api/compratori/{compratore_id}", data=data)
    
    def delete_compratore(self, compratore_id: int) -> None:
        """Elimina compratore"""
        self.delete(f"/api/compratori/{compratore_id}")
    
    # ==================== CONFERME ORDINE ====================
    def get_conferme_ordine(self, **filters) -> List[Dict]:
        """Recupera conferme ordine"""
        return self.get("/api/conferme-ordine", params=filters)
    
    def create_conferma_ordine(self, data: Dict) -> Dict:
        """Crea conferma ordine"""
        return self.post("/api/conferme-ordine", data=data)
    
    def update_conferma_ordine(self, conferma_id: int, data: Dict) -> Dict:
        """Aggiorna conferma ordine"""
        return self.put(f"/api/conferme-ordine/{conferma_id}", data=data)
    
    def delete_conferma_ordine(self, conferma_id: int) -> None:
        """Elimina conferma ordine"""
        self.delete(f"/api/conferme-ordine/{conferma_id}")
    
    # ==================== FATTURE ====================
    def get_fatture(self, **filters) -> List[Dict]:
        """Recupera fatture"""
        return self.get("/api/fatture", params=filters)

    def genera_fatture(self, mesi: List[str], anno: int) -> List[Dict]:
        """Genera fatture per mesi specificati"""
        return self.post("/api/fatture/genera", data={"mesi": mesi, "anno": anno})

    # ==================== REPORT ====================
    def get_report_potenziale(self, data_dal: str, data_al: str, id_venditore: Optional[int] = None) -> Dict:
        """Recupera dati report potenziale"""
        params = {"data_dal": data_dal, "data_al": data_al}
        if id_venditore:
            params["id_venditore"] = id_venditore
        return self.get("/api/report/potenziale", params=params)

    def download_report_potenziale_pdf(self, data_dal: str, data_al: str,
                                       id_venditore: Optional[int] = None) -> bytes:
        """Scarica PDF report potenziale"""
        params = {"data_dal": data_dal, "data_al": data_al}
        if id_venditore:
            params["id_venditore"] = id_venditore

        url = f"{self.base_url}/api/report/potenziale/pdf"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def get_report_effettivo(self, data_dal: str, data_al: str, id_venditore: Optional[int] = None) -> Dict:
        """Recupera dati report effettivo"""
        params = {"data_dal": data_dal, "data_al": data_al}
        if id_venditore:
            params["id_venditore"] = id_venditore
        return self.get("/api/report/effettivo", params=params)

    def download_report_effettivo_pdf(self, data_dal: str, data_al: str,
                                      id_venditore: Optional[int] = None) -> bytes:
        """Scarica PDF report effettivo"""
        params = {"data_dal": data_dal, "data_al": data_al}
        if id_venditore:
            params["id_venditore"] = id_venditore

        url = f"{self.base_url}/api/report/effettivo/pdf"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content
