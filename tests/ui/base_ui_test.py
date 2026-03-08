#!/usr/bin/env python
"""
Base UI Test Infrastructure
Provides common utilities for UI testing with proper handling of modal dialogs
"""
import sys
import os
import tempfile
import shutil
import sqlite3
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import date, datetime

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QDialog, QTableWidget, QLineEdit, QPushButton, 
    QMessageBox, QTextEdit, QComboBox, QDateEdit, QWidget, QDoubleSpinBox,
    QSpinBox, QListWidget, QCheckBox
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtTest import QTest


class DialogInteractor:
    def __init__(self):
        self.completed = False
        self.success = False
        self.error_message = None
        self._app = None
        self.error_dialog_found = False
        self.error_dialog_text = None
    
    def _check_for_error_dialogs(self):
        """Check if there are any unexpected error dialogs open"""
        for widget in self._app.topLevelWidgets():
            if isinstance(widget, QMessageBox) and widget.isVisible():
                self.error_dialog_found = True
                self.error_dialog_text = widget.text()
                return True
        return False
    
    def fill_and_submit_dialog(self, dialog_title_substring, field_values, 
                               button_texts=None, list_selections=None, delay_ms=800):
        button_texts = button_texts or ["OK", "&OK", "Enregistrer", "Valider"]
        list_selections = list_selections or {}
        self._app = QApplication.instance()
        
        def interaction_task():
            try:
                dialog = None
                for widget in self._app.topLevelWidgets():
                    if isinstance(widget, QDialog) and widget.isVisible():
                        if dialog_title_substring.lower() in widget.windowTitle().lower():
                            dialog = widget
                            break
                
                if not dialog:
                    for widget in self._app.topLevelWidgets():
                        if isinstance(widget, QDialog) and widget.isVisible():
                            if not isinstance(widget, QMessageBox):
                                dialog = widget
                                break
                
                if not dialog:
                    self.error_message = f"Dialog '{dialog_title_substring}' not found"
                    self.completed = True
                    return
                
                print(f"      [Auto] Found dialog: {dialog.windowTitle()}")
                dialog.raise_()
                dialog.activateWindow()
                QTest.qWait(100)
                
                self._fill_fields(dialog, field_values)
                self._select_list_items(dialog, list_selections)
                
                buttons = dialog.findChildren(QPushButton)
                ok_button = None
                for btn in buttons:
                    for search_text in button_texts:
                        if search_text.lower() in btn.text().lower():
                            ok_button = btn
                            break
                    if ok_button:
                        break
                
                if ok_button and ok_button.isEnabled():
                    print(f"      [Auto] Clicking button: {ok_button.text()}")
                    QTest.mouseClick(ok_button, Qt.MouseButton.LeftButton)
                    self._app.processEvents()
                    QTest.qWait(200)
                    self.success = True
                else:
                    self.error_message = "OK button not found or disabled"
                    dialog.close()
                
                self.completed = True
                
            except Exception as e:
                self.error_message = str(e)
                self.completed = True
                import traceback
                traceback.print_exc()
        
        QTimer.singleShot(delay_ms, interaction_task)
    
    def _fill_fields(self, dialog, field_values):
        filled_count = 0
        
        for field_name, value in field_values.items():
            filled = False
            
            field = dialog.findChild(QComboBox, field_name)
            if field:
                field.setFocus()
                QTest.qWait(30)
                index = field.findText(str(value), Qt.MatchFlag.MatchContains)
                if index >= 0:
                    field.setCurrentIndex(index)
                    print(f"      [Auto] Set QComboBox '{field_name}' = {value} (index {index})")
                else:
                    try:
                        idx = int(value)
                        if 0 <= idx < field.count():
                            field.setCurrentIndex(idx)
                            print(f"      [Auto] Set QComboBox '{field_name}' to index {idx}")
                    except:
                        print(f"      [Auto] Warning: Could not set QComboBox '{field_name}' to {value}")
                self._app.processEvents()
                QTest.qWait(30)
                filled = True
                filled_count += 1
                continue
            
            if not filled:
                field = dialog.findChild(QDateEdit, field_name)
                if field:
                    field.setFocus()
                    QTest.qWait(30)
                    if isinstance(value, (date, datetime)):
                        qdate = QDate(value.year, value.month, value.day)
                        field.setDate(qdate)
                        print(f"      [Auto] Set QDateEdit '{field_name}' = {value}")
                    elif isinstance(value, str):
                        try:
                            dt = datetime.strptime(value, "%Y-%m-%d")
                            qdate = QDate(dt.year, dt.month, dt.day)
                            field.setDate(qdate)
                            print(f"      [Auto] Set QDeateEdit '{field_name}' = {value}")
                        except:
                            print(f"      [Auto] Warning: Could not parse date '{value}'")
                    self._app.processEvents()
                    QTest.qWait(30)
                    filled = True
                    filled_count += 1
                    continue
            
            if not filled:
                field = dialog.findChild(QDoubleSpinBox, field_name)
                if field:
                    field.setFocus()
                    QTest.qWait(30)
                    try:
                        val = float(value)
                        field.setValue(val)
                        print(f"      [Auto] Set QDoubleSpinBox '{field_name}' = {val}")
                    except:
                        print(f"      [Auto] Warning: Could not set QDoubleSpinBox '{field_name}' to {value}")
                    self._app.processEvents()
                    QTest.qWait(30)
                    filled = True
                    filled_count += 1
                    continue
            
            if not filled:
                field = dialog.findChild(QSpinBox, field_name)
                if field:
                    field.setFocus()
                    QTest.qWait(30)
                    try:
                        val = int(value)
                        field.setValue(val)
                        print(f"      [Auto] Set QSpinBox '{field_name}' = {val}")
                    except:
                        print(f"      [Auto] Warning: Could not set QSpinBox '{field_name}' to {value}")
                    self._app.processEvents()
                    QTest.qWait(30)
                    filled = True
                    filled_count += 1
                    continue
            
            if not filled:
                field = dialog.findChild(QTextEdit, field_name)
                if field:
                    field.setFocus()
                    QTest.qWait(30)
                    field.clear()
                    field.setPlainText(str(value))
                    print(f"      [Auto] Set QTextEdit '{field_name}' = {value}")
                    self._app.processEvents()
                    QTest.qWait(30)
                    filled = True
                    filled_count += 1
                    continue
            
            if not filled:
                field = dialog.findChild(QCheckBox, field_name)
                if field:
                    field.setFocus()
                    QTest.qWait(30)
                    checked = bool(value)
                    field.setChecked(checked)
                    print(f"      [Auto] Set QCheckBox '{field_name}' = {checked}")
                    self._app.processEvents()
                    QTest.qWait(30)
                    filled = True
                    filled_count += 1
                    continue
            
            if not filled:
                field = dialog.findChild(QLineEdit, field_name)
                if field:
                    field.setFocus()
                    QTest.qWait(30)
                    field.clear()
                    field.setText(str(value))
                    self._app.processEvents()
                    QTest.qWait(30)
                    print(f"      [Auto] Set QLineEdit '{field_name}' = {value}")
                    filled = True
                    filled_count += 1
                    continue
            
            if not filled:
                print(f"      [Auto] Warning: Field '{field_name}' not found")
        
        print(f"      [Auto] Filled {filled_count}/{len(field_values)} fields")
    
    def _select_list_items(self, dialog, list_selections):
        for list_name, indices in list_selections.items():
            list_widget = dialog.findChild(QListWidget, list_name)
            if list_widget:
                list_widget.setFocus()
                QTest.qWait(50)
                list_widget.clearSelection()
                for idx in indices:
                    if 0 <= idx < list_widget.count():
                        item = list_widget.item(idx)
                        item.setSelected(True)
                        print(f"      [Auto] Selected QListWidget '{list_name}' item {idx}: {item.text()}")
                self._app.processEvents()
                QTest.qWait(50)
            else:
                print(f"      [Auto] Warning: QListWidget '{list_name}' not found")


