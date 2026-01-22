#!/usr/bin/env python
"""
Gestion Locative Pro - Application
Run: python main.py
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget,
                               QLabel, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap

from pathlib import Path

from app.ui.views.dashboard_view import DashboardView
from app.ui.views.immeuble_view import ImmeubleView
from app.ui.views.bureau_view import BureauView
from app.ui.views.locataire_view import LocataireView
from app.ui.views.contrat_view import ContratView
from app.ui.views.paiement_view import PaiementView
from app.ui.views.audit_view import AuditView
from app.ui.views.settings_view import SettingsView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Locative Pro")
        self.setMinimumSize(1200, 800)
        
        icon_path = Path(__file__).parent / "app" / "ui" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.setup_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                border: none;
            }
            QListWidget::item {
                color: #bdc3c7;
                padding: 12px 20px;
            }
            QListWidget::item:selected {
                background-color: #34495e;
                color: white;
                border-left: 3px solid #3498db;
            }
        """)
        
        for name in ["Tableau de Bord", "Immeubles", "Bureaux", "Locataires", "Contrats", "Paiements"]:
            item = QListWidgetItem(name)
            self.sidebar.addItem(item)
        
        sidebar_layout.addWidget(self.sidebar)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #34495e; max-height: 1px;")
        separator.setFixedHeight(1)
        sidebar_layout.addWidget(separator)
        
        self.sidebar_bottom = QListWidget()
        self.sidebar_bottom.setFixedWidth(200)
        self.sidebar_bottom.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                border: none;
            }
            QListWidget::item {
                color: #95a5a6;
                padding: 12px 20px;
            }
            QListWidget::item:selected {
                background-color: #34495e;
                color: white;
                border-left: 3px solid #9b59b6;
            }
        """)
        
        for name in ["Historique", "Paramètres"]:
            item = QListWidgetItem(name)
            self.sidebar_bottom.addItem(item)
        
        sidebar_layout.addWidget(self.sidebar_bottom)
        
        layout.addLayout(sidebar_layout)
        
        self.content = QStackedWidget()
        layout.addWidget(self.content)
        
        self.dashboard = DashboardView()
        self.content.addWidget(self.dashboard)
        self.content.addWidget(ImmeubleView())
        self.content.addWidget(BureauView())
        self.content.addWidget(LocataireView())
        self.content.addWidget(ContratView())
        self.content.addWidget(PaiementView())
        self.content.addWidget(AuditView())
        self.content.addWidget(SettingsView())
        
        self.sidebar.currentRowChanged.connect(self.content.setCurrentIndex)
        self.sidebar_bottom.currentRowChanged.connect(lambda row: self.content.setCurrentIndex(6 + row))
        
    def refresh_dashboard(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
