#!/usr/bin/env python
"""
Base view class for all entity views
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QComboBox, QDateEdit,
                               QGroupBox, QFormLayout, QGridLayout, QMessageBox,
                               QToolBar, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QIcon, QAction


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
