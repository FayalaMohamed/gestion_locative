#!/usr/bin/env python
"""
Dashboard view for Gestion Locative Pro - Building payment grids
"""
from datetime import date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea, QFrame, QGridLayout,
                               QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.ui.views.base_view import BaseView
from app.models.entities import Paiement, TypePaiement


class DashboardView(BaseView):
    
    def setup_ui(self):
        super().setup_ui()
        
        main_layout = self.layout()
        
        header = QLabel("Tableau de Bord")
        header.setObjectName("view_title")
        main_layout.addWidget(header)
        
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Contrats:"))
        
        self.statut_combo = QComboBox()
        self.statut_combo.addItem("Tous", None)
        self.statut_combo.addItem("Actifs", "actif")
        self.statut_combo.addItem("Résiliés", "resilie")
        self.statut_combo.setStyleSheet("min-width: 150px;")
        filter_layout.addWidget(self.statut_combo)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_area.setMinimumHeight(400)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)
        
    def setup_connections(self):
        self.statut_combo.currentIndexChanged.connect(self.load_data)
        self.load_data()
        
    def load_data(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Immeuble, Contrat, Bureau
            from sqlalchemy.orm import joinedload
            
            while self.content_layout.count():
                item = self.content_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())
            
            db = get_database()
            
            statut_value = self.statut_combo.currentData()
            
            with db.session_scope() as session:
                immeuble_list = session.query(Immeuble).options(
                    joinedload(Immeuble.bureaux).joinedload(Bureau.contrats).joinedload(Contrat.locataire)
                ).order_by(Immeuble.nom).all()
                
                if not immeuble_list:
                    label = QLabel("Aucun immeuble trouvé")
                    label.setStyleSheet("padding: 20px; color: #7f8c8d; font-style: italic;")
                    self.content_layout.addWidget(label)
                else:
                    for img in immeuble_list:
                        card = self.create_card(img, session, statut_value)
                        self.content_layout.addWidget(card)
            
            self.content_layout.addStretch()
            
        except Exception as e:
            print(f"Erreur: {e}")
            import traceback
            traceback.print_exc()
            
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
                
    def create_card(self, immeuble, session, statut_filter=None):
        card = QFrame()
        card.setStyleSheet("background: white; border: 1px solid #bdc3c7; border-radius: 6px;")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel(immeuble.nom)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        if immeuble.adresse:
            addr = QLabel(immeuble.adresse)
            addr.setStyleSheet("font-size: 12px; color: #7f8c8d;")
            layout.addWidget(addr)
        
        contrats = []
        for bureau in immeuble.bureaux:
            for contrat in bureau.contrats:
                if contrat not in contrats:
                    if statut_filter == "actif" and not contrat.est_resilie_col:
                        contrats.append(contrat)
                    elif statut_filter == "resilie" and contrat.est_resilie_col:
                        contrats.append(contrat)
                    elif statut_filter is None:
                        contrats.append(contrat)
        
        if not contrats:
            msg = QLabel("Aucun contrat")
            msg.setStyleSheet("color: #95a5a6; font-style: italic; padding: 10px;")
            layout.addWidget(msg)
            return card
        
        grid = self.create_grid(contrats, session)
        layout.addWidget(grid)
        
        legend = self.create_legend()
        layout.addLayout(legend)
        
        return card
        
    def create_grid(self, contrats, session):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(2)
        
        mois_noms = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jui", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        
        cur = date.today()
        months_to_show = 18
        start_offset = -12
        
        headers = []
        for i in range(months_to_show):
            m = cur.month + start_offset + i
            if m <= 0:
                y, m = cur.year - 1, 12 + m
            elif m > 12:
                y, m = cur.year + 1, m - 12
            else:
                y = cur.year
            headers.append((y, m))
        
        for col, (y, m) in enumerate(headers):
            lbl = QLabel(f"{mois_noms[m-1]} {y}")
            lbl.setStyleSheet("font-size: 10px; color: #7f8c8d;")
            lbl.setAlignment(Qt.AlignCenter)
            grid_layout.addWidget(lbl, 0, col + 1)
        
        grid_layout.addWidget(QLabel("Contrat"), 0, 0)
        
        for row, contrat in enumerate(contrats, 1):
            nums = ", ".join([b.numero for b in contrat.bureaux])
            nom = contrat.locataire.nom if contrat.locataire else "?"
            
            info = QLabel(f"{nums}\n{nom}")
            info.setStyleSheet("font-size: 9px; color: #2c3e50;")
            info.setWordWrap(True)
            grid_layout.addWidget(info, row, 0)
            
            paiements = session.query(Paiement).filter(
                Paiement.contrat_id == contrat.id,
                Paiement.type_paiement == TypePaiement.LOYER
            ).all()
            
            payes = set()
            for p in paiements:
                payes.update(p.get_mois_couverts())
            
            start = contrat.date_debut
            resilie = contrat.est_resilie_col
            date_resil = contrat.date_resiliation
            
            for col, (y, m) in enumerate(headers):
                key = (y, m)
                
                covered = False
                if start:
                    if key >= (start.year, start.month):
                        if resilie and date_resil:
                            if key <= (date_resil.year, date_resil.month):
                                covered = True
                        elif not resilie:
                            covered = True
                
                if key in payes:
                    color = "#2ecc71"
                elif covered:
                    color = "#bdc3c7"
                else:
                    color = "#e74c3c"
                
                cell = QLabel()
                cell.setFixedSize(40, 30)
                cell.setStyleSheet(f"background: {color}; border-radius: 3px;")
                grid_layout.addWidget(cell, row, col + 1)
        
        layout.addLayout(grid_layout)
        return widget
        
    def create_legend(self):
        layout = QHBoxLayout()
        layout.addWidget(self.create_legend_item("#2ecc71", "Payé"))
        layout.addWidget(self.create_legend_item("#bdc3c7", "Non payé"))
        layout.addWidget(self.create_legend_item("#e74c3c", "Non couvert"))
        layout.addStretch()
        return layout
        
    def create_legend_item(self, color, text):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        color_box = QLabel()
        color_box.setFixedSize(16, 16)
        color_box.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
        layout.addWidget(color_box)
        
        label = QLabel(text)
        label.setStyleSheet("font-size: 12px;")
        layout.addWidget(label)
        
        return widget
