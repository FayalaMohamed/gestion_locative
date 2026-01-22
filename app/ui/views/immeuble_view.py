#!/usr/bin/env python
"""
Immeuble management view
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QMessageBox, QGroupBox,
                               QFormLayout, QGridLayout, QSpinBox, QTextEdit,
                               QSplitter, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.ui.views.base_view import BaseView


class ImmeubleView(BaseView):
    data_changed = Signal()
    
    def setup_ui(self):
        super().setup_ui()
        
        header_layout = QHBoxLayout()
        
        title = QLabel("Immeubles")
        title.setObjectName("view_title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.btn_refresh = QPushButton("Actualiser")
        self.btn_refresh.setStyleSheet("background-color: #ecf0f1; padding: 8px 16px; border: 1px solid #bdc3c7; border-radius: 4px;")
        header_layout.addWidget(self.btn_refresh)
        
        self.layout().addLayout(header_layout)
        
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher un immeuble...")
        self.search_edit.setMinimumWidth(300)
        search_layout.addWidget(self.search_edit)
        
        search_layout.addStretch()
        
        self.layout().addLayout(search_layout)
        
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Adresse", "Bureaux", "Notes"])
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
        self.search_edit.textChanged.connect(self.on_search)
        self.load_data()
        
    def load_data(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Immeuble, Bureau
            from sqlalchemy import func
            
            db = get_database()
            
            with db.session_scope() as session:
                immeubles = session.query(Immeuble).all()
                
                self.table.setRowCount(len(immeubles))
                
                for row, img in enumerate(immeubles):
                    bureau_count = session.query(func.count(Bureau.id)).filter(Bureau.immeuble_id == img.id).scalar()
                    
                    self.table.setItem(row, 0, QTableWidgetItem(str(img.id)))
                    self.table.setItem(row, 1, QTableWidgetItem(img.nom))
                    self.table.setItem(row, 2, QTableWidgetItem(img.adresse or ""))
                    self.table.setItem(row, 3, QTableWidgetItem(str(bureau_count)))
                    self.table.setItem(row, 4, QTableWidgetItem(img.notes or ""))
                    
                    for col in range(5):
                        self.table.item(row, col).setFlags(
                            Qt.ItemIsSelectable | Qt.ItemIsEnabled
                        )
                        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {str(e)}")
            
    def on_add(self):
        dialog = ImmeubleDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
            
    def on_edit(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un immeuble")
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        
        dialog = ImmeubleDialog(self, item_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
            
    def on_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un immeuble")
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        
        reply = QMessageBox.question(self, "Confirmation", 
                                    "Êtes-vous sûr de vouloir supprimer cet immeuble?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                from app.database.connection import get_database
                from app.models.entities import Bureau
                from app.repositories.immeuble_repository import ImmeubleRepository
                from sqlalchemy import func
                
                db = get_database()
                with db.session_scope() as session:
                    repo = ImmeubleRepository(session)
                    img = repo.get_by_id(item_id)
                    if img:
                        bureau_count = session.query(func.count(Bureau.id)).filter(Bureau.immeuble_id == item_id).scalar()
                        
                        if bureau_count > 0:
                            QMessageBox.warning(self, "Suppression impossible", 
                                f"Cet immeuble contient {bureau_count} bureau(x). Supprimez d'abord les bureaux associés.")
                            return
                        
                        repo.delete(img)
                    self.load_data()
                    self.data_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
            
    def on_search(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount() - 1):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
            
    def on_browse_documents(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un immeuble pour consulter ses documents.")
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        item_name = self.table.item(selected[0].row(), 1).text()
        
        self.show_document_browser(item_id, item_name)
        
    def on_configure_tree(self):
        try:
            from app.database.connection import get_database
            from app.services.document_service import DocumentService
            from app.ui.dialogs.tree_config_dialog import TreeConfigDialog
            
            db = get_database()
            doc_service = DocumentService(db.get_session())
            existing_config = doc_service.get_tree_config("immeuble")
            
            dialog = TreeConfigDialog("immeuble", existing_config, self)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            
    def show_document_browser(self, item_id, item_name):
        try:
            from app.database.connection import get_database
            from app.services.document_service import DocumentService
            from app.ui.dialogs.document_browser_dialog import DocumentBrowserDialog
            
            db = get_database()
            doc_service = DocumentService(db.get_session())
            
            dialog = DocumentBrowserDialog(
                entity_type="immeuble",
                entity_id=item_id,
                entity_name=f"Immeuble: {item_name}",
                doc_service=doc_service,
                parent=self
            )
            
            dialog.exec()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")


from PySide6.QtWidgets import QDialog, QDialogButtonBox


class ImmeubleDialog(QDialog):
    def __init__(self, parent=None, immeuble_id=None):
        super().__init__(parent)
        self.parent_view = parent
        self.immeuble_id = immeuble_id
        self.existing_data = None
        
        if immeuble_id:
            self.setWindowTitle("Modifier Immeuble")
        else:
            self.setWindowTitle("Nouvel Immeuble")
            
        self.resize(500, 400)
        self.setup_ui()
        
        if immeuble_id:
            self.load_data()
            
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.nom_edit = QLineEdit()
        form_layout.addRow("Nom*:", self.nom_edit)
        
        self.adresse_edit = QLineEdit()
        form_layout.addRow("Adresse:", self.adresse_edit)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def load_data(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Immeuble
            
            db = get_database()
            with db.session_scope() as session:
                img = session.query(Immeuble).get(self.immeuble_id)
                if img:
                    self.existing_data = img
                    self.nom_edit.setText(img.nom)
                    self.adresse_edit.setText(img.adresse or "")
                    self.notes_edit.setText(img.notes or "")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            
    def validate_and_accept(self):
        nom = self.nom_edit.text().strip()
        
        if not nom:
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return
            
        try:
            from app.database.connection import get_database
            from app.models.entities import Immeuble
            from app.repositories.immeuble_repository import ImmeubleRepository
            
            db = get_database()
            with db.session_scope() as session:
                repo = ImmeubleRepository(session)
                if self.immeuble_id:
                    img = repo.get_by_id(self.immeuble_id)
                    if img:
                        repo.update(img,
                            nom=nom,
                            adresse=self.adresse_edit.text().strip() or None,
                            notes=self.notes_edit.toPlainText().strip() or None
                        )
                else:
                    repo.create(
                        nom=nom,
                        adresse=self.adresse_edit.text().strip() or None,
                        notes=self.notes_edit.toPlainText().strip() or None
                    )
                    
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
