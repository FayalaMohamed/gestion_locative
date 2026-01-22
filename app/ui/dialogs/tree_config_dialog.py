"""Tree configuration dialog for document management"""
from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QLineEdit, QComboBox,
    QDialogButtonBox, QMessageBox, QGroupBox, QFormLayout,
    QSpacerItem, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont


class TreeConfigDialog(QDialog):
    """Dialog for configuring document folder tree structure"""

    config_saved = Signal(str, dict)

    def __init__(self, entity_type: str, existing_config: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.entity_type = entity_type
        self.existing_config = existing_config
        self.setWindowTitle(f"Configuration de l'arborescence - {entity_type.capitalize()}")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setup_ui()
        self.load_existing_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel(f"Définir l'arborescence des dossiers pour {self.entity_type.capitalize()}")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)

        instruction_label = QLabel(
            "Créez la structure de dossiers qui sera utilisée pour organiser les documents.\n"
            "Vous pouvez ajouter des sous-dossiers à chaque niveau."
        )
        instruction_label.setWordWrap(True)
        instruction_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(instruction_label)

        tree_group = QGroupBox("Structure des dossiers")
        tree_layout = QVBoxLayout(tree_group)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Nom du dossier", ""])
        self.tree_widget.setColumnCount(2)
        self.tree_widget.header().setStretchLastSection(False)
        self.tree_widget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #e8f4fd;
            }
        """)
        tree_layout.addWidget(self.tree_widget)

        button_layout = QHBoxLayout()

        add_folder_btn = QPushButton("+ Ajouter un dossier")
        add_folder_btn.clicked.connect(self.add_folder)
        button_layout.addWidget(add_folder_btn)

        add_subfolder_btn = QPushButton("+ Ajouter un sous-dossier")
        add_subfolder_btn.clicked.connect(self.add_subfolder)
        button_layout.addWidget(add_subfolder_btn)

        remove_item_btn = QPushButton("- Supprimer")
        remove_item_btn.clicked.connect(self.remove_item)
        button_layout.addWidget(remove_item_btn)

        button_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        tree_layout.addLayout(button_layout)
        layout.addWidget(tree_group)

        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.load_default_structure()

    def load_default_structure(self):
        default_structures = {
            "immeuble": {"name": "Immeuble", "children": []},
            "bureau": {"name": "Bureau", "children": []},
            "locataire": {"name": "Locataire", "children": []},
            "contrat": {"name": "Contrat", "children": []},
            "paiement": {"name": "Paiement", "children": []}
        }
        if self.entity_type in default_structures:
            self.load_tree_from_dict(default_structures[self.entity_type])

    def load_existing_config(self):
        if self.existing_config:
            self.load_tree_from_dict(self.existing_config)

    def load_tree_from_dict(self, structure: Dict[str, Any]):
        self.tree_widget.clear()
        self._add_tree_items(None, structure)

    def _add_tree_items(self, parent_item, structure: Dict[str, Any]):
        if parent_item:
            item = QTreeWidgetItem(parent_item)
        else:
            item = QTreeWidgetItem(self.tree_widget)
        item.setText(0, structure.get("name", ""))
        item.setData(0, Qt.ItemDataRole.UserRole, structure)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

        for child in structure.get("children", []):
            self._add_tree_items(item, child)

        if not parent_item:
            item.setExpanded(True)

    def add_folder(self):
        current_item = self.tree_widget.currentItem()
        if current_item:
            parent = current_item.parent()
            if parent is None:
                parent = current_item
        else:
            parent = self.tree_widget.topLevelItem(0)
            if not parent:
                return

        new_name = "Nouveau dossier"
        if self._folder_exists_at_level(parent, new_name):
            counter = 1
            while self._folder_exists_at_level(parent, f"Nouveau dossier ({counter})"):
                counter += 1
            new_name = f"Nouveau dossier ({counter})"

        new_item = QTreeWidgetItem(parent)
        new_item.setText(0, new_name)
        new_item.setFlags(new_item.flags() | Qt.ItemFlag.ItemIsEditable)
        parent.addChild(new_item)
        parent.setExpanded(True)
        self.tree_widget.setCurrentItem(new_item)
        
        QTimer.singleShot(0, lambda: self.tree_widget.editItem(new_item, 0))

    def add_subfolder(self):
        current_item = self.tree_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Erreur", "Sélectionnez d'abord un dossier parent.")
            return

        new_name = "Nouveau sous-dossier"
        if self._folder_exists_at_level(current_item, new_name):
            counter = 1
            while self._folder_exists_at_level(current_item, f"Nouveau sous-dossier ({counter})"):
                counter += 1
            new_name = f"Nouveau sous-dossier ({counter})"

        new_item = QTreeWidgetItem(current_item)
        new_item.setText(0, new_name)
        new_item.setFlags(new_item.flags() | Qt.ItemFlag.ItemIsEditable)
        current_item.addChild(new_item)
        current_item.setExpanded(True)
        self.tree_widget.setCurrentItem(new_item)
        
        QTimer.singleShot(0, lambda: self.tree_widget.editItem(new_item, 0))

    def _folder_exists_at_level(self, parent_item: QTreeWidgetItem, name: str) -> bool:
        for i in range(parent_item.childCount()):
            if parent_item.child(i).text(0).lower() == name.lower():
                return True
        return False

    def remove_item(self):
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return

        if current_item.parent() is None:
            QMessageBox.warning(self, "Erreur", "Impossible de supprimer le dossier racine.")
            return

        reply = QMessageBox.question(
            self, "Confirmer",
            f"Supprimer '{current_item.text(0)}' et tous ses sous-dossiers ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            parent = current_item.parent()
            parent.takeChild(parent.indexOfChild(current_item))
            del current_item

    def validate_and_accept(self):
        if self.tree_widget.topLevelItemCount() == 0:
            QMessageBox.warning(self, "Erreur", "L'arborescence ne peut pas être vide.")
            return

        tree_structure = self._build_tree_dict()
        if not tree_structure.get("name"):
            QMessageBox.warning(self, "Erreur", "Le dossier racine doit avoir un nom.")
            return

        duplicates = self._find_duplicate_names()
        if duplicates:
            duplicate_list = "\n".join([f"• {name}" for name in duplicates])
            QMessageBox.warning(
                self, 
                "Noms en double", 
                f"Des dossiers avec le même nom existent à certains niveaux:\n\n{duplicate_list}\n\nVeuillez renommer les dossiers pour qu'ils soient uniques."
            )
            return

        self.config_saved.emit(self.entity_type, tree_structure)
        self.accept()

    def _find_duplicate_names(self) -> List[str]:
        seen_names = {}
        duplicates = set()
        
        def check_item(item: QTreeWidgetItem):
            for i in range(item.childCount()):
                child = item.child(i)
                name = child.text(0)
                if name in seen_names:
                    duplicates.add(name)
                else:
                    seen_names[name] = True
                check_item(child)
        
        root = self.tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            check_item(root.child(i))
        
        return list(duplicates)

    def _build_tree_dict(self) -> Dict[str, Any]:
        root = self.tree_widget.topLevelItem(0)
        if root:
            return self._item_to_dict(root)
        return {"name": self.entity_type, "children": []}

    def _item_to_dict(self, item: QTreeWidgetItem) -> Dict[str, Any]:
        children = []
        for i in range(item.childCount()):
            children.append(self._item_to_dict(item.child(i)))

        return {
            "name": item.text(0),
            "children": children
        }

    def get_tree_structure(self) -> Dict[str, Any]:
        return self._build_tree_dict()
