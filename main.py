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
        separator.setFrameShape(QFrame.Shape.HLine)
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
        self.dashboard = DashboardView()
        self.content.addWidget(self.dashboard)
        
        self.immeuble_view = ImmeubleView()
        self.content.addWidget(self.immeuble_view)
        
        self.bureau_view = BureauView()
        self.content.addWidget(self.bureau_view)
        
        self.locataire_view = LocataireView()
        self.content.addWidget(self.locataire_view)
        
        self.contrat_view = ContratView()
        self.content.addWidget(self.contrat_view)
        
        self.paiement_view = PaiementView()
        self.content.addWidget(self.paiement_view)
        
        self.audit_view = AuditView()
        self.content.addWidget(self.audit_view)
        
        self.settings_view = SettingsView()
        self.content.addWidget(self.settings_view)
        
        # Connect data changed signals to auto-refresh
        self.immeuble_view.data_changed.connect(self.refresh_current_view)
        self.locataire_view.data_changed.connect(self.refresh_current_view)
        self.contrat_view.data_changed.connect(self.refresh_current_view)
        self.paiement_view.data_changed.connect(self.refresh_current_view)
        # Also connect payment changes to refresh contract details specifically
        self.paiement_view.data_changed.connect(self.contrat_view.refresh_current_contract_details)
        
        self.sidebar.currentRowChanged.connect(self._on_sidebar_changed)
        self.sidebar_bottom.currentRowChanged.connect(self._on_bottom_sidebar_changed)
        
    def _on_sidebar_changed(self, row):
        """Handle main sidebar selection change"""
        # Only process if a valid row is selected
        if row >= 0:
            # Clear bottom sidebar selection without triggering its signal
            self.sidebar_bottom.blockSignals(True)
            self.sidebar_bottom.setCurrentRow(-1)
            self.sidebar_bottom.blockSignals(False)
            # Navigate to the selected page
            self.content.setCurrentIndex(row)
            self.refresh_current_view()
    
    def _on_bottom_sidebar_changed(self, row):
        """Handle bottom sidebar selection change"""
        # Only process if a valid row is selected
        if row >= 0:
            # Clear main sidebar selection without triggering its signal
            self.sidebar.blockSignals(True)
            self.sidebar.setCurrentRow(-1)
            self.sidebar.blockSignals(False)
            # Navigate to the selected page (offset by 6 for bottom items)
            self.content.setCurrentIndex(6 + row)
            self.refresh_current_view()
        
    def refresh_current_view(self):
        """Refresh the currently active view"""
        current_widget = self.content.currentWidget()
        if hasattr(current_widget, 'load_data'):
            current_widget.load_data()
        elif hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()
        
        # Special handling for contract view - refresh details if a contract is selected
        if current_widget == self.contrat_view and hasattr(current_widget, 'refresh_current_contract_details'):
            current_widget.refresh_current_contract_details()
        
    def refresh_dashboard(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
