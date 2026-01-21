#!/usr/bin/env python
"""
Dashboard view for Gestion Locative Pro - Empty placeholder
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from app.ui.views.base_view import BaseView


class DashboardView(BaseView):
    
    def setup_ui(self):
        super().setup_ui()
        
        header_layout = QHBoxLayout()
        
        title = QLabel("Tableau de Bord")
        title.setObjectName("view_title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.layout().addLayout(header_layout)
        
        content_layout = QVBoxLayout()
        content_layout.addStretch()
        
        placeholder = QLabel("Tableau de bord en construction")
        placeholder.setStyleSheet("color: #7f8c8d; font-size: 18px; font-style: italic;")
        placeholder.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(placeholder)
        
        content_layout.addStretch()
        
        self.layout().addLayout(content_layout)
