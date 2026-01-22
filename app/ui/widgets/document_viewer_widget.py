"""Document viewer widget for displaying and managing entity documents"""
import os
import subprocess
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QFrame, QMessageBox, QMenu, QToolBar, QSpacerItem, QSizePolicy,
    QSplitter
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QAction


class DocumentViewerWidget(QWidget):
    """Widget for viewing and managing documents for an entity"""

    document_opened = Signal(int)
    document_deleted = Signal(int)
    refresh_requested = Signal()

    def __init__(
        self,
        entity_type: str,
        entity_id: int,
        entity_name: str,
        parent=None
    ):
        super().__init__(parent)
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.doc_service = None
        self.current_folder_path = ""
        self.documents: List[Dict[str, Any]] = []

        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

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
        folder_label.setFont(QFont("Arial", 11, QFont.Bold))
        left_layout.addWidget(folder_label)

        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels(["", "Documents"])
        self.folder_tree.setColumnCount(2)
        self.folder_tree.header().setSectionResizeMode(0, QTreeWidget.ResizeMode.Fixed)
        self.folder_tree.header().setSectionResizeMode(1, QTreeWidget.ResizeMode.Stretch)
        self.folder_tree.setColumnWidth(0, 30)
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

        layout.addWidget(left_panel, 1)

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

        header_layout = QHBoxLayout()

        self.doc_count_label = QLabel("0 documents")
        self.doc_count_label.setFont(QFont("Arial", 11, QFont.Bold))
        header_layout.addWidget(self.doc_count_label)

        header_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.search_bar = QLabel("🔍")
        header_layout.addWidget(self.search_bar)

        right_layout.addLayout(header_layout)

        self.document_list = QListWidget()
        self.document_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.document_list.customContextMenuRequested.connect(self.show_context_menu)
        self.document_list.itemDoubleClicked.connect(self.on_document_double_clicked)
        right_layout.addWidget(self.document_list)

        button_layout = QHBoxLayout()

        open_btn = QPushButton("📂 Ouvrir")
        open_btn.clicked.connect(self.open_selected_document)
        button_layout.addWidget(open_btn)

        button_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        delete_btn = QPushButton("🗑️ Supprimer")
        delete_btn.clicked.connect(self.delete_selected_document)
        button_layout.addWidget(delete_btn)

        right_layout.addLayout(button_layout)

        layout.addWidget(right_panel, 2)

    def set_document_service(self, doc_service):
        """Set the document service instance"""
        self.doc_service = doc_service
        self.load_structure()
        self.load_documents()

    def load_structure(self):
        """Load and display the folder structure"""
        if not self.doc_service:
            return

        tree_config = self.doc_service.get_tree_config(self.entity_type)
        self.folder_tree.clear()
        self._add_folder_items(None, tree_config)

    def _add_folder_items(self, parent_item: Optional[QTreeWidgetItem], structure: Dict[str, Any]):
        item = QTreeWidgetItem(parent_item)
        item.setText(0, "📁")
        item.setText(1, structure.get("name", ""))
        item.setData(0, Qt.ItemDataRole.UserRole, {"path": self._get_storage_path(item)})
        item.setData(1, Qt.ItemDataRole.UserRole, structure)

        folder_count = self._count_subfolders(structure)
        if folder_count > 0:
            item.setText(0, f"📁")

        for child in structure.get("children", []):
            self._add_folder_items(item, child)

        if parent_item:
            parent_item.addChild(item)
        else:
            self.folder_tree.addTopLevelItem(item)
            item.setExpanded(True)

    def _get_storage_path(self, item: QTreeWidgetItem) -> str:
        path_parts = []
        current = item
        while current:
            path_parts.insert(0, current.text(1))
            current = current.parent()
        return "/".join(path_parts[1:])

    def _count_subfolders(self, structure: Dict[str, Any]) -> int:
        count = len(structure.get("children", []))
        for child in structure.get("children", []):
            count += self._count_subfolders(child)
        return count

    def on_folder_selected(self, current: Optional[QTreeWidgetItem], previous: Optional[QTreeWidgetItem]):
        if current:
            path = current.data(0, Qt.ItemDataRole.UserRole).get("path", "")
            self.current_folder_path = path
            self.load_documents()

    def load_documents(self):
        """Load documents for the current folder"""
        if not self.doc_service:
            return

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
            file_name = doc.get("original_name", doc.get("filename", ""))
            size = doc.get("file_size", 0)
            size_str = self._format_size(size) if size else ""

            item.setText(f"{icon} {file_name} ({size_str})")
            item.setData(Qt.ItemDataRole.UserRole, doc)
            self.document_list.addItem(item)

    def _get_file_icon(self, file_type: str) -> str:
        icons = {
            "image": "🖼️",
            "document": "📄",
            "archive": "📦",
            "other": "📎"
        }
        return icons.get(file_type, "📎")

    def _format_size(self, size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def on_document_double_clicked(self, item: QListWidgetItem):
        """Open document on double click"""
        doc = item.data(Qt.ItemDataRole.UserRole)
        if doc:
            self._open_document(doc)

    def open_selected_document(self):
        """Open the currently selected document"""
        selected = self.document_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un document à ouvrir.")
            return

        doc = selected[0].data(Qt.ItemDataRole.UserRole)
        if doc:
            self._open_document(doc)

    def _open_document(self, doc: Dict[str, Any]):
        """Open a document with the default system application"""
        if not self.doc_service:
            return

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

    def delete_selected_document(self):
        """Delete the selected document"""
        selected = self.document_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un document à supprimer.")
            return

        doc = selected[0].data(Qt.ItemDataRole.UserRole)
        file_name = doc.get("original_name", "ce document")

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
        """Show context menu for document list"""
        menu = QMenu()

        open_action = QAction("📂 Ouvrir", self)
        open_action.triggered.connect(self.open_selected_document)
        menu.addAction(open_action)

        menu.addSeparator()

        delete_action = QAction("🗑️ Supprimer", self)
        delete_action.triggered.connect(self.delete_selected_document)
        menu.addAction(delete_action)

        menu.exec_(self.document_list.mapToGlobal(position))

    def refresh(self):
        """Refresh the document list"""
        self.load_structure()
        self.load_documents()
