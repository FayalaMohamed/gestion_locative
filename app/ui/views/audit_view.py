#!/usr/bin/env python
"""
Audit log history view
"""
from datetime import datetime
from typing import Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QMessageBox, QDateEdit
)
from PySide6.QtCore import Qt

from app.ui.views.base_view import BaseView
from app.database.connection import get_database
from app.models.entities import AuditLog


class AuditView(BaseView):
    def setup_ui(self):
        super().setup_ui()

        header_layout = QHBoxLayout()

        title = QLabel("Historique des actions")
        title.setObjectName("view_title")
        header_layout.addWidget(title)

        header_layout.addStretch()
        self.layout().addLayout(header_layout)

        filter_group = QGroupBox("Filtres")
        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.setFixedWidth(200)
        filter_layout.addWidget(self.search_input)

        self.action_filter = QComboBox()
        self.action_filter.addItems(["Toutes les actions", "CREATE", "UPDATE", "DELETE", "RECEIPT_GENERATED"])
        filter_layout.addWidget(self.action_filter)

        self.btn_refresh = QPushButton("Actualiser")
        self.btn_refresh.setStyleSheet("background-color: #3498db; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        filter_layout.addWidget(self.btn_refresh)

        filter_group.setLayout(filter_layout)
        self.layout().addWidget(filter_group)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Action", "Table", "Entité", "Détails"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QTableWidget.NoFrame)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.layout().addWidget(self.table)

        self.layout().addStretch()

    def setup_connections(self):
        self.btn_refresh.clicked.connect(self.load_data)
        self.search_input.textChanged.connect(self.on_filter)
        self.action_filter.currentIndexChanged.connect(self.on_filter)
        self.load_data()

    def load_data(self):
        try:
            db = get_database()
            with db.session_scope() as session:
                logs = session.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
                self.display_logs(logs)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {str(e)}")

    def display_logs(self, logs: list):
        self.table.setRowCount(0)
        for log in logs:
            row = self.table.rowCount()
            self.table.insertRow(row)

            date_item = QTableWidgetItem(log.created_at.strftime('%d/%m/%Y %H:%M'))
            date_item.setData(Qt.UserRole, log.created_at)
            self.table.setItem(row, 0, date_item)

            action_item = QTableWidgetItem(log.action)
            if log.action == "CREATE":
                action_item.setBackground(Qt.green)
                action_item.setForeground(Qt.white)
            elif log.action == "DELETE":
                action_item.setBackground(Qt.red)
                action_item.setForeground(Qt.white)
            elif log.action == "UPDATE":
                action_item.setBackground(Qt.yellow)
                action_item.setForeground(Qt.black)
            elif log.action == "RECEIPT_GENERATED":
                action_item.setBackground(Qt.cyan)
                action_item.setForeground(Qt.black)
            self.table.setItem(row, 1, action_item)

            self.table.setItem(row, 2, QTableWidgetItem(log.table_nom or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(str(log.entite_id) if log.entite_id else "-"))

            details = ""
            if log.donnees_avant:
                details += f"Avant: {str(log.donnees_avant)[:50]}..."
            if log.donnees_apres:
                if details:
                    details += "\n"
                details += f"Après: {str(log.donnees_apres)[:50]}..."
            self.table.setItem(row, 4, QTableWidgetItem(details if details else "-"))

        self.table.resizeRowsToContents()

    def on_filter(self, text=None):
        search_text = self.search_input.text().lower()
        action_filter = self.action_filter.currentText()

        for row in range(self.table.rowCount()):
            match = True

            if search_text:
                row_text = ""
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                if search_text not in row_text:
                    match = False

            if action_filter != "Toutes les actions":
                action_item = self.table.item(row, 1)
                if action_item and action_item.text() != action_filter:
                    match = False

            self.table.setRowHidden(row, not match)
