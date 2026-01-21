#!/usr/bin/env python
"""
Phase 4 - Grille Rouge/Vert Matricielle dans le Dashboard

Organisation:
- Par Immeuble (section)
- Lignes = Contrats
- Colonnes = Mois (mois actuel au centre: 3 avant, 3 après)
- Vert = Payé, Rouge = Impayé
"""
from datetime import date, datetime
from decimal import Decimal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QScrollArea,
                               QDialog, QDialogButtonBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

from app.database.connection import get_database
from app.models.entities import Immeuble, Bureau, Contrat, Locataire, Paiement


class GrilleRougeVertDialog(QDialog):
    def __init__(self, parent=None, contrat_id=None):
        super().__init__(parent)
        self.parent_view = parent
        self.contrat_id = contrat_id
        self.setWindowTitle("Grille des Paiements")
        self.resize(1000, 700)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.grille_widget = GrilleMatricielleWidget(self)
        layout.addWidget(self.grille_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_data(self):
        self.grille_widget.load_data()


class GrilleMatricielleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Matrice des Paiements")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(30)
        self.content_layout.addStretch()
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        refresh_btn = QPushButton("Actualiser la grille")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.load_data()

    def load_data(self):
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        try:
            db = get_database()

            today = date.today()
            current_month = today.month
            current_year = today.year

            months_to_show = []
            for i in range(-3, 4):
                month = current_month + i
                year = current_year
                while month < 1:
                    month += 12
                    year -= 1
                while month > 12:
                    month -= 12
                    year += 1
                months_to_show.append((year, month))

            with db.session_scope() as session:
                immeuble_list = session.query(Immeuble).all()

                for img in immeuble_list:
                    section = self.create_immeuble_section(img, months_to_show, current_year, current_month)
                    self.content_layout.addWidget(section)

                self.content_layout.addStretch()

        except Exception as e:
            print(f"Erreur load_data: {e}")
            import traceback
            traceback.print_exc()
            
    def create_immeuble_section(self, immeuble, months_to_show, current_year, current_month):
        group = QGroupBox(immeuble.nom)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)

        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        try:
            db = get_database()

            with db.session_scope() as session:
                bureaux = session.query(Bureau).filter(Bureau.immeuble_id == immeuble.id).all()

                if not bureaux:
                    no_contrat = QLabel("Aucun bureau dans cet immeuble")
                    no_contrat.setStyleSheet("color: #7f8c8d; font-style: italic;")
                    layout.addWidget(no_contrat)
                    return group

                contrats_data = session.query(Contrat).filter(
                    Contrat.Locataire_id.in_(
                        session.query(Locataire.id).filter(Locataire.immeuble_id == immeuble.id)
                    )
                ).all()

                if not contrats_data:
                    no_contrat = QLabel("Aucun contrat dans cet immeuble")
                    no_contrat.setStyleSheet("color: #7f8c8d; font-style: italic;")
                    layout.addWidget(no_contrat)
                    return group

                table = QTableWidget()
                table.setColumnCount(len(months_to_show) + 2)
                table.setRowCount(len(contrats_data) + 1)

                headers = ["Contrat", "Locataire"] + [f"{m[0]}\n{m[1]:02d}" for m in months_to_show]
                table.setHorizontalHeaderLabels(headers)

                table.horizontalHeader().setStretchLastSection(False)
                for col in range(table.columnCount()):
                    table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

                table.verticalHeader().setVisible(False)
                table.setShowGrid(True)
                table.setStyleSheet("""
                    QTableWidget {
                        gridline-color: #e0e0e0;
                        background-color: white;
                        border: 1px solid #e0e0e0;
                    }
                    QTableWidget::item {
                        padding: 8px;
                        text-align: center;
                    }
                """)

                table.setRowHeight(0, 35)

                for col, (year, month) in enumerate(months_to_show):
                    is_current = (year == current_year and month == current_month)
                    item = QTableWidgetItem(f"{year}\n{month:02d}")
                    if is_current:
                        item.setBackground(QColor("#f39c12"))
                        item.setForeground(QColor("black"))
                        font = QFont("Arial", 9, QFont.Weight.Bold)
                        item.setFont(font)
                    table.setItem(0, col + 2, item)

                for row, ctr in enumerate(contrats_data, 1):
                    try:
                        ctr_id = ctr.id
                        loc_id = ctr.Locataire_id
                        montant = float(ctr.montant_mensuel) if ctr.montant_mensuel else 0

                        loc = session.query(Locataire).get(loc_id)
                        loc_name = loc.nom if loc else "N/A"

                        paiements = session.query(Paiement).filter(
                            Paiement.contrat_id == ctr_id,
                            Paiement.type_paiement == "loyer"
                        ).all()

                        mois_couverts = set()
                        for p in paiements:
                            date_debut = p.date_debut_periode
                            date_fin = p.date_fin_periode
                            if date_debut is not None and date_fin is not None:
                                current = date_debut
                                while current <= date_fin:
                                    mois_couverts.add((current.year, current.month))
                                    if current.month == 12:
                                        current = date(current.year + 1, 1, 1)
                                    else:
                                        current = date(current.year, current.month + 1, 1)

                        item_id = QTableWidgetItem(f"#{ctr_id}")
                        item_id.setBackground(QColor("#ecf0f1"))
                        item_id.setForeground(QColor("black"))
                        table.setItem(row, 0, item_id)

                        item_loc = QTableWidgetItem(loc_name)
                        item_loc.setBackground(QColor("#f8f9fa"))
                        item_loc.setForeground(QColor("black"))
                        table.setItem(row, 1, item_loc)

                        for col, (year, month) in enumerate(months_to_show):
                            est_paye = (year, month) in mois_couverts

                            cell = QTableWidgetItem()
                            cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                            if est_paye:
                                cell.setBackground(QColor("#2ecc71"))
                                cell.setForeground(QColor("black"))
                                cell.setText("✓")
                            else:
                                cell.setBackground(QColor("#e74c3c"))
                                cell.setForeground(QColor("black"))
                                cell.setText(str(int(montant)))

                            table.setItem(row, col + 2, cell)

                    except Exception as e:
                        print(f"Erreur contrat {ctr_id}: {e}")

        except Exception as e:
            print(f"Erreur create section: {e}")
            return group

        layout.addWidget(table)

        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(30)

        vert_widget = self.create_legend_item("#2ecc71", "Payé")
        legend_layout.addWidget(vert_widget)

        rouge_widget = self.create_legend_item("#e74c3c", "Impayé")
        legend_layout.addWidget(rouge_widget)

        orange_widget = self.create_legend_item("#f39c12", "Mois actuel")
        legend_layout.addWidget(orange_widget)

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        return group
        
    def create_legend_item(self, color, text):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        color_box = QLabel()
        color_box.setFixedSize(20, 20)
        color_box.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
        layout.addWidget(color_box)
        
        label = QLabel(text)
        label.setStyleSheet("font-size: 12px; color: #2c3e50;")
        layout.addWidget(label)
        
        return widget


def integrate_grille_to_dashboard(main_window):
    if hasattr(main_window, 'dashboard'):
        main_window.dashboard.add_grille_section()