class DatabaseHelper:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def verify_table_exists(self, table_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def count_records(self, table_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def record_exists(self, table_name, column, value):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM {table_name} WHERE {column} = ?", (value,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def delete_record(self, table_name, column, value):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE {column} = ?", (value,))
        conn.commit()
        conn.close()


class TestRunner:
    def __init__(self):
        self.app = None
        self.main_window = None
        self.test_db_path = None
        self.temp_dir = None
        self._original_db_path = None
        self.test_results = []
        self.db_helper = None
        
    def setup(self):
        print("[SETUP] Initializing test environment...")
        
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        self.temp_dir = tempfile.mkdtemp(prefix="gestion_locative_ui_test_")
        self.test_db_path = os.path.join(self.temp_dir, "test.db")
        
        from app.utils.config import Config
        config = Config()
        self._original_db_path = config.get('database', 'path', default=None)
        config.set(self.test_db_path, 'database', 'path')
        config.save_config()
        
        from app.database.connection import Database
        Database._instance = None
        Database._engine = None
        Database._session_factory = None
        
        from app.database.connection import get_database
        db = get_database()
        db.create_tables()
        
        self.db_helper = DatabaseHelper(self.test_db_path)
        
        assert self.db_helper.verify_table_exists("immeubles"), "immeubles table not created"
        assert self.db_helper.verify_table_exists("locataires"), "locataires table not created"
        print(f"    ✓ Database ready with tables")
        
        from main import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        
        self.app.processEvents()
        QTest.qWait(500)
        
        print(f"[SETUP] Complete (DB: {self.test_db_path})")
    
    def teardown(self):
        print("\n[TEARDOWN] Cleaning up...")
        
        self._close_all_dialogs()
        
        if self._original_db_path:
            from app.utils.config import Config
            config = Config()
            config.set(self._original_db_path, 'database', 'path')
            config.save_config()
        
        if self.main_window:
            self.main_window.close()
            self.main_window.deleteLater()
            self.main_window = None
        
        if self.app:
            self.app.processEvents()
        
        from app.database.connection import Database
        Database._instance = None
        Database._engine = None
        Database._session_factory = None
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"    ✓ Test directory removed")
            except Exception as e:
                print(f"    ⚠ Could not remove test directory: {e}")
    
    def _close_all_dialogs(self):
        for widget in self.app.topLevelWidgets():
            if isinstance(widget, QDialog):
                try:
                    widget.close()
                    widget.deleteLater()
                except Exception:
                    pass
    
    def navigate_to_view(self, view_name):
        view_map = {
            "dashboard": 0, "immeubles": 1, "bureaux": 2, "locataires": 3,
            "contrats": 4, "paiements": 5, "historique": 6, "parametres": 7
        }
        
        index = view_map.get(view_name.lower())
        if index is None:
            raise ValueError(f"Unknown view: {view_name}")
        
        self._close_all_dialogs()
        
        if index < 6:
            self.main_window.sidebar.setCurrentRow(index)
        else:
            self.main_window.sidebar_bottom.setCurrentRow(index - 6)
        
        self.app.processEvents()
        QTest.qWait(300)
        
        return self.main_window.content.currentWidget()
    
    def click_button(self, button_text):
        current_view = self.main_window.content.currentWidget()
        buttons = current_view.findChildren(QPushButton)
        
        for btn in buttons:
            if button_text.lower() in btn.text().lower():
                QTest.mouseClick(btn, Qt.MouseButton.LeftButton)
                self.app.processEvents()
                QTest.qWait(300)
                return True
        
        return False
    
    def delete_via_ui_with_confirmation(self, view, confirm_cascade=True):
        """
        Click delete button and handle all confirmation dialogs.
        Uses two separate async handlers for each dialog type.
        """
        from PySide6.QtWidgets import QPushButton
        
        def handle_first_confirmation():
            """Handle the first 'Are you sure?' dialog"""
            print("    [Auto] Handler 1: Waiting for first confirmation dialog...")
            app = QApplication.instance()
            for _ in range(30):  # 3 seconds
                app.processEvents()
                
                for widget in app.topLevelWidgets():
                    if isinstance(widget, QMessageBox) and widget.isVisible():
                        print(f"    [Auto] Handler 1: Found dialog - Title: '{widget.windowTitle()}'")
                        yes_btn = widget.button(QMessageBox.Yes)
                        if yes_btn:
                            print(f"    [Auto] Handler 1: Clicking Yes button")
                            QTest.mouseClick(yes_btn, Qt.MouseButton.LeftButton)
                        else:
                            print(f"    [Auto] Handler 1: No Yes button, using accept()")
                            widget.accept()
                        return
                
                QTest.qWait(100)
            
            print("    [Auto] Handler 1: No dialog found after 3 seconds")
        
        def handle_cascade_warning():
            """Handle the cascade warning dialog"""
            print("    [Auto] Handler 2: Waiting for cascade warning dialog...")
            app = QApplication.instance()
            for _ in range(30):  # 3 seconds
                app.processEvents()
                
                for widget in app.topLevelWidgets():
                    if isinstance(widget, QMessageBox) and widget.isVisible():
                        title = widget.windowTitle()
                        text = widget.text()
                        print(f"    [Auto] Handler 2: Found dialog - Title: '{title}'")
                        print(f"    [Auto] Handler 2: Dialog text: {text[:60]}...")
                        
                        is_cascade = "cascade" in title.lower() or "cascade" in text.lower()
                        print(f"    [Auto] Handler 2: Is cascade dialog: {is_cascade}")
                        
                        if is_cascade:
                            if confirm_cascade:
                                yes_btn = widget.button(QMessageBox.Yes)
                                if yes_btn:
                                    print(f"    [Auto] Handler 2: Clicking Yes button")
                                    QTest.mouseClick(yes_btn, Qt.MouseButton.LeftButton)
                                else:
                                    print(f"    [Auto] Handler 2: No Yes button, using accept()")
                                    widget.accept()
                            else:
                                no_btn = widget.button(QMessageBox.No)
                                if no_btn:
                                    print(f"    [Auto] Handler 2: Clicking No button")
                                    QTest.mouseClick(no_btn, Qt.MouseButton.LeftButton)
                                else:
                                    widget.reject()
                        return
                
                QTest.qWait(100)
            
            print("    [Auto] Handler 2: No cascade dialog found after 3 seconds")
        
        # Schedule both handlers with delays
        QTimer.singleShot(300, handle_first_confirmation)
        QTimer.singleShot(800, handle_cascade_warning)
        
        # Now click the delete button
        buttons = view.findChildren(QPushButton)
        for btn in buttons:
            if "supprimer" in btn.text().lower():
                print(f"    [Auto] Clicking delete button: {btn.text()}")
                QTest.mouseClick(btn, Qt.MouseButton.LeftButton)
                return True
        
        print("    [Auto] Delete button not found")
        return False

    def get_table_row_count(self):
        current_view = self.main_window.content.currentWidget()
        tables = current_view.findChildren(QTableWidget)
        return tables[0].rowCount() if tables else 0
    
    def open_dialog_and_fill(self, button_text, dialog_title, field_values, list_selections=None, timeout_ms=15000):
        interactor = DialogInteractor()
        interactor.fill_and_submit_dialog(dialog_title, field_values, 
                                         list_selections=list_selections, delay_ms=800)
        
        print(f"    Clicking '{button_text}' button (dialog will open)...")
        clicked = self.click_button(button_text)
        
        if not clicked:
            return False
        
        start_time = time.time()
        timeout_sec = timeout_ms / 1000.0
        
        while not interactor.completed:
            self.app.processEvents()
            QTest.qWait(100)
            
            if interactor._check_for_error_dialogs():
                print(f"    ⚠ Error dialog detected: {interactor.error_dialog_text}")
                for widget in self.app.topLevelWidgets():
                    if isinstance(widget, QMessageBox) and widget.isVisible():
                        widget.close()
                return False
            
            elapsed = time.time() - start_time
            if elapsed > timeout_sec:
                print(f"    ⚠ Timeout after {timeout_ms}ms waiting for dialog completion")
                self._close_all_dialogs()
                return False
        
        if interactor.error_message:
            print(f"    ⚠ Dialog error: {interactor.error_message}")
            return False
        
        QTest.qWait(500)
        return True
    
    def run_test(self, test_name, test_func):
        print(f"\n{'='*60}")
        print(f"  TEST: {test_name}")
        print(f"{'='*60}")
        
        try:
            test_func(self)
            result = {"name": test_name, "status": "PASSED", "error": None}
            print(f"  ✓ PASSED")
            self.test_results.append(result)
            return True
        except Exception as e:
            result = {"name": test_name, "status": "FAILED", "error": str(e)}
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        self.test_results.append(result)
        return False
    
    def print_report(self):
        print(f"\n{'='*60}")
        print("  TEST REPORT")
        print(f"{'='*60}")
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASSED")
        failed = total - passed
        
        for result in self.test_results:
            status_icon = "✓" if result["status"] == "PASSED" else "✗"
        print(f"{status_icon} {result['name']}: {result['status']}")
        if result["error"]:
            print(f"   Error: {result['error']}")
        
        print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
        print(f"{'='*60}")
        
        return failed == 0


if __name__ == "__main__":
    print("Base UI Test Infrastructure - Do not run directly")
    print("Use run_all_ui_tests.py instead")
