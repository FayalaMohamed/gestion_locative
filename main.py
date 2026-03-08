#!/usr/bin/env python
"""
Gestion Locative Pro - Application
Run: python main.py
"""
import sys
import os
import subprocess
import tempfile
import ssl
import json
import threading
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget,
                               QLabel, QFrame, QMessageBox, QMenuBar, QMenu, QPushButton)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtGui import QIcon, QPixmap

# Version actuelle de l'application - changez ceci pour chaque release
APP_VERSION = "0.2"
GITHUB_REPO = "FayalaMohamed/gestion_locative"

from app.ui.views.dashboard_view import DashboardView
from app.ui.views.immeuble_view import ImmeubleView
from app.ui.views.bureau_view import BureauView
from app.ui.views.locataire_view import LocataireView
from app.ui.views.contrat_view import ContratView
from app.ui.views.paiement_view import PaiementView
from app.ui.views.audit_view import AuditView
from app.ui.views.settings_view import SettingsView


def migrate_config():
    """Migrate config file if needed"""
    from app.utils.config import Config
    config = Config()
    
    # Get current config version (default to "0" if not set)
    config_version = config.get('app', 'version', default='0')
    
    if config_version != APP_VERSION:
        print(f"Migrating config from v{config_version} to v{APP_VERSION}")
        
        # Add any new config fields here for future migrations
        # Example:
        # if config_version < "1":
        #     config.set([], 'receipts', 'signatures')
        #     config.save_config()
        
        # Update version
        config.set(APP_VERSION, 'app', 'version')
        config.save_config()
        print("Config migration completed")


def run_database_migrations():
    """Run Alembic migrations on startup"""
    try:
        from alembic import command
        from alembic.config import Config as AlembicConfig
        
        alembic_cfg = AlembicConfig("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Database migrations completed successfully")
    except Exception as e:
        import traceback
        print(f"Migration error: {e}")
        traceback.print_exc()
        from PySide6.QtWidgets import QMessageBox, QApplication
        app = QApplication.instance()
        if app:
            QMessageBox.critical(
                None, 
                "Erreur de migration",
                f"La migration de la base de données a échoué:\n{str(e)}\n\n"
                "L'application va se fermer. Veuillez contacter le support."
            )
        import sys
        sys.exit(1)


