"""Receipt PDF generation service"""
import io
import random
from datetime import datetime
from typing import Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from sqlalchemy.orm import Session

from app.repositories.paiement_repository import PaiementRepository
from app.utils.config import Config


class ReceiptService:
    def __init__(self, db: Session):
        self.db = db
        self.config = Config()

    def generate_receipt(self, paiement_id: int) -> Tuple[bytes, str]:
        paiement = PaiementRepository(self.db).get_by_id(paiement_id)
        if not paiement:
            raise ValueError(f"Payment with ID {paiement_id} not found")

        receipt_number = self._generate_receipt_number()
        pdf_content = self._build_pdf(paiement, receipt_number)
        return pdf_content, receipt_number

    def _generate_receipt_number(self) -> str:
        year = datetime.now().year
        sequence = str(random.randint(1, 999999)).zfill(6)
        return f"RCU-{year}-{sequence}"

    def _build_pdf(self, paiement, receipt_number: str) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )

        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=16,
            spaceAfter=20
        )
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=10
        )

        company_name = self.config.get('receipts', 'company_name', default='Gestion Immobilière')
        elements.append(Paragraph(f"<b>{company_name}</b>", title_style))
        elements.append(Spacer(1, 10*mm))

        elements.append(Paragraph("REÇU DE PAIEMENT", header_style))
        elements.append(Spacer(1, 5*mm))

        receipt_data = [
            ['Numéro de reçu:', receipt_number],
            ["Date d'émission:", datetime.now().strftime('%d/%m/%Y %H:%M')],
        ]

        receipt_table = Table(receipt_data, colWidths=[80*mm, 100*mm])
        receipt_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(receipt_table)
        elements.append(Spacer(1, 10*mm))

        tenant = paiement.locataire
        tenant_data = [
            ['Locataire:', f"{tenant.nom}"],
            ['Téléphone:', tenant.telephone or '-'],
            ['Email:', tenant.email or '-'],
        ]

        tenant_table = Table(tenant_data, colWidths=[80*mm, 100*mm])
        tenant_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(tenant_table)
        elements.append(Spacer(1, 10*mm))

        type_label = {
            'LOYER': 'Loyer',
            'CAUTION': 'Caution',
            'PAS_DE_PORTE': 'Pas de porte',
            'AUTRE': 'Autre'
        }.get(paiement.type_paiement.value, paiement.type_paiement.value)

        payment_data = [
            ['Type de paiement:', type_label],
            ['Date de paiement:', paiement.date_paiement.strftime('%d/%m/%Y')],
            ['Montant:', f"{float(paiement.montant_total):,.0f} TND"],
        ]

        if paiement.date_debut_periode and paiement.date_fin_periode:
            payment_data.append([
                'Période:',
                f"{paiement.date_debut_periode.strftime('%d/%m/%Y')} - {paiement.date_fin_periode.strftime('%d/%m/%Y')}"
            ])

        payment_table = Table(payment_data, colWidths=[80*mm, 100*mm])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(payment_table)
        elements.append(Spacer(1, 10*mm))

        contrat = paiement.contrat
        if contrat and contrat.bureaux:
            bureau = contrat.bureaux[0]
            immeuble = bureau.immeuble

            property_data = [
                ['Immeuble:', immeuble.nom if immeuble else '-'],
                ['Adresse:', immeuble.adresse if immeuble else '-'],
                ['Bureau(x):', ', '.join([b.numero for b in contrat.bureaux])],
            ]

            property_table = Table(property_data, colWidths=[80*mm, 100*mm])
            property_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(property_table)
            elements.append(Spacer(1, 20*mm))

        elements.append(Spacer(1, 20*mm))
        elements.append(Paragraph("Signature:", styles['Normal']))
        elements.append(Spacer(1, 5*mm))

        signature_path = self.config.get('receipts', 'signature_path', default='')
        if signature_path:
            try:
                from pathlib import Path
                if Path(signature_path).exists():
                    signature_img = Image(signature_path, width=60*mm, height=30*mm)
                    signature_img.hAlign = 'LEFT'
                    elements.append(signature_img)
                else:
                    elements.append(Paragraph("__________________________", styles['Normal']))
            except Exception:
                elements.append(Paragraph("__________________________", styles['Normal']))
        else:
            elements.append(Paragraph("__________________________", styles['Normal']))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
