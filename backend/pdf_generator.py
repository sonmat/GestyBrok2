"""
Generatore PDF per le conferme d'ordine
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from datetime import datetime
from io import BytesIO
import json
import os


class PDFConfermaOrdine:
    """Classe per generare i PDF delle conferme d'ordine"""

    def __init__(self, company_data_path="/home/mattia/GestyBrok2/config/company_data.json",
                 logo_path="/home/mattia/GestyBrok2/frontend/Logo.png"):
        """Inizializza il generatore PDF"""
        self.company_data_path = company_data_path
        self.logo_path = logo_path
        self.company_data = self._load_company_data()

    def _load_company_data(self):
        """Carica i dati aziendali dal JSON"""
        try:
            with open(self.company_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Errore nel caricamento dei dati aziendali: {e}")
            return {}

    def _format_currency(self, value, lang='it'):
        """Formatta un valore come valuta"""
        try:
            val = float(value)
            if lang == 'it':
                return f"€ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            else:
                return f"€ {val:,.2f}"
        except:
            return "€ 0,00" if lang == 'it' else "€ 0.00"

    def _format_date(self, date_str):
        """Formatta una data"""
        if not date_str:
            return ""
        # Se la data è già formattata, la restituisce così com'è
        return str(date_str)

    def genera_conferma_venditore(self, conferma_data, venditore_data, compratore_data,
                                   articolo_data, date_consegna=None):
        """
        Genera la conferma d'ordine per il venditore

        Args:
            conferma_data: dict con dati della conferma (da TConferma)
            venditore_data: dict con dati del venditore (da TVenditore)
            compratore_data: dict con dati del compratore (da TCompratore)
            articolo_data: dict con dati dell'articolo (da TArticolo)
            date_consegna: list di date di consegna

        Returns:
            BytesIO: buffer contenente il PDF generato
        """
        is_estero = venditore_data.get('italiano', 'Si') != 'Si'
        lang = 'en' if is_estero else 'it'

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=2*cm, leftMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)

        # Container per gli elementi del PDF
        elements = []
        styles = getSampleStyleSheet()

        # Stile personalizzato per il titolo
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        # Header con logo e dati azienda
        elements.extend(self._crea_header(lang))

        # Titolo
        if lang == 'it':
            title_text = "CONFERMA D'ORDINE - VENDITORE"
        else:
            title_text = "ORDER CONFIRMATION - SELLER"

        elements.append(Paragraph(title_text, title_style))
        elements.append(Spacer(1, 0.5*cm))

        # Messaggio personalizzato per il venditore
        elements.extend(self._crea_messaggio_venditore(venditore_data, compratore_data, conferma_data, lang))
        elements.append(Spacer(1, 0.5*cm))

        # Informazioni conferma
        elements.extend(self._crea_info_conferma(conferma_data, lang))
        elements.append(Spacer(1, 0.5*cm))

        # Dati venditore e compratore
        elements.extend(self._crea_dati_parti_venditore(
            venditore_data, compratore_data, lang
        ))
        elements.append(Spacer(1, 0.5*cm))

        # Dettagli articolo
        elements.extend(self._crea_dettagli_articolo(
            articolo_data, conferma_data, lang
        ))
        elements.append(Spacer(1, 0.5*cm))

        # Date di consegna
        if date_consegna:
            elements.extend(self._crea_date_consegna(date_consegna, lang))
            elements.append(Spacer(1, 0.5*cm))

        # Note
        if conferma_data.get('note'):
            elements.extend(self._crea_note(conferma_data.get('note'), lang))
            elements.append(Spacer(1, 0.5*cm))

        # Footer
        elements.append(Spacer(1, 1*cm))
        elements.extend(self._crea_footer(lang))

        # Genera il PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def genera_conferma_compratore(self, conferma_data, venditore_data, compratore_data,
                                    articolo_data, date_consegna=None):
        """
        Genera la conferma d'ordine per il compratore

        Args:
            conferma_data: dict con dati della conferma
            venditore_data: dict con dati del venditore
            compratore_data: dict con dati del compratore
            articolo_data: dict con dati dell'articolo
            date_consegna: list di date di consegna

        Returns:
            BytesIO: buffer contenente il PDF generato
        """
        is_estero = compratore_data.get('italiano', 'Si') != 'Si'
        lang = 'en' if is_estero else 'it'

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=2*cm, leftMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)

        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        # Header
        elements.extend(self._crea_header(lang))

        # Titolo
        if lang == 'it':
            title_text = "CONFERMA D'ORDINE - COMPRATORE"
        else:
            title_text = "ORDER CONFIRMATION - BUYER"

        elements.append(Paragraph(title_text, title_style))
        elements.append(Spacer(1, 0.5*cm))

        # Messaggio personalizzato per il compratore
        elements.extend(self._crea_messaggio_compratore(compratore_data, venditore_data, conferma_data, lang))
        elements.append(Spacer(1, 0.5*cm))

        # Informazioni conferma
        elements.extend(self._crea_info_conferma(conferma_data, lang))
        elements.append(Spacer(1, 0.5*cm))

        # Dati compratore e venditore
        elements.extend(self._crea_dati_parti_compratore(
            venditore_data, compratore_data, lang
        ))
        elements.append(Spacer(1, 0.5*cm))

        # Dettagli articolo
        elements.extend(self._crea_dettagli_articolo(
            articolo_data, conferma_data, lang
        ))
        elements.append(Spacer(1, 0.5*cm))

        # Date di consegna
        if date_consegna:
            elements.extend(self._crea_date_consegna(date_consegna, lang))
            elements.append(Spacer(1, 0.5*cm))

        # Note
        if conferma_data.get('note'):
            elements.extend(self._crea_note(conferma_data.get('note'), lang))
            elements.append(Spacer(1, 0.5*cm))

        # Footer
        elements.append(Spacer(1, 1*cm))
        elements.extend(self._crea_footer(lang))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _crea_header(self, lang='it'):
        """Crea l'header con logo e dati azienda"""
        elements = []

        # Tabella per layout header
        header_data = []

        # Logo (se esiste)
        logo_cell = ""
        if os.path.exists(self.logo_path):
            try:
                logo = Image(self.logo_path, width=4*cm, height=2*cm)
                logo_cell = logo
            except:
                logo_cell = ""

        # Dati azienda
        company_info = []
        if self.company_data:
            company_info.append(Paragraph(
                f"<b>{self.company_data.get('ragione_sociale', '')}</b>",
                getSampleStyleSheet()['Normal']
            ))

            address = f"{self.company_data.get('indirizzo', '')}"
            if self.company_data.get('cap') or self.company_data.get('citta'):
                address += f"<br/>{self.company_data.get('cap', '')} {self.company_data.get('citta', '')}"

            company_info.append(Paragraph(address, getSampleStyleSheet()['Normal']))

            contact = []
            if self.company_data.get('telefono'):
                tel_label = 'Tel:' if lang == 'it' else 'Phone:'
                contact.append(f"{tel_label} {self.company_data.get('telefono')}")
            if self.company_data.get('email_principale'):
                contact.append(f"Email: {self.company_data.get('email_principale')}")

            if contact:
                company_info.append(Paragraph(
                    '<br/>'.join(contact),
                    getSampleStyleSheet()['Normal']
                ))

        if logo_cell:
            header_data.append([logo_cell, company_info])
            t = Table(header_data, colWidths=[5*cm, 12*cm])
            t.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(t)
        else:
            # Solo testo se non c'è logo
            for info in company_info:
                elements.append(info)

        elements.append(Spacer(1, 0.5*cm))

        # Linea separatrice
        elements.append(Table([['']], colWidths=[17*cm],
                             style=TableStyle([('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#1a5490'))])))
        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _crea_info_conferma(self, conferma_data, lang='it'):
        """Crea la sezione con le informazioni della conferma"""
        elements = []
        styles = getSampleStyleSheet()

        info_data = []

        if lang == 'it':
            if conferma_data.get('numero_conferma') or conferma_data.get('n_conf'):
                num_conf = conferma_data.get('numero_conferma') or conferma_data.get('n_conf')
                info_data.append(['N° Conferma:', str(num_conf)])

            if conferma_data.get('data_conferma') or conferma_data.get('data_conf'):
                data = conferma_data.get('data_conferma') or conferma_data.get('data_conf')
                info_data.append(['Data:', self._format_date(data)])
        else:
            if conferma_data.get('numero_conferma') or conferma_data.get('n_conf'):
                num_conf = conferma_data.get('numero_conferma') or conferma_data.get('n_conf')
                info_data.append(['Confirmation No.:', str(num_conf)])

            if conferma_data.get('data_conferma') or conferma_data.get('data_conf'):
                data = conferma_data.get('data_conferma') or conferma_data.get('data_conf')
                info_data.append(['Date:', self._format_date(data)])

        if info_data:
            t = Table(info_data, colWidths=[4*cm, 13*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(t)

        return elements

    def _crea_dati_parti_venditore(self, venditore_data, compratore_data, lang='it'):
        """Crea la sezione con i dati di venditore e compratore (vista venditore)"""
        elements = []
        styles = getSampleStyleSheet()

        # Intestazioni
        if lang == 'it':
            venditore_label = 'VENDITORE'
            compratore_label = 'COMPRATORE'
        else:
            venditore_label = 'SELLER'
            compratore_label = 'BUYER'

        # Dati venditore
        venditore_info = [
            Paragraph(f"<b>{venditore_label}</b>", styles['Heading3']),
            Paragraph(f"<b>{venditore_data.get('azienda', '')}</b>", styles['Normal'])
        ]

        if venditore_data.get('indirizzo'):
            venditore_info.append(Paragraph(venditore_data.get('indirizzo'), styles['Normal']))

        city_line = []
        if venditore_data.get('cap'):
            city_line.append(venditore_data.get('cap'))
        if venditore_data.get('citta'):
            city_line.append(venditore_data.get('citta'))
        if city_line:
            venditore_info.append(Paragraph(' '.join(city_line), styles['Normal']))

        if venditore_data.get('partita_iva') or venditore_data.get('piva'):
            piva_label = 'P.IVA:' if lang == 'it' else 'VAT:'
            piva = venditore_data.get('partita_iva') or venditore_data.get('piva')
            venditore_info.append(Paragraph(f"{piva_label} {piva}", styles['Normal']))

        if venditore_data.get('telefono'):
            tel_label = 'Tel:' if lang == 'it' else 'Phone:'
            venditore_info.append(Paragraph(f"{tel_label} {venditore_data.get('telefono')}", styles['Normal']))

        # Dati compratore
        compratore_info = [
            Paragraph(f"<b>{compratore_label}</b>", styles['Heading3']),
            Paragraph(f"<b>{compratore_data.get('azienda', '')}</b>", styles['Normal'])
        ]

        if compratore_data.get('indirizzo'):
            compratore_info.append(Paragraph(compratore_data.get('indirizzo'), styles['Normal']))

        city_line = []
        if compratore_data.get('cap'):
            city_line.append(compratore_data.get('cap'))
        if compratore_data.get('citta'):
            city_line.append(compratore_data.get('citta'))
        if city_line:
            compratore_info.append(Paragraph(' '.join(city_line), styles['Normal']))

        if compratore_data.get('partita_iva') or compratore_data.get('piva'):
            piva_label = 'P.IVA:' if lang == 'it' else 'VAT:'
            piva = compratore_data.get('partita_iva') or compratore_data.get('piva')
            compratore_info.append(Paragraph(f"{piva_label} {piva}", styles['Normal']))

        if compratore_data.get('telefono'):
            tel_label = 'Tel:' if lang == 'it' else 'Phone:'
            compratore_info.append(Paragraph(f"{tel_label} {compratore_data.get('telefono')}", styles['Normal']))

        # Tabella con due colonne
        parti_data = [[venditore_info, compratore_info]]
        t = Table(parti_data, colWidths=[8.5*cm, 8.5*cm])
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ('LINEAFTER', (0, 0), (0, -1), 1, colors.grey),
        ]))
        elements.append(t)

        return elements

    def _crea_dati_parti_compratore(self, venditore_data, compratore_data, lang='it'):
        """Crea la sezione con i dati di compratore e venditore (vista compratore)"""
        # Per il compratore invertiamo l'ordine: prima compratore poi venditore
        elements = []
        styles = getSampleStyleSheet()

        if lang == 'it':
            venditore_label = 'VENDITORE'
            compratore_label = 'COMPRATORE'
        else:
            venditore_label = 'SELLER'
            compratore_label = 'BUYER'

        # Dati compratore
        compratore_info = [
            Paragraph(f"<b>{compratore_label}</b>", styles['Heading3']),
            Paragraph(f"<b>{compratore_data.get('azienda', '')}</b>", styles['Normal'])
        ]

        if compratore_data.get('indirizzo'):
            compratore_info.append(Paragraph(compratore_data.get('indirizzo'), styles['Normal']))

        city_line = []
        if compratore_data.get('cap'):
            city_line.append(compratore_data.get('cap'))
        if compratore_data.get('citta'):
            city_line.append(compratore_data.get('citta'))
        if city_line:
            compratore_info.append(Paragraph(' '.join(city_line), styles['Normal']))

        if compratore_data.get('partita_iva') or compratore_data.get('piva'):
            piva_label = 'P.IVA:' if lang == 'it' else 'VAT:'
            piva = compratore_data.get('partita_iva') or compratore_data.get('piva')
            compratore_info.append(Paragraph(f"{piva_label} {piva}", styles['Normal']))

        if compratore_data.get('telefono'):
            tel_label = 'Tel:' if lang == 'it' else 'Phone:'
            compratore_info.append(Paragraph(f"{tel_label} {compratore_data.get('telefono')}", styles['Normal']))

        # Dati venditore
        venditore_info = [
            Paragraph(f"<b>{venditore_label}</b>", styles['Heading3']),
            Paragraph(f"<b>{venditore_data.get('azienda', '')}</b>", styles['Normal'])
        ]

        if venditore_data.get('indirizzo'):
            venditore_info.append(Paragraph(venditore_data.get('indirizzo'), styles['Normal']))

        city_line = []
        if venditore_data.get('cap'):
            city_line.append(venditore_data.get('cap'))
        if venditore_data.get('citta'):
            city_line.append(venditore_data.get('citta'))
        if city_line:
            venditore_info.append(Paragraph(' '.join(city_line), styles['Normal']))

        if venditore_data.get('partita_iva') or venditore_data.get('piva'):
            piva_label = 'P.IVA:' if lang == 'it' else 'VAT:'
            piva = venditore_data.get('partita_iva') or venditore_data.get('piva')
            venditore_info.append(Paragraph(f"{piva_label} {piva}", styles['Normal']))

        if venditore_data.get('telefono'):
            tel_label = 'Tel:' if lang == 'it' else 'Phone:'
            venditore_info.append(Paragraph(f"{tel_label} {venditore_data.get('telefono')}", styles['Normal']))

        # Tabella con due colonne (compratore a sinistra, venditore a destra)
        parti_data = [[compratore_info, venditore_info]]
        t = Table(parti_data, colWidths=[8.5*cm, 8.5*cm])
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ('LINEAFTER', (0, 0), (0, -1), 1, colors.grey),
        ]))
        elements.append(t)

        return elements

    def _crea_dettagli_articolo(self, articolo_data, conferma_data, lang='it'):
        """Crea la sezione con i dettagli dell'articolo"""
        elements = []

        if lang == 'it':
            headers = ['Articolo', 'Quantità', 'Prezzo Unitario', 'Totale']
        else:
            headers = ['Item', 'Quantity', 'Unit Price', 'Total']

        # Calcola totale
        qta = conferma_data.get('quantita', 0) or conferma_data.get('qta', 0)
        prezzo = conferma_data.get('prezzo', 0)

        try:
            qta_float = float(qta)
            prezzo_float = float(prezzo)
            totale = qta_float * prezzo_float
        except:
            qta_float = 0
            prezzo_float = 0
            totale = 0

        # Nome articolo
        nome_articolo = articolo_data.get('nome', '') or articolo_data.get('nome_articolo', '')

        # Unità di misura
        um = articolo_data.get('unita_misura', '')
        qta_str = f"{qta_float:.2f}" if um else f"{qta_float:.0f}"
        if um:
            qta_str += f" {um}"

        data_rows = [
            headers,
            [
                nome_articolo,
                qta_str,
                self._format_currency(prezzo_float, lang),
                self._format_currency(totale, lang)
            ]
        ]

        # Aggiungi provvigione se presente
        if conferma_data.get('provvigione'):
            prov_label = 'Provvigione' if lang == 'it' else 'Commission'
            prov = conferma_data.get('provvigione')
            data_rows.append([
                prov_label,
                '',
                self._format_currency(prov, lang),
                ''
            ])

        t = Table(data_rows, colWidths=[7*cm, 3.5*cm, 3.5*cm, 3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)

        return elements

    def _crea_date_consegna(self, date_consegna, lang='it'):
        """Crea la sezione con le date di consegna"""
        elements = []
        styles = getSampleStyleSheet()

        if lang == 'it':
            title = Paragraph("<b>Date di Consegna:</b>", styles['Heading3'])
        else:
            title = Paragraph("<b>Delivery Dates:</b>", styles['Heading3'])

        elements.append(title)

        # Prepara i dati per la tabella
        if lang == 'it':
            headers = ['Data', 'Quantità']
        else:
            headers = ['Date', 'Quantity']

        data_rows = [headers]

        for dc in date_consegna:
            data = dc.get('data_consegna', '')
            qta = dc.get('qta_consegna', '')
            data_rows.append([self._format_date(data), str(qta)])

        t = Table(data_rows, colWidths=[8.5*cm, 8.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f0f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)

        return elements

    def _crea_note(self, note, lang='it'):
        """Crea la sezione con le note"""
        elements = []
        styles = getSampleStyleSheet()

        if lang == 'it':
            title = Paragraph("<b>Note:</b>", styles['Heading3'])
        else:
            title = Paragraph("<b>Notes:</b>", styles['Heading3'])

        elements.append(title)
        elements.append(Paragraph(str(note), styles['Normal']))

        return elements

    def _crea_footer(self, lang='it'):
        """Crea il footer del documento"""
        elements = []
        styles = getSampleStyleSheet()

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )

        # Note legali
        if self.company_data.get('note_legali'):
            if lang == 'it':
                note_legali = self.company_data['note_legali'].get('italiano', '')
            else:
                note_legali = self.company_data['note_legali'].get('inglese', '')

            if note_legali:
                elements.append(Paragraph(note_legali, footer_style))

        # Footer documento
        if self.company_data.get('documenti'):
            if lang == 'it':
                footer_text = self.company_data['documenti'].get('conferma_ordine_venditore', {}).get('footer', '')
            else:
                footer_text = "Document automatically generated by GestyBrok"

            if footer_text:
                elements.append(Spacer(1, 0.3*cm))
                elements.append(Paragraph(footer_text, footer_style))

        return elements

    def _crea_messaggio_venditore(self, venditore_data, compratore_data, conferma_data, lang='it'):
        """Crea il messaggio personalizzato per il venditore"""
        elements = []
        styles = getSampleStyleSheet()

        # Stile per il messaggio
        msg_style = ParagraphStyle(
            'MessageStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=10,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#333333')
        )

        # Stile per il riepilogo
        riepilogo_style = ParagraphStyle(
            'RiepilogoStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            leftIndent=20,
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#555555')
        )

        azienda_venditore = venditore_data.get('azienda', '')
        azienda_compratore = compratore_data.get('azienda', '')
        articolo_nome = ''  # Sarà disponibile nel contesto principale
        quantita = conferma_data.get('quantita', 0) or conferma_data.get('qta', 0)

        if lang == 'it':
            # Messaggio in italiano
            saluto = f"<b>Gentile {azienda_venditore},</b>"
            elements.append(Paragraph(saluto, msg_style))

            messaggio = (
                f"con la presente confermiamo l'ordine ricevuto dal cliente <b>{azienda_compratore}</b> "
                f"per i prodotti da Voi forniti. Di seguito il riepilogo completo della transazione:"
            )
            elements.append(Paragraph(messaggio, msg_style))

            elements.append(Spacer(1, 0.3*cm))

            # Riepilogo
            riepilogo_title = Paragraph("<b>RIEPILOGO ORDINE:</b>", msg_style)
            elements.append(riepilogo_title)

        else:
            # Messaggio in inglese
            saluto = f"<b>Dear {azienda_venditore},</b>"
            elements.append(Paragraph(saluto, msg_style))

            messaggio = (
                f"we hereby confirm the order received from the customer <b>{azienda_compratore}</b> "
                f"for the products supplied by you. Below is the complete summary of the transaction:"
            )
            elements.append(Paragraph(messaggio, msg_style))

            elements.append(Spacer(1, 0.3*cm))

            # Riepilogo
            riepilogo_title = Paragraph("<b>ORDER SUMMARY:</b>", msg_style)
            elements.append(riepilogo_title)

        return elements

    def _crea_messaggio_compratore(self, compratore_data, venditore_data, conferma_data, lang='it'):
        """Crea il messaggio personalizzato per il compratore"""
        elements = []
        styles = getSampleStyleSheet()

        # Stile per il messaggio
        msg_style = ParagraphStyle(
            'MessageStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=10,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#333333')
        )

        # Stile per il riepilogo
        riepilogo_style = ParagraphStyle(
            'RiepilogoStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            leftIndent=20,
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#555555')
        )

        azienda_compratore = compratore_data.get('azienda', '')
        azienda_venditore = venditore_data.get('azienda', '')
        quantita = conferma_data.get('quantita', 0) or conferma_data.get('qta', 0)

        if lang == 'it':
            # Messaggio in italiano
            saluto = f"<b>Gentile {azienda_compratore},</b>"
            elements.append(Paragraph(saluto, msg_style))

            messaggio = (
                f"La ringraziamo per la richiesta d'ordine e siamo lieti di confermare "
                f"che abbiamo inoltrato il Vostro ordine al fornitore <b>{azienda_venditore}</b>. "
                f"Di seguito trovate il riepilogo completo della Vostra richiesta:"
            )
            elements.append(Paragraph(messaggio, msg_style))

            elements.append(Spacer(1, 0.3*cm))

            # Riepilogo
            riepilogo_title = Paragraph("<b>RIEPILOGO ORDINE:</b>", msg_style)
            elements.append(riepilogo_title)

        else:
            # Messaggio in inglese
            saluto = f"<b>Dear {azienda_compratore},</b>"
            elements.append(Paragraph(saluto, msg_style))

            messaggio = (
                f"Thank you for your order request. We are pleased to confirm "
                f"that we have forwarded your order to the supplier <b>{azienda_venditore}</b>. "
                f"Below you will find the complete summary of your request:"
            )
            elements.append(Paragraph(messaggio, msg_style))

            elements.append(Spacer(1, 0.3*cm))

            # Riepilogo
            riepilogo_title = Paragraph("<b>ORDER SUMMARY:</b>", msg_style)
            elements.append(riepilogo_title)

        return elements
