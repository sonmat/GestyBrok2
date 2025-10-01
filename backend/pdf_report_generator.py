"""
Generatore PDF per Report Potenziale ed Effettivo
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Optional


class PDFReportGenerator:
    """Genera PDF per report potenziale ed effettivo"""

    def __init__(self):
        self.styles = getSampleStyleSheet()

        # Stile titolo
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=1  # Center
        )

        # Stile sottotitolo
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            spaceAfter=20,
            alignment=1
        )

    def genera_report_potenziale(
        self,
        data_dal: str,
        data_al: str,
        records: List[Dict],
        venditore_nome: Optional[str] = None
    ) -> BytesIO:
        """
        Genera PDF Report Potenziale

        Args:
            data_dal: Data inizio periodo (formato YYYY-MM-DD)
            data_al: Data fine periodo (formato YYYY-MM-DD)
            records: Lista record dal database
            venditore_nome: Nome venditore (opzionale per filtro)
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # Titolo
        title = Paragraph("REPORT POTENZIALE", self.title_style)
        story.append(title)

        # Periodo e filtri
        filtro_text = f"Periodo: {self._format_date(data_dal)} - {self._format_date(data_al)}"
        if venditore_nome:
            filtro_text += f" | Venditore: {venditore_nome}"

        subtitle = Paragraph(filtro_text, self.subtitle_style)
        story.append(subtitle)
        story.append(Spacer(1, 0.5*cm))

        # Tabella dati
        if records:
            table_data = self._build_potenziale_table(records)
            table = self._create_table(table_data, landscape(A4)[0] - 4*cm)
            story.append(table)

            # Totali
            story.append(Spacer(1, 1*cm))
            totali = self._calcola_totali_potenziale(records)
            story.append(self._create_totali_table(totali))
        else:
            story.append(Paragraph("Nessun dato disponibile per il periodo selezionato.", self.styles['Normal']))

        # Footer
        story.append(Spacer(1, 2*cm))
        footer = Paragraph(
            f"Report generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}",
            self.subtitle_style
        )
        story.append(footer)

        doc.build(story)
        buffer.seek(0)
        return buffer

    def genera_report_effettivo(
        self,
        data_dal: str,
        data_al: str,
        records: List[Dict],
        venditore_nome: Optional[str] = None
    ) -> BytesIO:
        """
        Genera PDF Report Effettivo

        Args:
            data_dal: Data inizio periodo (formato YYYY-MM-DD)
            data_al: Data fine periodo (formato YYYY-MM-DD)
            records: Lista record dal database
            venditore_nome: Nome venditore (opzionale per filtro)
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # Titolo
        title = Paragraph("REPORT EFFETTIVO", self.title_style)
        story.append(title)

        # Periodo e filtri
        filtro_text = f"Periodo: {self._format_date(data_dal)} - {self._format_date(data_al)}"
        if venditore_nome:
            filtro_text += f" | Venditore: {venditore_nome}"

        subtitle = Paragraph(filtro_text, self.subtitle_style)
        story.append(subtitle)
        story.append(Spacer(1, 0.5*cm))

        # Tabella dati
        if records:
            table_data = self._build_effettivo_table(records)
            table = self._create_table(table_data, landscape(A4)[0] - 4*cm)
            story.append(table)

            # Totali
            story.append(Spacer(1, 1*cm))
            totali = self._calcola_totali_effettivo(records)
            story.append(self._create_totali_table(totali))
        else:
            story.append(Paragraph("Nessun dato disponibile per il periodo selezionato.", self.styles['Normal']))

        # Footer
        story.append(Spacer(1, 2*cm))
        footer = Paragraph(
            f"Report generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}",
            self.subtitle_style
        )
        story.append(footer)

        doc.build(story)
        buffer.seek(0)
        return buffer

    def _build_potenziale_table(self, records: List[Dict]) -> List[List]:
        """Costruisce dati tabella report potenziale"""
        # Header
        headers = [
            'Compratore', 'Venditore', 'Articolo', 'Tipo',
            'Arrivo', 'Carico', 'Qta', 'Prezzo',
            'Delta', 'Euro', 'Data Consegna', 'Tipologia'
        ]

        table_data = [headers]

        # Righe dati
        for r in records:
            row = [
                r.get('compratore_azienda', '')[:20],
                r.get('venditore_azienda', '')[:20],
                r.get('articolo_nome', '')[:20],
                r.get('articolo_tipologia', '')[:10],
                r.get('arrivo', '')[:10],
                r.get('carico', '')[:10],
                self._format_number(r.get('qta_cons', 0)),
                self._format_currency(r.get('prezzo', 0)),
                self._format_number(r.get('delta', 0)),
                self._format_currency(r.get('euro', 0)),
                self._format_date(r.get('data_consegna', '')),
                r.get('tipologia', '')[:10]
            ]
            table_data.append(row)

        return table_data

    def _build_effettivo_table(self, records: List[Dict]) -> List[List]:
        """Costruisce dati tabella report effettivo"""
        # Header
        headers = [
            'Compratore', 'Venditore', 'Articolo', 'Tipo',
            'Arrivo', 'Carico', 'Qta', 'Prezzo',
            'Delta', 'Euro', 'Data Consegna', 'Tipologia'
        ]

        table_data = [headers]

        # Righe dati
        for r in records:
            row = [
                r.get('compratore_azienda', '')[:20],
                r.get('venditore_azienda', '')[:20],
                r.get('articolo_nome', '')[:20],
                r.get('articolo_tipologia', '')[:10],
                r.get('arrivo', '')[:10],
                r.get('carico', '')[:10],
                self._format_number(r.get('qta', 0)),
                self._format_currency(r.get('prezzo', 0)),
                self._format_number(r.get('delta', 0)),
                self._format_currency(r.get('euro', 0)),
                self._format_date(r.get('data_consegna', '')),
                r.get('tipologia', '')[:10]
            ]
            table_data.append(row)

        return table_data

    def _create_table(self, data: List[List], available_width: float) -> Table:
        """Crea tabella formattata"""
        # Calcola larghezze colonne proporzionali
        col_widths = [
            available_width * 0.12,  # Compratore
            available_width * 0.12,  # Venditore
            available_width * 0.12,  # Articolo
            available_width * 0.08,  # Tipo
            available_width * 0.08,  # Arrivo
            available_width * 0.08,  # Carico
            available_width * 0.06,  # Qta
            available_width * 0.08,  # Prezzo
            available_width * 0.06,  # Delta
            available_width * 0.08,  # Euro
            available_width * 0.08,  # Data
            available_width * 0.04   # Tipologia
        ]

        table = Table(data, colWidths=col_widths, repeatRows=1)

        # Stile tabella
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Dati
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

            # Allineamento numeri a destra
            ('ALIGN', (6, 1), (9, -1), 'RIGHT'),

            # Bordi
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

            # Righe alternate
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))

        return table

    def _create_totali_table(self, totali: Dict) -> Table:
        """Crea tabella con totali"""
        data = [
            ['Totale Quantità:', self._format_number(totali.get('totale_qta', 0))],
            ['Totale Euro:', self._format_currency(totali.get('totale_euro', 0))],
            ['Numero Righe:', str(totali.get('num_righe', 0))]
        ]

        table = Table(data, colWidths=[8*cm, 6*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        return table

    def _calcola_totali_potenziale(self, records: List[Dict]) -> Dict:
        """Calcola totali per report potenziale"""
        totale_qta = sum(float(r.get('qta_cons', 0) or 0) for r in records)
        totale_euro = sum(float(r.get('euro', 0) or 0) for r in records)

        return {
            'totale_qta': totale_qta,
            'totale_euro': totale_euro,
            'num_righe': len(records)
        }

    def _calcola_totali_effettivo(self, records: List[Dict]) -> Dict:
        """Calcola totali per report effettivo"""
        totale_qta = sum(float(r.get('qta', 0) or 0) for r in records)
        totale_euro = sum(float(r.get('euro', 0) or 0) for r in records)

        return {
            'totale_qta': totale_qta,
            'totale_euro': totale_euro,
            'num_righe': len(records)
        }

    def _format_date(self, date_str: str) -> str:
        """Formatta data per visualizzazione"""
        if not date_str:
            return ''

        try:
            # Prova formato YYYY-MM-DD
            if '-' in str(date_str):
                dt = datetime.strptime(str(date_str), '%Y-%m-%d')
                return dt.strftime('%d/%m/%Y')
            # Prova formato DD/MM/YYYY
            elif '/' in str(date_str):
                return str(date_str)
            # Numero intero (timestamp o numero Access)
            else:
                return str(date_str)
        except:
            return str(date_str)

    def _format_currency(self, value) -> str:
        """Formatta valore come valuta"""
        try:
            return f"€ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            return '€ 0,00'

    def _format_number(self, value) -> str:
        """Formatta numero"""
        try:
            return f"{float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            return '0,00'
