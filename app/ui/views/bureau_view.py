#!/usr/bin/env python
"""
Simplified Bureau management view
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QMessageBox,
                               QFormLayout, QComboBox, QDoubleSpinBox, QSpinBox,
                               QTextEdit, QDialog, QDialogButtonBox, QGridLayout)
from PySide6.QtCore import Qt
from sqlalchemy import func
from app.models.entities import contrat_bureau
from app.ui.views.base_view import TableSelectionHelper
from typing import List


class BureauView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
        self.setup_connections()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        title = QLabel("Bureaux")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.btn_refresh = QPushButton("Actualiser")
        self.btn_refresh.setStyleSheet("background-color: #ecf0f1; padding: 8px 16px; border: 1px solid #bdc3c7; border-radius: 4px;")
        header_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(header_layout)
        
        filter_layout = QHBoxLayout()
        
        self.immeuble_combo = QComboBox()
        self.immeuble_combo.setMinimumWidth(200)
        self.immeuble_combo.addItem("Tous les immeubles", None)
        filter_layout.addWidget(self.immeuble_combo)
        
        self.disponible_combo = QComboBox()
        self.disponible_combo.addItem("Tous", None)
        self.disponible_combo.addItem("Disponibles", True)
        self.disponible_combo.addItem("Occupés", False)
        filter_layout.addWidget(self.disponible_combo)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Numéro", "Immeuble", "Étage", "Surface", "Disponible", "Notes"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
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
        layout.addLayout(buttons_layout)
        
    def setup_connections(self):
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_configure_tree.clicked.connect(self.on_configure_tree)
        self.btn_browse_docs.clicked.connect(self.on_browse_documents)
        self.immeuble_combo.currentIndexChanged.connect(self.load_data)
        self.disponible_combo.currentIndexChanged.connect(self.load_data)

        self.table_helper = TableSelectionHelper(
            self.table, self,
            on_edit_callback=self._on_edit_items,
            on_delete_callback=self._on_delete_items,
            entity_name="bureau"
        )

        self.load_immeubles()
        self.load_data()
        
    def load_data(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Bureau, Immeuble, Contrat
            from sqlalchemy.orm import joinedload
            
            db = get_database()
            
            with db.session_scope() as session:
                query = session.query(Bureau).outerjoin(Immeuble)
                
                immeuble_id = self.immeuble_combo.currentData()
                if immeuble_id is not None:
                    query = query.filter(Bureau.immeuble_id == immeuble_id)
                    
                disponible = self.disponible_combo.currentData()
                if disponible is not None:
                    if disponible:
                        query = query.filter(~Bureau.contrats.any(Contrat.est_resilie_col == False))
                    else:
                        query = query.filter(Bureau.contrats.any(Contrat.est_resilie_col == False))
                    
                bureaux = query.order_by(Bureau.numero).all()
                
                self.table.setRowCount(len(bureaux))
                
                for row, bur in enumerate(bureaux):
                    self.table.setItem(row, 0, QTableWidgetItem(str(bur.id)))
                    self.table.setItem(row, 1, QTableWidgetItem(f"#{bur.numero}"))
                    img_name = bur.immeuble.nom if bur.immeuble else "N/A"
                    self.table.setItem(row, 2, QTableWidgetItem(img_name))
                    self.table.setItem(row, 3, QTableWidgetItem(bur.etage or ""))
                    self.table.setItem(row, 4, QTableWidgetItem(f"{bur.surface_m2} m²" if bur.surface_m2 else ""))
                    
                    est_disponible = not any(c.est_resilie_col == False for c in bur.contrats)
                    self.table.setItem(row, 5, QTableWidgetItem("Oui" if est_disponible else "Non"))
                    self.table.setItem(row, 6, QTableWidgetItem(bur.notes or ""))
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            
    def load_immeubles(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Immeuble
            
            db = get_database()
            with db.session_scope() as session:
                immeubles = session.query(Immeuble).all()
                self.immeuble_combo.clear()
                self.immeuble_combo.addItem("Tous les immeubles", None)
                for img in immeubles:
                    self.immeuble_combo.addItem(img.nom, img.id)
        except Exception as e:
            print(f"Erreur: {e}")
            
    def on_add(self):
        dialog = BureauDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_immeubles()
            self.load_data()
            
    def on_edit(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un bureau")
            return
        item_id = int(self.table.item(selected[0].row(), 0).text())
        dialog = BureauDialog(self, item_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            
    def on_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un bureau")
            return
        item_id = int(self.table.item(selected[0].row(), 0).text())
        reply = QMessageBox.question(self, "Confirmation", "Supprimer?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                from app.database.connection import get_database
                from app.models.entities import Bureau, Contrat
                from app.repositories.bureau_repository import BureauRepository
                db = get_database()
                with db.session_scope() as session:
                    repo = BureauRepository(session)
                    bur = repo.get_by_id(item_id)
                    if bur:
                        contrat_count = session.query(func.count(Contrat.id)).join(contrat_bureau).filter(contrat_bureau.c.bureau_id == item_id).scalar()
                        if contrat_count > 0:
                            QMessageBox.warning(self, "Suppression impossible", 
                                "Ce bureau est lié à un ou plusieurs contrats. Résiliez d'abord les contrats associés.")
                            return
                        repo.delete(bur)
                self.load_immeubles()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def _on_edit_items(self, item_ids: List[int]):
        """Handle edit action from context menu or keyboard."""
        if len(item_ids) == 1:
            dialog = BureauDialog(self, item_ids[0])
            if dialog.exec() == QDialog.Accepted:
                self.load_data()
        else:
            QMessageBox.information(self, "Information",
                "Veuillez sélectionner un seul bureau pour la modification.")

    def _on_delete_items(self, item_ids: List[int]):
        """Handle delete action from context menu or keyboard."""
        if not item_ids:
            return

        count = len(item_ids)
        reply = QMessageBox.question(self, "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer {count} bureau{'x' if count > 1 else ''}?",
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                from app.database.connection import get_database
                from app.models.entities import Contrat
                from app.repositories.bureau_repository import BureauRepository

                db = get_database()
                deleted_count = 0
                skipped_count = 0

                with db.session_scope() as session:
                    repo = BureauRepository(session)

                    for item_id in item_ids:
                        bur = repo.get_by_id(item_id)
                        if bur:
                            contrat_count = session.query(func.count(Contrat.id)).join(contrat_bureau).filter(contrat_bureau.c.bureau_id == item_id).scalar()

                            if contrat_count > 0:
                                skipped_count += 1
                                continue

                            repo.delete(bur)
                            deleted_count += 1

                self.load_immeubles()
                self.load_data()

                if skipped_count > 0:
                    QMessageBox.warning(self, "Suppression partielle",
                        f"{deleted_count} bureau(s) supprimé(s), {skipped_count} non supprimé(s) car ils sont liés à des contrats.")

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")

    def on_configure_tree(self):
        try:
            from app.database.connection import get_database
            from app.services.document_service import DocumentService
            from app.ui.dialogs.tree_config_dialog import TreeConfigDialog

            db = get_database()
            with db.session_scope() as session:
                doc_service = DocumentService(session)
                existing_config = doc_service.get_tree_config("bureau")

                dialog = TreeConfigDialog("bureau", existing_config, self)
                # Connect the save signal to actually save the configuration
                dialog.config_saved.connect(
                    lambda entity_type, tree_structure: doc_service.save_tree_config(entity_type, tree_structure)
                )
                dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            
    def on_browse_documents(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un bureau pour consulter ses documents.")
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        item_name = f"Bureau #{self.table.item(selected[0].row(), 1).text()}"
        
        self.show_document_browser(item_id, item_name)
        
    def show_document_browser(self, item_id, item_name):
        try:
            from app.database.connection import get_database
            from app.services.document_service import DocumentService
            from app.ui.dialogs.document_browser_dialog import DocumentBrowserDialog
            
            db = get_database()
            doc_service = DocumentService(db.get_session())
            
            dialog = DocumentBrowserDialog(
                entity_type="bureau",
                entity_id=item_id,
                entity_name=item_name,
                doc_service=doc_service,
                parent=self
            )
            
            dialog.exec()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")


class BureauDialog(QDialog):
    def __init__(self, parent=None, bureau_id=None):
        super().__init__(parent)
        self.parent_view = parent
        self.bureau_id = bureau_id
        self.setWindowTitle("Modifier Bureau" if bureau_id else "Nouveau Bureau")
        self.resize(450, 400)
        self.setup_ui()
        self.load_immeubles()
        if bureau_id:
            self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(15)
        
        self.immeuble_combo = QComboBox()
        form.addRow("Immeuble*:", self.immeuble_combo)
        
        self.numero_edit = QLineEdit()
        self.numero_edit.setPlaceholderText("Ex: B2.1, 101, A-5")
        form.addRow("Numéro*:", self.numero_edit)
        
        self.etage_edit = QLineEdit()
        form.addRow("Étage:", self.etage_edit)
        
        self.surface_spin = QDoubleSpinBox()
        self.surface_spin.setMinimum(0)
        self.surface_spin.setMaximum(10000)
        self.surface_spin.setSuffix(" m²")
        self.surface_spin.setDecimals(1)
        form.addRow("Surface:", self.surface_spin)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        form.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form)
        layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def load_immeubles(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Immeuble
            db = get_database()
            with db.session_scope() as session:
                immeubles = session.query(Immeuble).all()
                self.immeuble_combo.clear()
                self.immeuble_combo.addItem("", None)
                for img in immeubles:
                    self.immeuble_combo.addItem(img.nom, img.id)
        except Exception as e:
            print(f"Erreur: {e}")
            
    def load_data(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Bureau
            db = get_database()
            with db.session_scope() as session:
                bur = session.query(Bureau).get(self.bureau_id)
                if bur:
                    idx = self.immeuble_combo.findData(bur.immeuble_id)
                    if idx >= 0:
                        self.immeuble_combo.setCurrentIndex(idx)
                    self.numero_edit.setText(bur.numero or "")
                    self.etage_edit.setText(bur.etage or "")
                    self.surface_spin.setValue(bur.surface_m2 or 0)
                    self.notes_edit.setText(bur.notes or "")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
            
    def validate(self):
        if self.immeuble_combo.currentData() is None:
            QMessageBox.warning(self, "Validation", "Immeuble obligatoire")
            return
        
        numero_text = self.numero_edit.text().strip()
        if not numero_text:
            QMessageBox.warning(self, "Validation", "Numéro de bureau obligatoire")
            return
        
        try:
            from app.database.connection import get_database
            from app.models.entities import Bureau
            from app.repositories.bureau_repository import BureauRepository
            db = get_database()
            with db.session_scope() as session:
                repo = BureauRepository(session)
                if self.bureau_id:
                    bur = repo.get_by_id(self.bureau_id)
                    if bur:
                        repo.update(bur,
                            immeuble_id=self.immeuble_combo.currentData(),
                            numero=numero_text,
                            etage=self.etage_edit.text().strip() or None,
                            surface_m2=self.surface_spin.value(),
                            notes=self.notes_edit.toPlainText().strip() or None
                        )
                else:
                    repo.create(
                        immeuble_id=self.immeuble_combo.currentData(),
                        numero=numero_text,
                        etage=self.etage_edit.text().strip() or None,
                        surface_m2=self.surface_spin.value(),
                        notes=self.notes_edit.toPlainText().strip() or None
                    )
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
