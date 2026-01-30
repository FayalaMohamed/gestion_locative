"""Document browser dialog for viewing and managing entity documents"""
import os
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QFrame, QMessageBox, QMenu, QToolBar, QSpacerItem, QSizePolicy,
    QDialogButtonBox, QInputDialog, QLineEdit, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QAction


class DocumentBrowserDialog(QDialog):
    """Dialog for browsing and managing documents for an entity"""
    
    document_opened = Signal(int)
    document_deleted = Signal(int)
    
    def __init__(
        self,
        entity_type: str,
        entity_id: int,
        entity_name: str,
        doc_service,
        parent=None
    ):
        super().__init__(parent)
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.doc_service = doc_service
        
        self.setWindowTitle(f"Documents - {entity_name}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        
        title = QLabel(f"Documents: {self.entity_name}")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        self.btn_upload = QPushButton("+ Ajouter des documents")
        self.btn_upload.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_upload.clicked.connect(self.on_upload)
        header_layout.addWidget(self.btn_upload)
        
        layout.addLayout(header_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)

        folder_label = QLabel("Dossiers")
        folder_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        left_layout.addWidget(folder_label)

        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels(["", ""])
        self.folder_tree.setColumnCount(1)
        self.folder_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.folder_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #f0f0f0;
                border-radius: 4px;
            }
            QTreeWidget::item {
                padding: 6px;
            }
        """)
        self.folder_tree.currentItemChanged.connect(self.on_folder_selected)
        left_layout.addWidget(self.folder_tree)

        content_layout.addWidget(left_panel, 1)

        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)

        doc_header_layout = QHBoxLayout()
        
        self.doc_count_label = QLabel("0 documents")
        self.doc_count_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        doc_header_layout.addWidget(self.doc_count_label)
        
        doc_header_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        right_layout.addLayout(doc_header_layout)

        self.document_list = QListWidget()
        self.document_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.document_list.customContextMenuRequested.connect(self.show_context_menu)
        self.document_list.itemDoubleClicked.connect(self.on_document_double_clicked)
        self.document_list.itemSelectionChanged.connect(self.update_button_states)
        self.document_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e8f4fd;
            }
        """)
        right_layout.addWidget(self.document_list)

        button_layout = QHBoxLayout()

        self.btn_open = QPushButton("📂 Ouvrir")
        self.btn_open.clicked.connect(self.open_selected_document)
        button_layout.addWidget(self.btn_open)

        button_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.btn_rename = QPushButton("✏️ Renommer")
        self.btn_rename.clicked.connect(self.rename_document)
        button_layout.addWidget(self.btn_rename)

        self.btn_delete = QPushButton("🗑️ Supprimer")
        self.btn_delete.clicked.connect(self.delete_selected_document)
        button_layout.addWidget(self.btn_delete)

        right_layout.addLayout(button_layout)

        content_layout.addWidget(right_panel, 2)

        layout.addLayout(content_layout)

        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.current_folder_path = ""
        self.documents: List[Dict[str, Any]] = []
        self.update_button_states()

    def load_data(self):
        self.load_folder_structure()
        self.load_documents()

    def load_folder_structure(self):
        tree_config = self.doc_service.get_tree_config(self.entity_type)
        self.folder_tree.clear()
        
        root_item = QTreeWidgetItem(self.folder_tree)
        root_item.setText(0, "📁 Dossier racine")
        root_item.setData(0, Qt.ItemDataRole.UserRole, {"path": ""})
        root_item.setExpanded(True)
        self.folder_tree.addTopLevelItem(root_item)
        
        self._add_folder_items(root_item, tree_config)

    def _add_folder_items(self, parent_item: Optional[QTreeWidgetItem], structure: Dict[str, Any]):
        for child in structure.get("children", []):
            if parent_item:
                item = QTreeWidgetItem(parent_item)
            else:
                item = QTreeWidgetItem(self.folder_tree)
            item.setText(0, f"📁 {child.get('name', '')}")
            item.setData(0, Qt.ItemDataRole.UserRole, {"path": self._get_storage_path(item)})
            
            if child.get("children"):
                self._add_folder_items(item, child)
            
            if parent_item:
                parent_item.addChild(item)

    def _get_storage_path(self, item: QTreeWidgetItem) -> str:
        path_parts = []
        current = item
        while current:
            text = current.text(0)
            if text == "📁 Dossier racine":
                pass
            else:
                clean_text = text.replace("📁 ", "")
                path_parts.insert(0, clean_text)
            current = current.parent()
        return "/".join(path_parts)

    def on_folder_selected(self, current: Optional[QTreeWidgetItem], previous: Optional[QTreeWidgetItem]):
        if current:
            path = current.data(0, Qt.ItemDataRole.UserRole).get("path", "")
            self.current_folder_path = path
        else:
            self.current_folder_path = ""
        self.load_documents()

    def load_documents(self):
        self.document_list.clear()

        if self.current_folder_path:
            docs = self.doc_service.get_documents_by_folder(
                self.entity_type, self.entity_id, self.current_folder_path
            )
        else:
            docs = self.doc_service.get_documents_for_entity(
                self.entity_type, self.entity_id
            )

        self.documents = docs
        self.doc_count_label.setText(f"{len(docs)} document(s)")

        for doc in docs:
            item = QListWidgetItem()
            icon = self._get_file_icon(doc.get("file_type", ""))
            file_name = doc.get("filename", doc.get("original_name", ""))
            size = doc.get("file_size", 0)
            size_str = self._format_size(size) if size else ""

            item.setText(f"{icon} {file_name} ({size_str})")
            item.setData(Qt.ItemDataRole.UserRole, doc)
            self.document_list.addItem(item)

        self.update_button_states()

    def _get_file_icon(self, file_type: str) -> str:
        icons = {
            "image": "🖼️",
            "document": "📄",
            "archive": "📦",
            "other": "📎"
        }
        return icons.get(file_type, "📎")

    def _format_size(self, size_bytes: float) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes = size_bytes / 1024
        return f"{size_bytes:.1f} TB"

    def update_button_states(self):
        has_selection = bool(self.document_list.selectedItems())
        self.btn_open.setEnabled(has_selection)
        self.btn_rename.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)

    def on_document_double_clicked(self, item: QListWidgetItem):
        doc = item.data(Qt.ItemDataRole.UserRole)
        if doc:
            self._open_document(doc)

    def open_selected_document(self):
        selected = self.document_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un document à ouvrir.")
            return

        doc = selected[0].data(Qt.ItemDataRole.UserRole)
        if doc:
            self._open_document(doc)

    def _open_document(self, doc: Dict[str, Any]):
        file_path = self.doc_service.get_file_path(doc.get("id"))
        if file_path and file_path.exists():
            try:
                if os.name == 'nt':
                    os.startfile(str(file_path))
                else:
                    subprocess.run(['xdg-open', str(file_path)], check=True)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le fichier:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Erreur", "Le fichier n'existe pas ou a été déplacé.")

    def rename_document(self):
        selected = self.document_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un document à renommer.")
            return

        item = selected[0]
        doc = item.data(Qt.ItemDataRole.UserRole)
        current_name = doc.get("filename", doc.get("original_name", ""))
        current_id = doc.get("id")

        new_name, ok = QInputDialog.getText(
            self, "Renommer le document",
            "Nouveau nom:",
            QLineEdit.EchoMode.Normal,
            current_name
        )

        if ok and new_name.strip():
            new_name = new_name.strip()
            if new_name.lower() == current_name.lower():
                return()
                 
            if self._file_exists_in_current_folder(new_name, current_id):
                QMessageBox.warning(self, "Erreur", f"Un fichier nommé '{new_name}' existe déjà dans ce dossier.")
                return
                 
            try:
                # Update both the filename and original_name to maintain consistency
                self.doc_service.rename_document(
                    current_id,
                    new_name
                )
                self.load_documents()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de renommer:\n{str(e)}")

    def _file_exists_in_current_folder(self, filename: str, exclude_id: int) -> bool:
        for doc in self.documents:
            if doc.get("id") != exclude_id:
                if doc.get("original_name", "").lower() == filename.lower() or doc.get("filename", "").lower() == filename.lower():
                    return True
        return False

    def delete_selected_document(self):
        selected = self.document_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un document à supprimer.")
            return

        doc = selected[0].data(Qt.ItemDataRole.UserRole)
        file_name = doc.get("filename", doc.get("original_name", "ce document"))

        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer '{file_name}' ?\nCette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.doc_service.delete_file(doc.get("id")):
                self.document_deleted.emit(doc.get("id"))
                self.load_documents()
                QMessageBox.information(self, "Succès", "Document supprimé avec succès.")
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de supprimer le document.")

    def show_context_menu(self, position):
        menu = QMenu()

        open_action = QAction("📂 Ouvrir", self)
        open_action.triggered.connect(self.open_selected_document)
        menu.addAction(open_action)

        rename_action = QAction("✏️ Renommer", self)
        rename_action.triggered.connect(self.rename_document)
        menu.addAction(rename_action)

        menu.addSeparator()

        delete_action = QAction("🗑️ Supprimer", self)
        delete_action.triggered.connect(self.delete_selected_document)
        menu.addAction(delete_action)

        menu.exec_(self.document_list.mapToGlobal(position))

    def on_upload(self):
        try:
            from app.ui.dialogs.document_upload_dialog import DocumentUploadDialog

            tree_config = self.doc_service.get_tree_config(self.entity_type)

            dialog = DocumentUploadDialog(
                entity_type=self.entity_type,
                entity_id=self.entity_id,
                entity_name=self.entity_name,
                tree_config=tree_config,
                parent=self
            )

            dialog.files_uploaded.connect(self.handle_files_uploaded)

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    def handle_files_uploaded(self, entity_type, entity_id, folder_path, file_paths):
        try:
            self.doc_service.upload_files(entity_type, entity_id, folder_path, file_paths)
            self.load_documents()
            QMessageBox.information(self, "Succès", "Document(s) téléversé(s) avec succès!")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du téléversement: {str(e)}")

    def refresh(self):
        self.load_data()
