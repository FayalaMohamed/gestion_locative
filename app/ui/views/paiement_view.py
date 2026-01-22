#!/usr/bin/env python
"""
Paiement management view
"""
import calendar
import os
from datetime import date

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QMessageBox, QGroupBox,
                               QFormLayout, QGridLayout, QTextEdit, QComboBox,
                               QDateEdit, QDoubleSpinBox, QSpinBox, QFileDialog)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QColor

from app.ui.views.base_view import BaseView
from app.services.receipt_service import ReceiptService
from app.services.audit_service import AuditService


class PaiementView(BaseView):
    data_changed = Signal()
    _is_loading = False
    
    def setup_ui(self):
        super().setup_ui()
        
        header_layout = QHBoxLayout()
        
        title = QLabel("Paiements")
        title.setObjectName("view_title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.btn_refresh = QPushButton("Actualiser")
        self.btn_refresh.setStyleSheet("background-color: #ecf0f1; padding: 8px 16px; border: 1px solid #bdc3c7; border-radius: 4px;")
        header_layout.addWidget(self.btn_refresh)
        
        self.layout().addLayout(header_layout)
        
        filter_layout = QHBoxLayout()
        
        self.contrat_combo = QComboBox()
        self.contrat_combo.setMinimumWidth(200)
        self.contrat_combo.addItem("Tous les contrats", None)
        filter_layout.addWidget(self.contrat_combo)
        
        self.type_combo = QComboBox()
        self.type_combo.addItem("Tous les types", None)
        filter_layout.addWidget(self.type_combo)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher...")
        self.search_edit.setMinimumWidth(200)
        filter_layout.addWidget(self.search_edit)
        
        filter_layout.addStretch()
        
        self.layout().addLayout(filter_layout)
        
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Locataire", "Contrat", "Type", "Montant", "Date", "Période", "Commentaire"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QTableWidget.NoFrame)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        table_layout.addWidget(self.table)
        
        self.layout().addLayout(table_layout)
        
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        
        self.layout().addLayout(totals_layout)
        
        buttons_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("Ajouter")
        self.btn_add.setStyleSheet("background-color: #3498db; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        buttons_layout.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("Modifier")
        self.btn_edit.setStyleSheet("background-color: #ecf0f1; padding: 8px 16px; border: 1px solid #bdc3c7; border-radius: 4px;")
        buttons_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        buttons_layout.addWidget(self.btn_delete)
        
        self.btn_receipt = QPushButton("Générer Reçu")
        self.btn_receipt.setStyleSheet("background-color: #ecf0f1; padding: 8px 16px; border: 1px solid #bdc3c7; border-radius: 4px;")
        buttons_layout.addWidget(self.btn_receipt)
        
        buttons_layout.addStretch()
        
        self.layout().addLayout(buttons_layout)
        
    def setup_connections(self):
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_receipt.clicked.connect(self.on_receipt)
        self.contrat_combo.currentIndexChanged.connect(self.load_data)
        self.type_combo.currentIndexChanged.connect(self.load_data)
        self.search_edit.textChanged.connect(self.on_search)
        self.load_contrats()
        self.load_data()
        

    def load_data(self):
        if self._is_loading:
            return
        self._is_loading = True
        try:
            from app.database.connection import get_database
            from app.models.entities import Paiement, Locataire, Contrat, TypePaiement
            from sqlalchemy import or_
            from sqlalchemy.orm import joinedload
            
            db = get_database()
            
            with db.session_scope() as session:
                query = session.query(Paiement).options(joinedload(Paiement.locataire), joinedload(Paiement.contrat)).join(Locataire).outerjoin(Contrat)
                
                contrat_id = self.contrat_combo.currentData()
                if contrat_id:
                    query = query.filter(Paiement.contrat_id == contrat_id)
                    
                type_paiement = self.type_combo.currentData()
                if type_paiement is not None:
                    query = query.filter(Paiement.type_paiement == TypePaiement[type_paiement])
                    
                paiements = query.order_by(Paiement.date_paiement.desc()).all()
                
                self.table.setRowCount(len(paiements))
                
                total = 0
                
                for row, p in enumerate(paiements):
                    self.table.setItem(row, 0, QTableWidgetItem(str(p.id)))
                    self.table.setItem(row, 1, QTableWidgetItem(p.locataire.nom if p.locataire else "N/A"))
                    self.table.setItem(row, 2, QTableWidgetItem(f"#{p.contrat_id}" if p.contrat_id else "N/A"))
                    
                    type_str = p.type_paiement.value if p.type_paiement else "N/A"
                    self.table.setItem(row, 3, QTableWidgetItem(type_str))
                    
                    self.table.setItem(row, 4, QTableWidgetItem(f"{p.montant_total} TND"))
                    total += float(p.montant_total or 0)
                    
                    self.table.setItem(row, 5, QTableWidgetItem(str(p.date_paiement)))
                    
                    periode = ""
                    if p.date_debut_periode and p.date_fin_periode:
                        periode = f"{p.date_debut_periode} au {p.date_fin_periode}"
                    self.table.setItem(row, 6, QTableWidgetItem(periode))
                    
                    self.table.setItem(row, 7, QTableWidgetItem(p.commentaire or ""))
                    
                    for col in range(8):
                        self.table.item(row, col).setFlags(
                            Qt.ItemIsSelectable | Qt.ItemIsEnabled
                        )
                                        
                self.load_contrats()
                self.load_types()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
        finally:
            self._is_loading = False
            
    def load_contrats(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Contrat
            from sqlalchemy.orm import joinedload
            
            db = get_database()
            with db.session_scope() as session:
                contrats = session.query(Contrat).options(
                    joinedload(Contrat.locataire),
                    joinedload(Contrat.bureaux)
                ).order_by(Contrat.date_debut.desc()).all()
                
                current_data = self.contrat_combo.currentData()
                self.contrat_combo.blockSignals(True)
                self.contrat_combo.clear()
                self.contrat_combo.addItem("Tous les contrats", None)
                
                for ctr in contrats:
                    loc_name = ctr.locataire.nom if ctr.locataire else "N/A"
                    bureaux_nums = ", ".join([b.numero for b in ctr.bureaux]) if ctr.bureaux else "N/A"
                    display_text = f"#{ctr.id} - {loc_name} (Bureaux: {bureaux_nums})"
                    self.contrat_combo.addItem(display_text, ctr.id)
                    
                if current_data is not None:
                    idx = self.contrat_combo.findData(current_data)
                    if idx >= 0:
                        self.contrat_combo.setCurrentIndex(idx)
                self.contrat_combo.blockSignals(False)
                        
        except Exception as e:
            print(f"Erreur: {e}")
            
    def load_types(self):
        if self.type_combo.count() <= 1:
            from app.models.entities import TypePaiement
            for tp in TypePaiement:
                self.type_combo.addItem(tp.value, tp.name)
                
    def on_add(self):
        dialog = PaiementDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
            
    def on_edit(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un paiement")
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        
        dialog = PaiementDialog(self, paiement_id=item_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
            
    def on_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un paiement")
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        
        reply = QMessageBox.question(self, "Confirmation", 
                                    "Êtes-vous sûr de vouloir supprimer ce paiement?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                from app.database.connection import get_database
                from app.models.entities import Paiement
                
                db = get_database()
                with db.session_scope() as session:
                    p = session.query(Paiement).get(item_id)
                    if p:
                        session.delete(p)
                self.load_data()
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
                
    def on_receipt(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un paiement")
            return

        paiement_id = int(self.table.item(selected[0].row(), 0).text())

        try:
            from app.database.connection import get_database
            db = get_database()
            with db.session_scope() as session:
                service = ReceiptService(session)
                pdf_content, receipt_number = service.generate_receipt(paiement_id)

                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Enregistrer le reçu PDF",
                    os.path.join(os.path.expanduser("~"), "Downloads", f"recu_{receipt_number}.pdf"),
                    "Fichiers PDF (*.pdf)"
                )

                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(pdf_content)
                    AuditService.log_receipt(session, paiement_id, receipt_number, file_path)
                    QMessageBox.information(
                        self,
                        "Succès",
                        f"Reçu enregistré avec succès:\n{file_path}"
                    )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la génération du reçu:\n{str(e)}"
            )
            
    def on_search(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)


from PySide6.QtWidgets import QDialog, QDialogButtonBox


class PaiementDialog(QDialog):
    def __init__(self, parent=None, paiement_id=None):
        super().__init__(parent)
        self.parent_view = parent
        self.paiement_id = paiement_id
        
        if paiement_id:
            self.setWindowTitle("Modifier Paiement")
        else:
            self.setWindowTitle("Nouveau Paiement")
            
        self.resize(550, 450)
        self.setup_ui()
        
        if paiement_id:
            self.load_data()
            
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.locataire_combo = QComboBox()
        self.locataire_combo.setEditable(True)
        self.locataire_combo.setInsertPolicy(QComboBox.NoInsert)
        self.locataire_combo.setMinimumWidth(200)
        self.load_locataires()
        form_layout.addRow("Locataire*:", self.locataire_combo)
        
        self.contrat_combo = QComboBox()
        self.contrat_combo.addItem("", None)
        form_layout.addRow("Contrat*:", self.contrat_combo)
        
        self.type_combo = QComboBox()
        from app.models.entities import TypePaiement
        for tp in TypePaiement:
            self.type_combo.addItem(tp.value, tp.name)
        form_layout.addRow("Type*:", self.type_combo)
        
        self.montant = QDoubleSpinBox()
        self.montant.setMinimum(0)
        self.montant.setMaximum(10000000)
        self.montant.setSuffix(" TND")
        self.montant.setDecimals(3)
        form_layout.addRow("Montant*:", self.montant)
        
        self.date_paiement = QDateEdit()
        self.date_paiement.setCalendarPopup(True)
        self.date_paiement.setDate(QDate.currentDate())
        form_layout.addRow("Date paiement*:", self.date_paiement)
        
        self.periode_group = QGroupBox("Période du loyer (pour loyer uniquement)")
        periode_layout = QFormLayout()
        
        self.mois_debut_combo = QComboBox()
        mois_list = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                     "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        for i, mois in enumerate(mois_list, 1):
            self.mois_debut_combo.addItem(mois, i)
        current_month = QDate.currentDate().month()
        self.mois_debut_combo.setCurrentIndex(current_month - 1)
        periode_layout.addRow("Mois début:", self.mois_debut_combo)
        
        self.annee_debut_spin = QSpinBox()
        self.annee_debut_spin.setMinimum(2000)
        self.annee_debut_spin.setMaximum(2100)
        self.annee_debut_spin.setValue(QDate.currentDate().year())
        periode_layout.addRow("Année début:", self.annee_debut_spin)
        
        self.mois_fin_combo = QComboBox()
        for i, mois in enumerate(mois_list, 1):
            self.mois_fin_combo.addItem(mois, i)
        self.mois_fin_combo.setCurrentIndex(current_month - 1)
        periode_layout.addRow("Mois fin:", self.mois_fin_combo)
        
        self.annee_fin_spin = QSpinBox()
        self.annee_fin_spin.setMinimum(2000)
        self.annee_fin_spin.setMaximum(2100)
        self.annee_fin_spin.setValue(QDate.currentDate().year())
        periode_layout.addRow("Année fin:", self.annee_fin_spin)
        
        self.periode_group.setLayout(periode_layout)
        form_layout.addRow(self.periode_group)
        
        self.commentaire_edit = QTextEdit()
        self.commentaire_edit.setMaximumHeight(80)
        form_layout.addRow("Commentaire:", self.commentaire_edit)
        
        layout.addLayout(form_layout)
        
        layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.locataire_combo.currentIndexChanged.connect(self.on_locataire_changed)
        self.load_contrats()
        
    def load_locataires(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Locataire
            
            db = get_database()
            with db.session_scope() as session:
                locs = session.query(Locataire).all()
                
                self.locataire_combo.clear()
                self.locataire_combo.addItem("", None)
                
                for loc in locs:
                    self.locataire_combo.addItem(f"{loc.nom}", loc.id)
                    
        except Exception as e:
            print(f"Erreur: {e}")
            
    def on_locataire_changed(self):
        loc_id = self.locataire_combo.currentData()
        if loc_id is None:
            loc_id = self.locataire_combo.itemData(self.locataire_combo.currentIndex())
        if loc_id:
            self.load_contrats()
            
    def load_contrats(self):
        loc_id = self.locataire_combo.currentData()
        if loc_id is None:
            loc_id = self.locataire_combo.itemData(self.locataire_combo.currentIndex())
        if not loc_id:
            self.contrat_combo.clear()
            self.contrat_combo.addItem("", None)
            return
            
        try:
            from app.database.connection import get_database
            from app.models.entities import Contrat
            
            db = get_database()
            with db.session_scope() as session:
                contrats = session.query(Contrat).filter(
                    Contrat.Locataire_id == loc_id,
                    Contrat.est_resilie_col == False
                ).all()
                
                current_data = self.contrat_combo.currentData()
                self.contrat_combo.clear()
                self.contrat_combo.addItem("", None)
                
                for ctr in contrats:
                    self.contrat_combo.addItem(f"#{ctr.id} - {ctr.date_debut}", ctr.id)
                    
                if current_data is not None:
                    idx = self.contrat_combo.findData(current_data)
                    if idx >= 0:
                        self.contrat_combo.setCurrentIndex(idx)
                        
        except Exception as e:
            print(f"Erreur: {e}")
            
    def load_data(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Paiement, TypePaiement
            
            db = get_database()
            with db.session_scope() as session:
                p = session.query(Paiement).get(self.paiement_id)
                if p:
                    loc_id = p.Locataire_id
                    idx = self.locataire_combo.findData(loc_id)
                    if idx >= 0:
                        self.locataire_combo.setCurrentIndex(idx)
                        self.load_contrats()
                        
                    contrat_id = p.contrat_id
                    idx = self.contrat_combo.findData(contrat_id)
                    if idx >= 0:
                        self.contrat_combo.setCurrentIndex(idx)
                        
                    idx = self.type_combo.findData(p.type_paiement.name if p.type_paiement else None)
                    if idx >= 0:
                        self.type_combo.setCurrentIndex(idx)
                        
                    self.montant.setValue(float(p.montant_total or 0))
                    self.date_paiement.setDate(p.date_paiement)
                    
                    if p.date_debut_periode:
                        self.mois_debut_combo.setCurrentIndex(p.date_debut_periode.month - 1)
                        self.annee_debut_spin.setValue(p.date_debut_periode.year)
                    if p.date_fin_periode:
                        self.mois_fin_combo.setCurrentIndex(p.date_fin_periode.month - 1)
                        self.annee_fin_spin.setValue(p.date_fin_periode.year)
                        
                    self.commentaire_edit.setText(p.commentaire or "")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            
    def validate_and_accept(self):
        from app.models.entities import TypePaiement
        
        loc_id = self.locataire_combo.currentData()
        if loc_id is None:
            loc_id = self.locataire_combo.itemData(self.locataire_combo.currentIndex())
        contrat_id = self.contrat_combo.currentData()
        if contrat_id is None:
            contrat_id = self.contrat_combo.itemData(self.contrat_combo.currentIndex())
        
        if loc_id is None:
            QMessageBox.warning(self, "Validation", "Le locataire est obligatoire")
            return
            
        if contrat_id is None:
            QMessageBox.warning(self, "Validation", "Le contrat est obligatoire")
            return
            
        type_paiement = TypePaiement[self.type_combo.currentData()]
        montant = self.montant.value()
        
        if montant <= 0:
            QMessageBox.warning(self, "Validation", "Le montant doit être positif")
            return
            
        try:
            from app.database.connection import get_database
            from app.models.entities import Paiement
            
            db = get_database()
            with db.session_scope() as session:
                if self.paiement_id:
                    p = session.query(Paiement).get(self.paiement_id)
                    if p:
                        p.Locataire_id = loc_id
                        p.contrat_id = contrat_id
                        p.type_paiement = type_paiement
                        p.montant_total = montant
                        p.date_paiement = self.date_paiement.date().toPython()
                        
                        if type_paiement == TypePaiement.LOYER:
                            mois_debut = self.mois_debut_combo.currentData()
                            annee_debut = self.annee_debut_spin.value()
                            p.date_debut_periode = date(annee_debut, mois_debut, 1)
                            
                            mois_fin = self.mois_fin_combo.currentData()
                            annee_fin = self.annee_fin_spin.value()
                            last_day = calendar.monthrange(annee_fin, mois_fin)[1]
                            p.date_fin_periode = date(annee_fin, mois_fin, last_day)
                        else:
                            p.date_debut_periode = None
                            p.date_fin_periode = None
                            
                        p.commentaire = self.commentaire_edit.toPlainText().strip() or None
                else:
                    p = Paiement(
                        Locataire_id=loc_id,
                        contrat_id=contrat_id,
                        type_paiement=type_paiement,
                        montant_total=montant,
                        date_paiement=self.date_paiement.date().toPython(),
                        date_debut_periode=None,
                        date_fin_periode=None,
                        commentaire=self.commentaire_edit.toPlainText().strip() or None
                    )
                    if type_paiement == TypePaiement.LOYER:
                        mois_debut = self.mois_debut_combo.currentData()
                        annee_debut = self.annee_debut_spin.value()
                        p.date_debut_periode = date(annee_debut, mois_debut, 1)
                        
                        mois_fin = self.mois_fin_combo.currentData()
                        annee_fin = self.annee_fin_spin.value()
                        last_day = calendar.monthrange(annee_fin, mois_fin)[1]
                        p.date_fin_periode = date(annee_fin, mois_fin, last_day)
                    session.add(p)
                    
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
