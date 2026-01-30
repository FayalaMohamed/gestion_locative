#!/usr/bin/env python
"""
Base view class for all entity views
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QComboBox, QDateEdit,
                               QGroupBox, QFormLayout, QGridLayout, QMessageBox,
                               QToolBar, QSpacerItem, QSizePolicy, QMenu, QAbstractItemView)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QIcon, QAction, QKeyEvent
from typing import Optional, List


class BaseView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
        QTimer.singleShot(100, self.setup_connections)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
    def setup_connections(self):
        pass
        
    def load_data(self):
        pass
        
    def refresh(self):
        self.load_data()


class TableSelectionHelper:
    """
    Helper class to enable multi-selection, context menu, and keyboard delete
    for entity table widgets.
    """

    def __init__(self, table: QTableWidget, parent_view: QWidget,
                 on_edit_callback, on_delete_callback, entity_name: str = "élément"):
        """
        Initialize the helper for a table widget.

        Args:
            table: The QTableWidget to enhance
            parent_view: The parent view widget (for showing dialogs)
            on_edit_callback: Function to call when editing (receives list of IDs)
            on_delete_callback: Function to call when deleting (receives list of IDs)
            entity_name: Name of the entity type for messages (e.g., "immeuble")
        """
        self.table = table
        self.parent_view = parent_view
        self.on_edit_callback = on_edit_callback
        self.on_delete_callback = on_delete_callback
        self.entity_name = entity_name

        self._setup_table()
        self._setup_context_menu()
        self._setup_keyboard_shortcuts()

    def _setup_table(self):
        """Configure table for multi-selection."""
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setFocusPolicy(Qt.StrongFocus)

    def _setup_context_menu(self):
        """Setup right-click context menu."""
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard event handling for delete key."""
        self.table.keyPressEvent = self._key_press_event

    def _key_press_event(self, event: QKeyEvent):
        """Handle key press events, especially Delete key."""
        if event.key() == Qt.Key_Delete:
            self._handle_delete()
        else:
            QTableWidget.keyPressEvent(self.table, event)

    def _get_selected_ids(self) -> List[int]:
        """Get list of selected row IDs from the table."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        ids = []
        for row in selected_rows:
            id_item = self.table.item(row, 0)
            if id_item:
                try:
                    ids.append(int(id_item.text()))
                except ValueError:
                    continue
        return ids

    def _show_context_menu(self, position):
        """Show context menu on right-click."""
        selected_ids = self._get_selected_ids()

        if not selected_ids:
            return

        menu = QMenu(self.parent_view)

        if len(selected_ids) == 1:
            edit_action = menu.addAction(f"Modifier {self.entity_name}")
            edit_action.triggered.connect(lambda: self.on_edit_callback(selected_ids))
            menu.addSeparator()

        delete_text = f"Supprimer {len(selected_ids)} {self.entity_name}{'s' if len(selected_ids) > 1 else ''}"
        delete_action = menu.addAction(delete_text)
        delete_action.triggered.connect(lambda: self.on_delete_callback(selected_ids))

        menu.exec(self.table.viewport().mapToGlobal(position))

    def _handle_delete(self):
        """Handle Delete key press."""
        selected_ids = self._get_selected_ids()
        if selected_ids:
            self.on_delete_callback(selected_ids)


def apply_view_stylesheet():
    return """
        QLabel#view_title {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        QLabel#section_title {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 10px;
        }
        
        QWidget#stat_card {
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        QLabel#stat_title {
            color: #7f8c8d;
            font-size: 13px;
        }
        
        QLabel#stat_value {
            color: #2c3e50;
            font-size: 28px;
            font-weight: bold;
        }
        
        QTableWidget#recent_table {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            font-size: 13px;
        }
        
        QTableWidget#recent_table::item {
            padding: 8px 12px;
        }
        
        QTableWidget#recent_table::item:selected {
            background-color: #e8f4fd;
            color: #2c3e50;
        }
        
        QHeaderView::section {
            background-color: #f5f7fa;
            padding: 10px;
            font-weight: bold;
            color: #2c3e50;
            border: none;
            border-bottom: 1px solid #e0e0e0;
        }
        
        QPushButton#primary_button {
            background-color: #3498db;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
        }
        
        QPushButton#primary_button:hover {
            background-color: #2980b9;
        }
        
        QPushButton#secondary_button {
            background-color: #ecf0f1;
            color: #2c3e50;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
        }
        
        QPushButton#secondary_button:hover {
            background-color: #bdc3c7;
        }
        
        QLineEdit, QComboBox, QDateEdit {
            padding: 8px 12px;
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            font-size: 14px;
            background-color: #ffffff;
        }
        
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
            border-color: #3498db;
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
    """
