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
                               QLabel)
from PySide6.QtCore import Qt, QTimer

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
        self.setup_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
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
        
        for name in ["Tableau de Bord", "Immeubles", "Bureaux", "Locataires", "Contrats", "Paiements", "Historique", "Paramètres"]:
            item = QListWidgetItem(name)
            self.sidebar.addItem(item)
            
        layout.addWidget(self.sidebar)
        
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
        
    def refresh_dashboard(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
