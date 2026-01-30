#!/usr/bin/env python
"""
Locataire management view
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QMessageBox, QGroupBox,
                               QFormLayout, QGridLayout, QTextEdit, QComboBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from typing import List
from app.ui.views.base_view import BaseView, TableSelectionHelper


class LocataireView(BaseView):
    data_changed = Signal()
    _is_loading = False
    
    def setup_ui(self):
        super().setup_ui()
        
        header_layout = QHBoxLayout()
        
        title = QLabel("Locataires")
        title.setObjectName("view_title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.btn_refresh = QPushButton("Actualiser")
        self.btn_refresh.setStyleSheet("background-color: #ecf0f1; padding: 8px 16px; border: 1px solid #bdc3c7; border-radius: 4px;")
        header_layout.addWidget(self.btn_refresh)
        
        self.layout().addLayout(header_layout)
        
        filter_layout = QHBoxLayout()
        
        self.statut_combo = QComboBox()
        self.statut_combo.addItem("Tous les statuts", None)
        self.statut_combo.addItem("Actifs", "actif")
        self.statut_combo.addItem("Historique", "historique")
        filter_layout.addWidget(self.statut_combo)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher par nom, CIN, email...")
        self.search_edit.setMinimumWidth(300)
        filter_layout.addWidget(self.search_edit)
        
        filter_layout.addStretch()
        
        self.layout().addLayout(filter_layout)
        
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Téléphone", "Email", "CIN", "Raison Sociale", "Statut"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QTableWidget.NoFrame)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        table_layout.addWidget(self.table)
        
        self.layout().addLayout(table_layout)
        
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
        
        buttons_layout.addStretch()
        
        self.btn_configure_tree = QPushButton("⚙️ Configurer arborescence")
        self.btn_configure_tree.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        buttons_layout.addWidget(self.btn_configure_tree)
        
        self.btn_browse_docs = QPushButton("📂 Parcourir documents")
        self.btn_browse_docs.setStyleSheet("background-color: #9b59b6; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        buttons_layout.addWidget(self.btn_browse_docs)
        
        self.layout().addLayout(buttons_layout)
        
    def setup_connections(self):
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_configure_tree.clicked.connect(self.on_configure_tree)
        self.btn_browse_docs.clicked.connect(self.on_browse_documents)
        self.statut_combo.currentIndexChanged.connect(self.load_data)
        self.search_edit.textChanged.connect(self.on_search)
        self.table_helper = TableSelectionHelper(
            self.table, self,
            on_edit_callback=self._on_edit_items,
            on_delete_callback=self._on_delete_items,
            entity_name="locataire"
        )
        self.load_data()
        
    def load_data(self):
        if self._is_loading:
            return
        self._is_loading = True
        try:
            from app.database.connection import get_database
            from app.models.entities import Locataire, StatutLocataire
            from sqlalchemy import or_
            from sqlalchemy.orm import joinedload
            
            db = get_database()
            
            with db.session_scope() as session:
                query = session.query(Locataire).options(joinedload(Locataire.contrats), joinedload(Locataire.paiements))
                
                statut = self.statut_combo.currentData()
                if statut:
                    query = query.filter(Locataire.statut == StatutLocataire[statut.upper()])
                    
                locataires = query.order_by(Locataire.nom).all()
                
                self.table.setRowCount(len(locataires))
                
                for row, loc in enumerate(locataires):
                    self.table.setItem(row, 0, QTableWidgetItem(str(loc.id)))
                    self.table.setItem(row, 1, QTableWidgetItem(loc.nom))
                    self.table.setItem(row, 2, QTableWidgetItem(loc.telephone or ""))
                    self.table.setItem(row, 3, QTableWidgetItem(loc.email or ""))
                    self.table.setItem(row, 4, QTableWidgetItem(loc.cin or ""))
                    self.table.setItem(row, 5, QTableWidgetItem(loc.raison_sociale or ""))
                    self.table.setItem(row, 6, QTableWidgetItem(loc.statut.value))
                    
                    for col in range(7):
                        self.table.item(row, col).setFlags(
                            Qt.ItemIsSelectable | Qt.ItemIsEnabled
                        )
                        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
        finally:
            self._is_loading = False
            
    def on_add(self):
        dialog = LocataireDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
            
    def on_edit(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un locataire")
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        
        dialog = LocataireDialog(self, locataire_id=item_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
            
    def on_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un locataire")
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        
        reply = QMessageBox.question(self, "Confirmation", 
                                    "Êtes-vous sûr de vouloir supprimer ce locataires?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                from app.database.connection import get_database
                from app.models.entities import Locataire, Contrat, Paiement
                from app.repositories.locataire_repository import LocataireRepository
                from sqlalchemy import func
                
                db = get_database()
                with db.session_scope() as session:
                    repo = LocataireRepository(session)
                    loc = repo.get_by_id(item_id)
                    if loc:
                        contrat_count = session.query(func.count(Contrat.id)).filter(Contrat.Locataire_id == item_id).scalar()
                        if contrat_count > 0:
                            QMessageBox.warning(self, "Suppression impossible", 
                                f"Ce locataire a {contrat_count} contrat(s). Supprimez d'abord les contrats associés.")
                            return
                            
                        paiement_count = session.query(func.count(Paiement.id)).filter(Paiement.Locataire_id == item_id).scalar()
                        if paiement_count > 0:
                            QMessageBox.warning(self, "Suppression impossible", 
                                f"Ce locataire a {paiement_count} paiement(s). Supprimez d'abord les paiements associés.")
                            return
                        
                        repo.delete(loc)
                self.load_data()
                self.data_changed.emit()
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    def _on_edit_items(self, item_ids: List[int]):
        """Handle edit action from context menu or keyboard."""
        if len(item_ids) == 1:
            dialog = LocataireDialog(self, locataire_id=item_ids[0])
            if dialog.exec() == QDialog.Accepted:
                self.load_data()
                self.data_changed.emit()
        else:
            QMessageBox.information(self, "Information", 
                "Veuillez sélectionner un seul locataire pour la modification.")

    def _on_delete_items(self, item_ids: List[int]):
        """Handle delete action from context menu or keyboard."""
        if not item_ids:
            return

        count = len(item_ids)
        reply = QMessageBox.question(self, "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer {count} locataire{'s' if count > 1 else ''}?",
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                from app.database.connection import get_database
                from app.models.entities import Locataire, Contrat, Paiement
                from app.repositories.locataire_repository import LocataireRepository
                from sqlalchemy import func

                db = get_database()
                deleted_count = 0
                skipped_count = 0

                with db.session_scope() as session:
                    repo = LocataireRepository(session)

                    for item_id in item_ids:
                        loc = repo.get_by_id(item_id)
                        if loc:
                            contrat_count = session.query(func.count(Contrat.id)).filter(Contrat.Locataire_id == item_id).scalar()
                            if contrat_count > 0:
                                skipped_count += 1
                                continue

                            paiement_count = session.query(func.count(Paiement.id)).filter(Paiement.Locataire_id == item_id).scalar()
                            if paiement_count > 0:
                                skipped_count += 1
                                continue

                            repo.delete(loc)
                            deleted_count += 1

                self.load_data()
                self.data_changed.emit()

                if skipped_count > 0:
                    QMessageBox.warning(self, "Suppression partielle",
                        f"{deleted_count} locataire(s) supprimé(s), {skipped_count} non supprimé(s) car ils ont des contrats ou paiements associés.")

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            
    def on_search(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount() - 1):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
            
    def on_configure_tree(self):
        try:
            from app.database.connection import get_database
            from app.services.document_service import DocumentService
            from app.ui.dialogs.tree_config_dialog import TreeConfigDialog
            
            db = get_database()
            doc_service = DocumentService(db.get_session())
            existing_config = doc_service.get_tree_config("locataire")
            
            dialog = TreeConfigDialog("locataire", existing_config, self)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            
    def on_browse_documents(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un locataire pour consulter ses documents.")
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        item_name = self.table.item(selected[0].row(), 1).text()
        
        self.show_document_browser(item_id, item_name)
        
    def show_document_browser(self, item_id, item_name):
        try:
            from app.database.connection import get_database
            from app.services.document_service import DocumentService
            from app.ui.dialogs.document_browser_dialog import DocumentBrowserDialog
            
            db = get_database()
            doc_service = DocumentService(db.get_session())
            
            dialog = DocumentBrowserDialog(
                entity_type="locataire",
                entity_id=item_id,
                entity_name=f"Locataire: {item_name}",
                doc_service=doc_service,
                parent=self
            )
            
            dialog.exec()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")


from PySide6.QtWidgets import QDialog, QDialogButtonBox


class LocataireDialog(QDialog):
    def __init__(self, parent=None, locataire_id=None):
        super().__init__(parent)
        self.parent_view = parent
        self.locataire_id = locataire_id
        
        if locataire_id:
            self.setWindowTitle("Modifier Locataire")
        else:
            self.setWindowTitle("Nouveau Locataire")
            
        self.resize(550, 500)
        self.setup_ui()
        
        if locataire_id:
            self.load_data()
            
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.nom_edit = QLineEdit()
        form_layout.addRow("Nom*:", self.nom_edit)
        
        self.telephone_edit = QLineEdit()
        form_layout.addRow("Téléphone:", self.telephone_edit)
        
        self.email_edit = QLineEdit()
        form_layout.addRow("Email:", self.email_edit)
        
        self.cin_edit = QLineEdit()
        form_layout.addRow("CIN:", self.cin_edit)
        
        self.raison_sociale_edit = QLineEdit()
        form_layout.addRow("Raison Sociale:", self.raison_sociale_edit)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(120)
        form_layout.addRow("Commentaires:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def load_data(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Locataire
            
            db = get_database()
            with db.session_scope() as session:
                loc = session.query(Locataire).get(self.locataire_id)
                if loc:
                    self.existing_data = loc
                    self.nom_edit.setText(loc.nom)
                    self.telephone_edit.setText(loc.telephone or "")
                    self.email_edit.setText(loc.email or "")
                    self.cin_edit.setText(loc.cin or "")
                    self.raison_sociale_edit.setText(loc.raison_sociale or "")
                    self.notes_edit.setText(loc.commentaires or "")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            
    def validate_and_accept(self):
        nom = self.nom_edit.text().strip()
        
        if not nom:
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return
            
        try:
            from app.database.connection import get_database
            from app.models.entities import Locataire, StatutLocataire
            from app.repositories.locataire_repository import LocataireRepository
            
            db = get_database()
            with db.session_scope() as session:
                repo = LocataireRepository(session)
                if self.locataire_id:
                    loc = repo.get_by_id(self.locataire_id)
                    if loc:
                        repo.update(loc,
                            nom=nom,
                            telephone=self.telephone_edit.text().strip() or None,
                            email=self.email_edit.text().strip() or None,
                            cin=self.cin_edit.text().strip() or None,
                            raison_sociale=self.raison_sociale_edit.text().strip() or None,
                            commentaires=self.notes_edit.toPlainText().strip() or None
                        )
                        
                        active_contrats = session.query(Locataire).filter(
                            Locataire.id == self.locataire_id,
                            Locataire.statut == StatutLocataire.ACTIF
                        ).count()
                        loc.statut = StatutLocataire.ACTIF if active_contrats > 0 else StatutLocataire.HISTORIQUE
                else:
                    repo.create(
                        nom=nom,
                        telephone=self.telephone_edit.text().strip() or None,
                        email=self.email_edit.text().strip() or None,
                        cin=self.cin_edit.text().strip() or None,
                        raison_sociale=self.raison_sociale_edit.text().strip() or None,
                        statut=StatutLocataire.ACTIF,
                        commentaires=self.notes_edit.toPlainText().strip() or None
                    )
                    
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            
    def validate_and_accept(self):
        nom = self.nom_edit.text().strip()
        
        if not nom:
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return
            
        try:
            from app.database.connection import get_database
            from app.models.entities import Locataire, StatutLocataire, Contrat
            from app.repositories.locataire_repository import LocataireRepository
            
            db = get_database()
            with db.session_scope() as session:
                repo = LocataireRepository(session)
                if self.locataire_id:
                    loc = repo.get_by_id(self.locataire_id)
                    if loc:
                        repo.update(loc,
                            nom=nom,
                            telephone=self.telephone_edit.text().strip() or None,
                            email=self.email_edit.text().strip() or None,
                            cin=self.cin_edit.text().strip() or None,
                            raison_sociale=self.raison_sociale_edit.text().strip() or None,
                            commentaires=self.notes_edit.toPlainText().strip() or None
                        )
                        
                        active_contrats = session.query(Contrat).filter(
                            Contrat.Locataire_id == self.locataire_id,
                            Contrat.est_resilie_col == False
                        ).count()
                        loc.statut = StatutLocataire.ACTIF if active_contrats > 0 else StatutLocataire.HISTORIQUE
                else:
                    repo.create(
                        nom=nom,
                        telephone=self.telephone_edit.text().strip() or None,
                        email=self.email_edit.text().strip() or None,
                        cin=self.cin_edit.text().strip() or None,
                        raison_sociale=self.raison_sociale_edit.text().strip() or None,
                        statut=StatutLocataire.ACTIF,
                        commentaires=self.notes_edit.toPlainText().strip() or None
                    )
                    
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
