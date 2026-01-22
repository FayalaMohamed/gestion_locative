#!/usr/bin/env python
"""
Main application window for Gestion Locative Pro
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget,
                               QLabel, QFrame, QSplitter, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction, QFont, QColor, QPalette


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Locative Pro")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        self.setup_ui()
        self.setup_menu()
        self.setup_connections()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        self.sidebar = Sidebar(self)
        splitter.addWidget(self.sidebar)
        
        self.content_stack = QStackedWidget()
        splitter.addWidget(self.content_stack)
        
        splitter.setSizes([250, 950])
        
        self.views = {}
        
        from app.ui.views.dashboard_view import DashboardView
        dashboard_view = DashboardView(self)
        self.views["dashboard"] = dashboard_view
        self.add_view(dashboard_view, "Tableau de Bord")
        
        from app.ui.views.immeuble_view import ImmeubleView
        immeuble_view = ImmeubleView(self)
        self.views["immeuble"] = immeuble_view
        self.add_view(immeuble_view, "Immeubles")
        
        from app.ui.views.bureau_view import BureauView
        bureau_view = BureauView(self)
        self.views["bureau"] = bureau_view
        self.add_view(bureau_view, "Bureaux")
        
        from app.ui.views.locataire_view import LocataireView
        locataire_view = LocataireView(self)
        self.views["locataire"] = locataire_view
        self.add_view(locataire_view, "Locataires")
        
        from app.ui.views.contrat_view import ContratView
        contrat_view = ContratView(self)
        self.views["contrat"] = contrat_view
        self.add_view(contrat_view, "Contrats")
        
        from app.ui.views.paiement_view import PaiementView
        paiement_view = PaiementView(self)
        self.views["paiement"] = paiement_view
        self.add_view(paiement_view, "Paiements")
        
        from app.ui.views.settings_view import SettingsView
        settings_view = SettingsView(self)
        self.views["settings"] = settings_view
        self.add_view(settings_view, "Paramètres")
        
        self.connect_data_changed_signals()
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Fichier")
        
        export_action = QAction("Exporter...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.on_export)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)
        
        tools_menu = menubar.addMenu("Outils")
        
        receipts_action = QAction("Générer reçus PDF...", self)
        tools_menu.addAction(receipts_action)
        
        help_menu = menubar.addMenu("Aide")
        
        about_action = QAction("À propos", self)
        help_menu.addAction(about_action)
        
    def setup_connections(self):
        pass
    
    def on_export(self):
        settings_view = self.views.get("settings")
        if settings_view:
            index = self.content_stack.indexOf(settings_view)
            self.content_stack.setCurrentIndex(index)
            settings_view.on_export()
    
    def add_view(self, view, name, icon=None):
        self.content_stack.addWidget(view)
        self.sidebar.add_item(name, icon)
    
    def set_current_view(self, index):
        self.content_stack.setCurrentIndex(index)


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.item_to_index = {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedWidth(250)
        self.setObjectName("sidebar")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        title_label = QLabel("Gestion Locative Pro")
        title_label.setObjectName("sidebar_title")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(60)
        layout.addWidget(title_label)
        
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("sidebar_list")
        self.list_widget.setFrameShape(QListWidget.NoFrame)
        layout.addWidget(self.list_widget)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)
        
        version_label = QLabel("Version 1.0")
        version_label.setObjectName("sidebar_version")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setFixedHeight(30)
        layout.addWidget(version_label)
        
        self.list_widget.currentRowChanged.connect(self.on_current_row_changed)
        
    def add_item(self, name, icon=None):
        item = QListWidgetItem(name)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.list_widget.addItem(item)
        index = self.list_widget.count() - 1
        self.item_to_index[name] = index
        
    def on_current_row_changed(self, row):
        if self.parent_window:
            self.parent_window.set_current_view(row)


def apply_stylesheet(app):
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 247, 250))
    palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 247, 250))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(51, 51, 51))
    palette.setColor(QPalette.Text, QColor(51, 51, 51))
    palette.setColor(QPalette.Button, QColor(245, 247, 250))
    palette.setColor(QPalette.ButtonText, QColor(51, 51, 51))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Link, QColor(66, 133, 244))
    palette.setColor(QPalette.Highlight, QColor(66, 133, 244))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f7fa;
        }
        
        QWidget#sidebar {
            background-color: #2c3e50;
        }
        
        QWidget#sidebar_title {
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            background-color: #1a252f;
        }
        
        QListWidget#sidebar_list {
            background-color: #2c3e50;
            border: none;
            outline: none;
        }
        
        QListWidget#sidebar_list::item {
            color: #bdc3c7;
            padding: 12px 20px;
            font-size: 14px;
            border: none;
            outline: none;
        }
        
        QListWidget#sidebar_list::item:selected {
            background-color: #34495e;
            color: #ffffff;
            border-left: 3px solid #3498db;
        }
        
        QListWidget#sidebar_list::item:hover:!selected {
            background-color: #34495e;
            color: #ffffff;
        }
        
        QWidget#sidebar_version {
            color: #7f8c8d;
            font-size: 11px;
            background-color: #1a252f;
        }
        
        QLabel {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QMenuBar {
            background-color: #ffffff;
            color: #333333;
            border-bottom: 1px solid #e0e0e0;
            padding: 4px;
        }
        
        QMenuBar::item:selected {
            background-color: #e8f4fd;
        }
        
        QMenu {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 4px;
        }
        
        QMenu::item:selected {
            background-color: #3498db;
            color: #ffffff;
        }
        
        QSplitter::handle {
            background-color: #d0d0d0;
            width: 1px;
        }
    """)


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    
    from app.database.connection import init_database
    init_database()
    
    app = QApplication(sys.argv)
    apply_stylesheet(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