class UpdateNotification(QWidget):
    """Non-blocking notification popup for update availability"""
    
    def __init__(self, parent=None, version="", download_url="", on_update=None, on_dismiss=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.download_url = download_url
        self.on_update = on_update
        self.on_dismiss = on_dismiss
        self.closed = False
        
        self.setFixedSize(350, 150)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Position at bottom right
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 370, screen.height() - 190)
        
        self.setup_ui(version)
        self.setup_animation()
        
        # Auto-close timer (10 seconds)
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.start_fade_out)
        self.close_timer.start(10000)
    
    def setup_ui(self, version):
        """Setup the notification UI"""
        # Main container with rounded corners
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, 350, 150)
        self.container.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                border-radius: 10px;
                border: 2px solid #3498db;
            }
        """)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Mise à jour disponible")
        title.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 16px;
                font-weight: bold;
                border: none;
                background: transparent;
            }
        """)
        layout.addWidget(title)
        
        # Message
        message = QLabel(f"Version {version} est disponible")
        message.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 13px;
                border: none;
                background: transparent;
            }
        """)
        message.setWordWrap(True)
        layout.addWidget(message)
        
        layout.addStretch()
        
        # Buttons layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # Update button
        update_btn = QPushButton("Mettre à jour")
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        update_btn.clicked.connect(self.on_update_clicked)
        btn_layout.addWidget(update_btn)
        
        # Dismiss button
        dismiss_btn = QPushButton("Ignorer")
        dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        dismiss_btn.clicked.connect(self.on_dismiss_clicked)
        btn_layout.addWidget(dismiss_btn)
        
        layout.addLayout(btn_layout)
    
    def setup_animation(self):
        """Setup fade animation"""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        # Fade in animation
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Fade out animation
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_out.finished.connect(self.close_notification)
        
        # Start fade in
        self.fade_in.start()
    
    def start_fade_out(self):
        """Start fade out animation"""
        if not self.closed:
            self.fade_out.start()
    
    def close_notification(self):
        """Close and cleanup notification"""
        self.closed = True
        if self.on_dismiss:
            self.on_dismiss()
        self.close()
        self.deleteLater()
    
    def on_update_clicked(self):
        """Handle update button click"""
        self.close_timer.stop()
        self.closed = True
        if self.on_update:
            self.on_update(self.download_url)
        self.close()
        self.deleteLater()
    
    def on_dismiss_clicked(self):
        """Handle dismiss button click"""
        self.close_timer.stop()
        self.start_fade_out()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Locative Pro")
        self.setMinimumSize(1200, 800)
        
        icon_path = Path(__file__).parent / "app" / "ui" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.setup_ui()
        self.setup_menu()
        
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # Menu Aide
        help_menu = menubar.addMenu("Aide")
        
        # Action: Vérifier les mises à jour
        check_update_action = help_menu.addAction("Vérifier les mises à jour")
        check_update_action.triggered.connect(self.check_for_updates)
        
        help_menu.addSeparator()
        
        # Action: À propos
        about_action = help_menu.addAction("À propos")
        about_action.triggered.connect(self.show_about)
        
    def check_for_updates(self):
        """Check for updates from GitHub"""
        checking_msg = None
        try:
            # Show checking message
            checking_msg = QMessageBox(self)
            checking_msg.setWindowTitle("Vérification")
            checking_msg.setText("Vérification des mises à jour...")
            checking_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
            checking_msg.show()
            QApplication.processEvents()
            
            # Fetch latest release from GitHub
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            
            # Create SSL context to handle certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(url, headers={'User-Agent': 'GestionLocativeApp'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            # Properly close the checking dialog
            if checking_msg:
                checking_msg.hide()
                checking_msg.close()
                checking_msg.deleteLater()
                QApplication.processEvents()
            
            latest_version = data['tag_name'].replace('v', '').replace('V', '')
            
            if self._is_newer_version(latest_version, APP_VERSION):
                # New version available
                reply = QMessageBox.question(
                    self,
                    "Mise à jour disponible",
                    f"Une nouvelle version est disponible!\n\n"
                    f"Version actuelle: v{APP_VERSION}\n"
                    f"Nouvelle version: v{latest_version}\n\n"
                    f"Voulez-vous télécharger et installer la mise à jour maintenant?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Get download URL from assets - look for .exe file
                    assets = data.get('assets', [])
                    download_url = None
                    
                    for asset in assets:
                        asset_name = asset.get('name', '').lower()
                        if asset_name.endswith('.exe'):
                            download_url = asset.get('browser_download_url')
                            break
                    
                    if download_url:
                        self.download_and_install_update(download_url)
                    else:
                        QMessageBox.warning(
                            self,
                            "Erreur",
                            "Impossible de trouver le fichier de mise à jour (.exe).\n\n"
                            "Assurez-vous que le fichier .exe a été attaché à la release sur GitHub.\n\n"
                            f"Vous pouvez télécharger manuellement depuis:\n"
                            f"https://github.com/{GITHUB_REPO}/releases/latest"
                        )
            else:
                # Up to date
                QMessageBox.information(
                    self,
                    "À jour",
                    f"Vous utilisez la dernière version (v{APP_VERSION})."
                )
                
        except Exception as e:
            # Close checking message on error
            if checking_msg:
                checking_msg.hide()
                checking_msg.close()
                checking_msg.deleteLater()
                QApplication.processEvents()
            
            error_str = str(e)
            
            if "404" in error_str:
                QMessageBox.information(
                    self,
                    "À jour",
                    f"Vous utilisez la dernière version (v{APP_VERSION})."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Erreur",
                    f"Impossible de vérifier les mises à jour.\n\n"
                    f"Détail: {error_str}\n\n"
                    f"Veuillez vérifier votre connexion internet ou réessayer plus tard."
                )
    
    def download_and_install_update(self, download_url: str):
        """Download update and auto-restart"""
        try:
            # Check if running as compiled executable
            if not getattr(sys, 'frozen', False):
                QMessageBox.warning(
                    self,
                    "Information",
                    "La mise à jour automatique n'est disponible que pour la version compilée.\n\n"
                    f"Téléchargez la nouvelle version depuis:\n"
                    f"https://github.com/{GITHUB_REPO}/releases/latest"
                )
                return
            
            # Show downloading message
            downloading_msg = QMessageBox(self)
            downloading_msg.setWindowTitle("Téléchargement")
            downloading_msg.setText("Téléchargement de la mise à jour...")
            downloading_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
            downloading_msg.show()
            QApplication.processEvents()
            
            # Download the new executable
            temp_dir = tempfile.gettempdir()
            temp_exe_path = os.path.join(temp_dir, "gestion_locative_update.exe")
            
            # Create SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Download
            req = urllib.request.Request(download_url, headers={'User-Agent': 'GestionLocativeApp'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=60) as response:
                with open(temp_exe_path, 'wb') as f:
                    f.write(response.read())
            
            downloading_msg.close()
            
            # Get current executable path and directory
            current_exe_path = sys.executable
            current_exe_dir = os.path.dirname(current_exe_path)
            
            # Find database path - check multiple locations
            db_path = None
            possible_db_paths = [
                Path(current_exe_dir) / "data" / "gestion_locative.db",
                Path.cwd() / "data" / "gestion_locative.db",
            ]
            
            for path in possible_db_paths:
                if path.exists():
                    db_path = path
                    break
            
            backup_path = None
            if db_path and db_path.exists():
                import shutil
                backup_dir = db_path.parent
                backup_path = backup_dir / f"gestion_locative_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(db_path, backup_path)
                print(f"Database backed up to: {backup_path}")
            
            # Get the actual exe name for taskkill
            exe_name = os.path.basename(current_exe_path)
            
            # Create log file for debugging
            log_path = os.path.join(temp_dir, "update_log.txt")
            
            # Create batch script for update with logging
            batch_script = f'''@echo off
set LOG_FILE={log_path}
echo Update started at %DATE% %TIME% > "%LOG_FILE%"
echo Temp exe: {temp_exe_path} >> "%LOG_FILE%"
echo Target exe: {current_exe_path} >> "%LOG_FILE%"
echo Exe name: {exe_name} >> "%LOG_FILE%"

echo.
echo ========================================
echo   MISE A JOUR EN COURS
echo ========================================
echo.
echo Fermeture de l'application dans 5 secondes...
timeout /t 5 /nobreak

echo.
echo Arret du processus {exe_name}...
echo Killing process {exe_name}... >> "%LOG_FILE%"
taskkill /F /IM "{exe_name}" 2>>"%LOG_FILE%"
if %errorlevel% == 0 (
    echo Processus arrete avec succes.
    echo Process killed successfully >> "%LOG_FILE%"
) else (
    echo Aucun processus a arreter ou deja ferme.
    echo No process to kill or already closed >> "%LOG_FILE%"
)

echo.
echo Attente de 3 secondes pour liberation des fichiers...
timeout /t 3 /nobreak

echo.
echo Copie du nouveau fichier...
echo Copying file... >> "%LOG_FILE%"
copy /Y "{temp_exe_path}" "{current_exe_path}" >> "%LOG_FILE%" 2>&1
set COPY_RESULT=%errorlevel%

if %COPY_RESULT% == 0 (
    echo.
    echo Copie reussie!
    echo Copy successful >> "%LOG_FILE%"
    
    echo.
    echo Verification du fichier copie...
    if exist "{current_exe_path}" (
        echo Fichier verifie avec succes.
        echo File verified >> "%LOG_FILE%"
    ) else (
        echo ERREUR: Le fichier n'existe pas apres copie!
        echo ERROR: File does not exist after copy >> "%LOG_FILE%"
        goto :error
    )
    
    echo.
    echo Attente de 2 secondes avant redemarrage...
    timeout /t 2 /nobreak
    
    echo.
    echo Demarrage de la nouvelle version...
    echo Starting new version... >> "%LOG_FILE%"
    start "" "{current_exe_path}"
    
    echo.
    echo ========================================
    echo   MISE A JOUR TERMINEE AVEC SUCCES!
    echo ========================================
    echo Update completed successfully >> "%LOG_FILE%"
    timeout /t 2 /nobreak
    goto :cleanup
) else (
    goto :error
)

:error
echo.
echo ========================================
echo   ERREUR LORS DE LA MISE A JOUR
echo ========================================
echo.
echo Code d'erreur de copie: %COPY_RESULT%
echo Copy failed with error %COPY_RESULT% >> "%LOG_FILE%"
echo.
echo Le fichier de log se trouve ici:
echo {log_path}
echo.
echo Vous pouvez telecharger manuellement la mise a jour depuis:
echo https://github.com/{GITHUB_REPO}/releases/latest
echo.
pause

:cleanup
echo Cleaning up... >> "%LOG_FILE%"
del "{temp_exe_path}" 2>>"%LOG_FILE%"
del "%~f0" 2>>"%LOG_FILE%"
'''
            
            batch_path = os.path.join(temp_dir, "update_script.bat")
            with open(batch_path, 'w') as f:
                f.write(batch_script)
            
            # Show success message
            backup_info = f"\n\nSauvegarde de la base de données: {backup_path}" if backup_path else ""
            QMessageBox.information(
                self,
                "Mise à jour",
                f"Mise à jour téléchargée avec succès!{backup_info}\n\n"
                "L'application va se fermer et se redémarrer automatiquement."
            )
            
            # Run the batch script and quit
            subprocess.Popen([batch_path], shell=True)
            QTimer.singleShot(1000, QApplication.quit)
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erreur",
                f"Impossible de télécharger la mise à jour.\n\n"
                f"Détail: {str(e)}\n\n"
                f"Veuillez réessayer plus tard ou contacter le support."
            )
    
    def check_for_updates_silent(self):
        """Check for updates silently in the background"""
        def check_update_worker():
            try:
                # Fetch latest release from GitHub
                url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
                
                # Create SSL context to handle certificates
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                req = urllib.request.Request(url, headers={'User-Agent': 'GestionLocativeApp'})
                with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                    data = json.loads(response.read().decode())
                
                latest_version = data['tag_name'].replace('v', '').replace('V', '')
                
                if self._is_newer_version(latest_version, APP_VERSION):
                    # Get download URL from assets
                    assets = data.get('assets', [])
                    download_url = None
                    
                    # Look for .exe asset
                    for asset in assets:
                        asset_name = asset.get('name', '').lower()
                        if asset_name.endswith('.exe'):
                            download_url = asset.get('browser_download_url')
                            break
                    
                    if download_url:
                        # Show notification on main thread
                        QTimer.singleShot(0, lambda: self.show_update_notification(latest_version, download_url))
                    else:
                        print(f"Update available (v{latest_version}) but no .exe asset found in release")
                        
            except Exception as e:
                # Silently fail - don't show errors during silent check
                print(f"Silent update check failed: {e}")
        
        # Run check in background using QTimer to avoid blocking
        thread = threading.Thread(target=check_update_worker, daemon=True)
        thread.start()
    
    def show_update_notification(self, version: str, download_url: str):
        """Show the update notification popup"""
        self.update_notification = UpdateNotification(
            parent=None,
            version=version,
            download_url=download_url,
            on_update=self.download_and_install_update,
            on_dismiss=lambda: setattr(self, 'update_notification', None)
        )
        self.update_notification.show()
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Compare version strings"""
        try:
            # Split by dot and convert to integers
            latest_parts = [int(x) for x in latest.split('.') if x.isdigit()]
            current_parts = [int(x) for x in current.split('.') if x.isdigit()]
            
            # Pad with zeros
            while len(latest_parts) < len(current_parts):
                latest_parts.append(0)
            while len(current_parts) < len(latest_parts):
                current_parts.append(0)
            
            return latest_parts > current_parts
        except:
            return latest != current
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "À propos",
            f"<b>Gestion Locative Pro</b><br><br>"
            f"Version: v{APP_VERSION}<br><br>"
            f"Application de gestion locative pour bureaux.<br><br>"
            f"© 2024-2026"
        )
        
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
        
        self.immeuble_view.data_changed.connect(self.refresh_current_view)
        self.locataire_view.data_changed.connect(self.refresh_current_view)
        self.contrat_view.data_changed.connect(self.refresh_current_view)
        self.paiement_view.data_changed.connect(self.refresh_current_view)
        self.paiement_view.data_changed.connect(self.contrat_view.refresh_current_contract_details)
        
        self.sidebar.currentRowChanged.connect(self._on_sidebar_changed)
        self.sidebar_bottom.currentRowChanged.connect(self._on_bottom_sidebar_changed)
        
        # Check for updates after 5 seconds (give UI time to load)
        QTimer.singleShot(5000, self.check_for_updates_silent)
        
    def _on_sidebar_changed(self, row):
        if row >= 0:
            self.sidebar_bottom.blockSignals(True)
            self.sidebar_bottom.setCurrentRow(-1)
            self.sidebar_bottom.blockSignals(False)
            self.content.setCurrentIndex(row)
            self.refresh_current_view()
    
    def _on_bottom_sidebar_changed(self, row):
        if row >= 0:
            self.sidebar.blockSignals(True)
            self.sidebar.setCurrentRow(-1)
            self.sidebar.blockSignals(False)
            self.content.setCurrentIndex(6 + row)
            self.refresh_current_view()
        
    def refresh_current_view(self):
        current_widget = self.content.currentWidget()
        if hasattr(current_widget, 'load_data'):
            current_widget.load_data()
        elif hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()
        
        if current_widget == self.contrat_view and hasattr(current_widget, 'refresh_current_contract_details'):
            current_widget.refresh_current_contract_details()


if __name__ == "__main__":
    # Run migrations first
    run_database_migrations()
    migrate_config()
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
