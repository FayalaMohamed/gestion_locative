"""Document upload dialog with tree navigation"""
import os
from typing import Dict, Any, List, Optional, Tuple
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QLineEdit, QComboBox,
    QDialogButtonBox, QMessageBox, QGroupBox, QFormLayout,
    QListWidget, QListWidgetItem, QProgressBar, QFrame,
    QSpacerItem, QSizePolicy, QFileDialog, QScrollArea, QWidget,
    QHeaderView
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QDragEnterEvent, QDropEvent


class DocumentUploadDialog(QDialog):
    """Dialog for uploading documents with tree folder selection"""

    files_uploaded = Signal(str, int, str, list)

    def __init__(
        self,
        entity_type: str,
        entity_id: int,
        entity_name: str,
        tree_config: Dict[str, Any],
        parent=None
    ):
        super().__init__(parent)
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.tree_config = tree_config
        self.uploaded_files: List[Dict[str, Any]] = []

        self.setWindowTitle(f"Téléverser des documents - {entity_name}")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        self.setup_ui()
        self.build_folder_tree()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()

        title_label = QLabel(f"Téléverser des documents pour {self.entity_name}")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        layout.addLayout(header_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        folder_group = QGroupBox("Sélectionner le dossier de destination")
        folder_layout = QVBoxLayout(folder_group)
        folder_layout.setContentsMargins(10, 15, 10, 10)

        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels(["Dossier"])
        self.folder_tree.setColumnCount(1)
        self.folder_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.folder_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #e8f4fd;
            }
        """)
        self.folder_tree.currentItemChanged.connect(self.on_folder_selected)
        folder_layout.addWidget(self.folder_tree)

        self.selected_folder_label = QLabel("<b>Dossier:</b> <span style='color: #7f8c8d;'>-</span>")
        self.selected_folder_label.setStyleSheet("padding: 8px; background-color: #ecf0f1; border-radius: 4px;")
        folder_layout.addWidget(self.selected_folder_label)

        content_layout.addWidget(folder_group, 1)

        files_group = QGroupBox("Fichiers à téléverser")
        files_layout = QVBoxLayout(files_group)
        files_layout.setContentsMargins(10, 15, 10, 10)

        drop_area = QLabel()
        drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_area.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 2px dashed #3498db;
                border-radius: 8px;
                min-height: 100px;
                color: #7f8c8d;
                font-size: 14px;
            }
            QLabel:hover {
                background-color: #f8f9fa;
                border-color: #2980b9;
            }
        """)
        drop_area.setText("Glissez-déposez vos fichiers ici\nou cliquez sur 'Parcourir'")
        drop_area.setAcceptDrops(True)
        drop_area.mousePressEvent = lambda e: self.browse_files()
        drop_area.dragEnterEvent = self.drag_enter_event
        drop_area.dropEvent = self.drop_event
        files_layout.addWidget(drop_area)

        browse_btn = QPushButton("Parcourir les fichiers...")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        browse_btn.clicked.connect(self.browse_files)
        files_layout.addWidget(browse_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin-top: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0;
            }
        """)
        self.file_list.setMinimumHeight(150)
        files_layout.addWidget(self.file_list)

        files_button_layout = QHBoxLayout()

        clear_btn = QPushButton("Tout effacer")
        clear_btn.clicked.connect(self.clear_file_list)
        files_button_layout.addWidget(clear_btn)

        files_button_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        remove_selected_btn = QPushButton("Supprimer la sélection")
        remove_selected_btn.clicked.connect(self.remove_selected_files)
        files_button_layout.addWidget(remove_selected_btn)

        files_layout.addLayout(files_button_layout)

        content_layout.addWidget(files_group, 2)

        layout.addLayout(content_layout)

        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        layout.addWidget(self.progress_bar)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Téléverser")
        self.ok_button.setEnabled(False)
        layout.addWidget(button_box)

        self.current_folder_path = ""

    def build_folder_tree(self):
        self.folder_tree.clear()
        
        root_item = QTreeWidgetItem(self.folder_tree)
        root_item.setText(0, "📁 Dossier racine")
        root_item.setData(0, Qt.ItemDataRole.UserRole, {"path": ""})
        root_item.setExpanded(True)
        self.folder_tree.addTopLevelItem(root_item)
        
        self._add_folder_items(root_item, self.tree_config)

    def _add_folder_items(self, parent_item: QTreeWidgetItem, structure: Dict[str, Any]):
        for child in structure.get("children", []):
            item = QTreeWidgetItem(parent_item)
            item.setText(0, f"📁 {child.get('name', '')}")
            item.setData(0, Qt.ItemDataRole.UserRole, {"path": self._get_storage_path(item)})
            
            if child.get("children"):
                self._add_folder_items(item, child)

            parent_item.addChild(item)

    def _get_storage_path(self, item: QTreeWidgetItem) -> str:
        path_parts = []
        current = item
        while current:
            text = current.text(0).replace("📁 ", "")
            if text != "Dossier racine":
                path_parts.insert(0, text)
            current = current.parent()
        return "/".join(path_parts)

    def on_folder_selected(self, current: Optional[QTreeWidgetItem], previous: Optional[QTreeWidgetItem]):
        if current:
            self.current_folder_path = current.data(0, Qt.ItemDataRole.UserRole).get("path", "")
            display_path = self.current_folder_path if self.current_folder_path else "Dossier racine"
            self.selected_folder_label.setText(
                f"<b>Dossier:</b> <span style='color: #3498db;'>{display_path}</span>"
            )
            self.update_ok_button_state()
        else:
            self.current_folder_path = ""
            self.selected_folder_label.setText("<b>Dossier:</b> <span style='color: #e74c3c;'>-</span>")
            self.update_ok_button_state()

    def update_ok_button_state(self):
        folder_item = self.folder_tree.currentItem()
        has_folder = folder_item is not None
        has_files = self.file_list.count() > 0
        self.ok_button.setEnabled(has_folder and has_files)

    def drag_enter_event(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def drop_event(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    files.append(file_path)
        if files:
            self.add_files(files)
            event.acceptProposedAction()

    def browse_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner les fichiers",
            "",
            "Tous les fichiers (*);;Documents PDF (*.pdf);;Images (*.png *.jpg *.jpeg);;Fichiers Excel (*.xlsx *.xls);;Fichiers Word (*.docx *.doc)"
        )
        if file_paths:
            self.add_files(file_paths)

    def add_files(self, file_paths: List[str]):
        for file_path in file_paths:
            if not self._file_already_added(file_path):
                file_info = os.path.basename(file_path)
                if self._file_exists_in_destination(file_info):
                    QMessageBox.warning(
                        self, 
                        "Fichier existant", 
                        f"Le fichier '{file_info}' existe déjà dans ce dossier."
                    )
                    continue
                    
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, file_path)

                file_size = os.path.getsize(file_path)
                size_str = self._format_size(file_size)

                item.setText(f"📄 {file_info} ({size_str})")
                item.setToolTip(file_path)

                self.file_list.addItem(item)
        self.update_ok_button_state()

    def _file_exists_in_destination(self, filename: str) -> bool:
        folder_item = self.folder_tree.currentItem()
        
        if not folder_item:
            return False

        folder_path = folder_item.data(0, Qt.ItemDataRole.UserRole).get("path", "")
        
        try:
            from app.database.connection import get_database
            from app.services.document_service import DocumentService
            
            db = get_database()
            doc_service = DocumentService(db.get_session())
            
            docs = doc_service.get_documents_by_folder(
                self.entity_type, 
                self.entity_id, 
                folder_path
            )
            
            for doc in docs:
                if doc.get("original_name", "").lower() == filename.lower():
                    return True
                    
            return False
        except Exception:
            return False

    def _file_already_added(self, file_path: str) -> bool:
        for i in range(self.file_list.count()):
            if self.file_list.item(i).data(Qt.ItemDataRole.UserRole) == file_path:
                return True
        return False

    def _format_size(self, size_bytes: float) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes = size_bytes / 1024
        return f"{size_bytes:.1f} TB"

    def clear_file_list(self):
        self.file_list.clear()
        self.update_ok_button_state()

    def remove_selected_files(self):
        for item in self.file_list.selectedItems():
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
        self.update_ok_button_state()

    def validate_and_accept(self):
        folder_item = self.folder_tree.currentItem()
        
        if not folder_item:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un dossier de destination.")
            return

        self.current_folder_path = folder_item.data(0, Qt.ItemDataRole.UserRole).get("path", "")

        if self.file_list.count() == 0:
            QMessageBox.warning(self, "Erreur", "Veuillez ajouter au moins un fichier.")
            return

        file_paths = []
        for i in range(self.file_list.count()):
            file_paths.append(self.file_list.item(i).data(Qt.ItemDataRole.UserRole))

        self.files_uploaded.emit(self.entity_type, self.entity_id, self.current_folder_path, file_paths)
        self.accept()

    def get_uploaded_files(self) -> List[Dict[str, Any]]:
        return self.uploaded_files
