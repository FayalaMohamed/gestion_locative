#!/usr/bin/env python
"""
Contrat management view with red/green payment grid
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QMessageBox, QGroupBox,
                               QFormLayout, QGridLayout, QTextEdit, QComboBox,
                               QDateEdit, QDoubleSpinBox, QListWidget, QListWidgetItem,
                               QScrollArea, QFrame, QCheckBox)
from PySide6.QtCore import Qt, Signal, QSize, QDate
from PySide6.QtGui import QFont, QColor

from app.ui.views.base_view import BaseView


class ContratView(BaseView):
    data_changed = Signal()
    _is_loading = False
    
    def setup_ui(self):
        super().setup_ui()
        
        header_layout = QHBoxLayout()
        
        title = QLabel("Contrats de Location")
        title.setObjectName("view_title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.btn_refresh = QPushButton("Actualiser")
        self.btn_refresh.setStyleSheet("background-color: #ecf0f1; padding: 8px 16px; border: 1px solid #bdc3c7; border-radius: 4px;")
        header_layout.addWidget(self.btn_refresh)
        
        self.layout().addLayout(header_layout)
        
        filter_layout = QHBoxLayout()
        
        self.locataire_combo = QComboBox()
        self.locataire_combo.setMinimumWidth(200)
        self.locataire_combo.addItem("Tous les locataires", None)
        filter_layout.addWidget(self.locataire_combo)
        
        self.statut_combo = QComboBox()
        self.statut_combo.addItem("Tous les statuts", None)
        self.statut_combo.addItem("Actifs", "actif")
        self.statut_combo.addItem("Résiliés", "resilie")
        filter_layout.addWidget(self.statut_combo)
        
        filter_layout.addStretch()
        
        self.layout().addLayout(filter_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_title = QLabel("Liste des Contrats")
        left_title.setObjectName("section_title")
        left_layout.addWidget(left_title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Locataire", "Bureaux", "Date Début", "Mensuel", "Statut"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setFrameShape(QTableWidget.NoFrame)
        self.table.horizontalHeader().setStretchLastSection(True)
        left_layout.addWidget(self.table)
        
        buttons_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("Ajouter")
        self.btn_add.setStyleSheet("background-color: #3498db; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        buttons_layout.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("Modifier")
        self.btn_edit.setStyleSheet("background-color: #ecf0f1; padding: 8px 16px; border: 1px solid #bdc3c7; border-radius: 4px;")
        buttons_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        buttons_layout.addWidget(self.btn_delete)
        
        left_layout.addLayout(buttons_layout)
        
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        self.groupe_title = QLabel("Détails du Contrat")
        self.groupe_title.setObjectName("section_title")
        right_layout.addWidget(self.groupe_title)
        
        self.detail_frame = QFrame()
        self.detail_frame.setFrameShape(QFrame.StyledPanel)
        self.detail_layout = QVBoxLayout(self.detail_frame)
        right_layout.addWidget(self.detail_frame)
        
        self.no_selection_label = QLabel("Sélectionnez un contrat pour voir les détails")
        self.no_selection_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        self.detail_layout.addWidget(self.no_selection_label)
        
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        
        splitter.setSizes([500, 400])
        
        self.layout().addWidget(splitter)
        
    def setup_connections(self):
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.locataire_combo.currentIndexChanged.connect(self.load_data)
        self.statut_combo.currentIndexChanged.connect(self.load_data)
        self.load_data()
        
    def load_data(self):
        if self._is_loading:
            return
        self._is_loading = True
        try:
            from app.database.connection import get_database
            from app.models.entities import Contrat, Locataire, Bureau
            from sqlalchemy import or_
            from sqlalchemy.orm import joinedload
            
            db = get_database()
            
            with db.session_scope() as session:
                query = session.query(Contrat).options(joinedload(Contrat.locataire), joinedload(Contrat.bureaux)).join(Locataire)
                
                loc_id = self.locataire_combo.currentData()
                if loc_id:
                    query = query.filter(Contrat.Locataire_id == loc_id)
                    
                statut_value = self.statut_combo.currentData()
                if statut_value == "actif":
                    query = query.filter(Contrat.est_resilie_col == False)
                elif statut_value == "resilie":
                    query = query.filter(Contrat.est_resilie_col == True)
                    
                contrats = query.order_by(Contrat.date_debut.desc()).all()
                
                self.table.setRowCount(len(contrats))
                
                for row, ctr in enumerate(contrats):
                    self.table.setItem(row, 0, QTableWidgetItem(str(ctr.id)))
                    self.table.setItem(row, 1, QTableWidgetItem(ctr.locataire.nom if ctr.locataire else "N/A"))
                    
                    nums = ", ".join([b.numero for b in ctr.bureaux]) if ctr.bureaux else "Aucun"
                    self.table.setItem(row, 2, QTableWidgetItem(nums))
                    
                    self.table.setItem(row, 3, QTableWidgetItem(str(ctr.date_debut)))
                    self.table.setItem(row, 4, QTableWidgetItem(f"{ctr.montant_mensuel} TND"))
                    self.table.setItem(row, 5, QTableWidgetItem("Résilié" if ctr.est_resilie_col else "Actif"))
                    
                    for col in range(6):
                        self.table.item(row, col).setFlags(
                            Qt.ItemIsSelectable | Qt.ItemIsEnabled
                        )
                        
                self.load_locataires()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
        finally:
            self._is_loading = False
            
    def load_locataires(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Locataire
            
            db = get_database()
            with db.session_scope() as session:
                locs = session.query(Locataire).all()
                
                current_data = self.locataire_combo.currentData()
                self.locataire_combo.blockSignals(True)
                self.locataire_combo.clear()
                self.locataire_combo.addItem("Tous les locataires", None)
                
                for loc in locs:
                    self.locataire_combo.addItem(loc.nom, loc.id)
                    
                if current_data is not None:
                    idx = self.locataire_combo.findData(current_data)
                    if idx >= 0:
                        self.locataire_combo.setCurrentIndex(idx)
                self.locataire_combo.blockSignals(False)
                        
        except Exception as e:
            print(f"Erreur: {e}")
            
    def load_impayes(self, contrat_id, label, list_widget, date_debut, est_resilie, date_resiliation):
        try:
            from app.database.connection import get_database
            from app.models.entities import Contrat, Paiement, TypePaiement
            from datetime import date
            
            db = get_database()
            
            with db.session_scope() as session:
                paiements = session.query(Paiement).filter(
                    Paiement.contrat_id == contrat_id,
                    Paiement.type_paiement == TypePaiement.LOYER
                ).all()
                
                mois_payes = set()
                for p in paiements:
                    mois = p.get_mois_couverts()
                    mois_payes.update(mois)
                
                mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                             "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
                
                mois_impayes = []
                
                if date_debut:
                    start_year, start_month = date_debut.year, date_debut.month
                    end_year, end_month = date.today().year, date.today().month
                    
                    if est_resilie and date_resiliation:
                        end_year, end_month = date_resiliation.year, date_resiliation.month
                    
                    year, month = start_year, start_month
                    while (year < end_year) or (year == end_year and month <= end_month):
                        if (year, month) not in mois_payes:
                            mois_impayes.append((year, month))
                        month += 1
                        if month > 12:
                            month = 1
                            year += 1
                
                count = len(mois_impayes)
                if count > 0:
                    label.setText(f"<u>Mois impayés: {count}</u>")
                    label.setStyleSheet("color: #e74c3c; font-weight: bold; cursor: pointer;")
                    list_widget.clear()
                    for year, month in mois_impayes:
                        item = QListWidgetItem(f"{mois_noms[month-1]} {year}")
                        list_widget.addItem(item)
                else:
                    label.setText("Aucun mois impayé")
                    label.setStyleSheet("color: #27ae60; font-weight: bold;")
                    list_widget.clear()
                    
        except Exception as e:
            print(f"Erreur load_impayes: {e}")
            
    def toggle_impayes_list(self, label, list_widget, contrat_id):
        try:
            from app.database.connection import get_database
            from app.models.entities import Contrat
            
            db = get_database()
            with db.session_scope() as session:
                ctr = session.query(Contrat).get(contrat_id)
                if ctr:
                    current_height = list_widget.maximumHeight()
                    if current_height == 0:
                        list_widget.setMaximumHeight(150)
                        self.load_impayes(contrat_id, label, list_widget, ctr.date_debut, ctr.est_resilie_col, ctr.date_resiliation)
                    else:
                        list_widget.setMaximumHeight(0)
        except Exception as e:
            print(f"Erreur toggle: {e}")
            
    def on_selection_changed(self):
        selected = self.table.selectedItems()
        if not selected:
            self.clear_details()
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        self.show_details(item_id)
        
    def clear_details(self):
        self.no_selection_label.show()
        
        for i in range(self.detail_layout.count() - 1, -1, -1):
            item = self.detail_layout.itemAt(i)
            if item.widget() and item.widget() != self.no_selection_label:
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
                
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
        
    def show_details(self, contrat_id):
        self.clear_details()
        try:
            from app.database.connection import get_database
            from app.models.entities import Contrat, Paiement, TypePaiement
            from datetime import datetime
            
            db = get_database()
            
            with db.session_scope() as session:
                ctr = session.query(Contrat).get(contrat_id)
                if not ctr:
                    return
                    
                self.no_selection_label.hide()
                
                info_layout = QFormLayout()
                
                info_layout.addRow("Locataire:", QLabel(ctr.locataire.nom if ctr.locataire else "N/A"))
                
                bureaux_str = ", ".join([f"#{b.numero}" for b in ctr.bureaux]) if ctr.bureaux else "Aucun"
                info_layout.addRow("Bureaux:", QLabel(bureaux_str))
                
                info_layout.addRow("Date début:", QLabel(str(ctr.date_debut)))
                
                if ctr.date_derniere_augmentation:
                    info_layout.addRow("Dernière augmentation:", QLabel(str(ctr.date_derniere_augmentation)))
                
                info_layout.addRow("Premier mois:", QLabel(f"{ctr.montant_premier_mois} TND"))
                info_layout.addRow("Mensuel:", QLabel(f"{ctr.montant_mensuel} TND"))
                info_layout.addRow("Caution:", QLabel(f"{ctr.montant_caution} TND"))
                info_layout.addRow("Pas de porte:", QLabel(f"{ctr.montant_pas_de_porte} TND"))
                
                if ctr.compteur_steg:
                    info_layout.addRow("Compteur STEG:", QLabel(ctr.compteur_steg))
                if ctr.compteur_sonede:
                    info_layout.addRow("Compteur SONEDE:", QLabel(ctr.compteur_sonede))
                
                info_layout.addRow("Statut:", QLabel("Résilié" if ctr.est_resilie_col else "Actif"))
                
                if ctr.est_resilie_col and ctr.date_resiliation:
                    info_layout.addRow("Date résiliation:", QLabel(str(ctr.date_resiliation)))
                if ctr.est_resilie_col and ctr.motif_resiliation:
                    info_layout.addRow("Motif résiliation:", QLabel(ctr.motif_resiliation))
                
                if ctr.conditions:
                    info_layout.addRow("Conditions:", QLabel(ctr.conditions))
                
                self.detail_layout.addLayout(info_layout)
                
                from datetime import date
                current_date = date.today()
                current_month = current_date.month
                current_year = current_date.year
                
                mois_impayes_label = QLabel()
                mois_impayes_label.setObjectName("clickable_label")
                mois_impayes_label.setCursor(Qt.PointingHandCursor)
                self.detail_layout.addWidget(mois_impayes_label)
                mois_impayes_label.clicked = False
                mois_impayes_label.mousePressEvent = lambda event: self.toggle_impayes_list(mois_impayes_label, impayes_list, contrat_id)
                
                impayes_list = QListWidget()
                impayes_list.setObjectName("impayes_list")
                impayes_list.setMaximumHeight(0)
                impayes_list.setStyleSheet("background-color: #f8f9fa; border-radius: 4px;")
                self.detail_layout.addWidget(impayes_list)
                
                self.load_impayes(contrat_id, mois_impayes_label, impayes_list, ctr.date_debut, ctr.est_resilie_col, ctr.date_resiliation)
                
                grid_label = QLabel(f"\nGrille des Paiements:")
                grid_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
                self.detail_layout.addWidget(grid_label)
                
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                scroll_area.setMinimumHeight(120)
                scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
                
                paiements = session.query(Paiement).filter(
                    Paiement.contrat_id == contrat_id,
                    Paiement.type_paiement == TypePaiement.LOYER
                ).all()
                
                mois_payes = set()
                for p in paiements:
                    mois = p.get_mois_couverts()
                    mois_payes.update(mois)
                    
                grid_widget = self.create_grid_widget(ctr, mois_payes, current_year, current_month)
                scroll_area.setWidget(grid_widget)
                self.detail_layout.addWidget(scroll_area)
                
        except Exception as e:
            print(f"Erreur détails: {e}")
            
    def create_grid_widget(self, contrat, mois_payes, current_year, current_month):
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(3)
        
        mois_noms = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jui", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        
        months_to_show = 12
        start_month_offset = -5
        
        def get_month_info(offset):
            m = current_month + start_month_offset + offset
            if m <= 0:
                return (current_year - 1, 12 + m)
            elif m > 12:
                return (current_year + 1, m - 12)
            return (current_year, m)
        
        for col in range(months_to_show):
            year, month = get_month_info(col)
            
            if month == current_month and year == current_year:
                label = QLabel(f"{mois_noms[month-1]} {year}")
                label.setStyleSheet("font-size: 11px; font-weight: bold; color: #2c3e50;")
            else:
                label = QLabel(f"{mois_noms[month-1]} {year}")
                label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
            label.setAlignment(Qt.AlignCenter)
            grid_layout.addWidget(label, 0, col)
            
        contract_start = contrat.date_debut
        contract_resilie = contrat.est_resilie_col
        contract_resiliation_date = contrat.date_resiliation
        
        for col in range(months_to_show):
            year, month = get_month_info(col)
            month_tuple = (year, month)
            
            is_paye = month_tuple in mois_payes
            
            month_covered = False
            if contract_start:
                contract_start_tuple = (contract_start.year, contract_start.month)
                if month_tuple >= contract_start_tuple:
                    if contract_resilie and contract_resiliation_date:
                        resiliation_tuple = (contract_resiliation_date.year, contract_resiliation_date.month)
                        if month_tuple <= resiliation_tuple:
                            month_covered = True
                    elif not contract_resilie:
                        month_covered = True
            
            if not month_covered:
                color = QColor(231, 76, 60)
                tooltip = f"Non couvert ({mois_noms[month-1]} {year})"
            elif is_paye:
                color = QColor(46, 204, 113)
                tooltip = f"Payé ({mois_noms[month-1]} {year})"
            else:
                color = QColor(189, 195, 199)
                tooltip = f"Non payé ({mois_noms[month-1]} {year})"
                
            cell = QLabel()
            cell.setFixedSize(50, 40)
            cell.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px;")
            cell.setToolTip(tooltip)
            grid_layout.addWidget(cell, 1, col)
            
        layout.addLayout(grid_layout)
        
        legend_layout = QHBoxLayout()
        legend_layout.setContentsMargins(0, 10, 0, 0)
        
        legend_layout.addWidget(self.create_legend_item("#2ecc71", "Payé"))
        legend_layout.addWidget(self.create_legend_item("#bdc3c7", "Non payé"))
        legend_layout.addWidget(self.create_legend_item("#e74c3c", "Non couvert"))
        legend_layout.addStretch()
        
        layout.addLayout(legend_layout)
        
        return widget
        
    def create_legend_item(self, color, text):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        color_box = QLabel()
        color_box.setFixedSize(16, 16)
        color_box.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
        layout.addWidget(color_box)
        
        label = QLabel(text)
        label.setStyleSheet("font-size: 12px;")
        layout.addWidget(label)
        
        return widget
        
    def on_add(self):
        dialog = ContratDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
            
    def on_edit(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un contrat")
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        
        dialog = ContratDialog(self, contrat_id=item_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
            
    def on_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un contrat")
            return
            
        item_id = int(self.table.item(selected[0].row(), 0).text())
        
        reply = QMessageBox.question(self, "Confirmation", 
                                    "Êtes-vous sûr de vouloir supprimer ce contrat?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                from app.database.connection import get_database
                from app.models.entities import Contrat, Paiement, Locataire, StatutLocataire
                from app.repositories.contrat_repository import ContratRepository
                from sqlalchemy import func
                
                db = get_database()
                with db.session_scope() as session:
                    repo = ContratRepository(session)
                    ctr = repo.get_by_id(item_id)
                    if ctr:
                        paiement_count = session.query(func.count(Paiement.id)).filter(Paiement.contrat_id == item_id).scalar()
                        if paiement_count > 0:
                            QMessageBox.warning(self, "Suppression impossible", 
                                f"Ce contrat a {paiement_count} paiement(s) associé(s). Supprimez d'abord les paiements associés.")
                            return
                        
                        loc_id = ctr.Locataire_id
                        repo.delete(ctr)
                        
                        active_count = session.query(func.count(Contrat.id)).filter(
                            Contrat.Locataire_id == loc_id,
                            Contrat.est_resilie_col == False
                        ).scalar()
                        if active_count == 0:
                            loc_repo = session.query(Locataire).get(loc_id)
                            if loc_repo:
                                loc_repo.statut = StatutLocataire.HISTORIQUE
                                
                self.load_data()
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")


from PySide6.QtWidgets import QDialog, QDialogButtonBox, QSplitter


class ContratDialog(QDialog):
    def __init__(self, parent=None, contrat_id=None):
        super().__init__(parent)
        self.parent_view = parent
        self.contrat_id = contrat_id
        
        if contrat_id:
            self.setWindowTitle("Modifier Contrat")
        else:
            self.setWindowTitle("Nouveau Contrat")
            
        self.resize(750, 700)
        self.setup_ui()
        self.setup_connections()
        
        self.load_locataires()
        self.load_bureaux()
        
        if contrat_id:
            self.load_data()
            
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Vertical)
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        
        self.locataire_combo = QComboBox()
        self.load_locataires()
        form_layout.addRow("Locataire*:", self.locataire_combo)
        
        self.bureaux_list = QListWidget()
        self.bureaux_list.setSelectionMode(QListWidget.MultiSelection)
        self.bureaux_list.setMinimumHeight(100)
        form_layout.addRow("Bureaux*:", self.bureaux_list)
        
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate())
        form_layout.addRow("Date début*:", self.date_debut)
        
        self.date_derniere_augmentation = QDateEdit()
        self.date_derniere_augmentation.setCalendarPopup(True)
        self.date_derniere_augmentation.setDate(QDate.currentDate())
        form_layout.addRow("Dernière augmentation:", self.date_derniere_augmentation)
        
        self.montant_premier_mois = QDoubleSpinBox()
        self.montant_premier_mois.setMinimum(0)
        self.montant_premier_mois.setMaximum(1000000)
        self.montant_premier_mois.setSuffix(" TND")
        self.montant_premier_mois.setDecimals(3)
        form_layout.addRow("Premier mois*:", self.montant_premier_mois)
        
        self.montant_mensuel = QDoubleSpinBox()
        self.montant_mensuel.setMinimum(0)
        self.montant_mensuel.setMaximum(1000000)
        self.montant_mensuel.setSuffix(" TND")
        self.montant_mensuel.setDecimals(3)
        form_layout.addRow("Mensuel*:", self.montant_mensuel)
        
        self.montant_caution = QDoubleSpinBox()
        self.montant_caution.setMinimum(0)
        self.montant_caution.setMaximum(1000000)
        self.montant_caution.setSuffix(" TND")
        self.montant_caution.setDecimals(3)
        form_layout.addRow("Caution:", self.montant_caution)
        
        self.montant_pas_de_porte = QDoubleSpinBox()
        self.montant_pas_de_porte.setMinimum(0)
        self.montant_pas_de_porte.setMaximum(1000000)
        self.montant_pas_de_porte.setSuffix(" TND")
        self.montant_pas_de_porte.setDecimals(3)
        form_layout.addRow("Pas de porte:", self.montant_pas_de_porte)
        
        self.compteur_steg_edit = QLineEdit()
        form_layout.addRow("Compteur STEG:", self.compteur_steg_edit)
        
        self.compteur_sonede_edit = QLineEdit()
        form_layout.addRow("Compteur SONEDE:", self.compteur_sonede_edit)
        
        self.conditions_edit = QTextEdit()
        self.conditions_edit.setMaximumHeight(80)
        form_layout.addRow("Conditions:", self.conditions_edit)
        
        self.resiliation_group = QGroupBox("Résiliation")
        resiliation_layout = QFormLayout()
        
        self.est_resilie_col = QCheckBox("Contrat résilié")
        resiliation_layout.addRow("", self.est_resilie_col)
        
        self.date_resiliation = QDateEdit()
        self.date_resiliation.setCalendarPopup(True)
        self.date_resiliation.setDate(QDate.currentDate())
        self.date_resiliation.setEnabled(False)
        resiliation_layout.addRow("Date résiliation:", self.date_resiliation)
        
        self.motif_resiliation_edit = QTextEdit()
        self.motif_resiliation_edit.setMaximumHeight(60)
        self.motif_resiliation_edit.setEnabled(False)
        resiliation_layout.addRow("Motif résiliation:", self.motif_resiliation_edit)
        
        self.resiliation_group.setLayout(resiliation_layout)
        form_layout.addRow(self.resiliation_group)
        
        splitter.addWidget(form_widget)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.addStretch()
        btn_layout.addWidget(buttons)
        splitter.addWidget(btn_widget)
        
        layout.addWidget(splitter)
        
    def setup_connections(self):
        self.est_resilie_col.toggled.connect(self.date_resiliation.setEnabled)
        self.est_resilie_col.toggled.connect(self.motif_resiliation_edit.setEnabled)
        
    def load_locataires(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Locataire
            
            db = get_database()
            with db.session_scope() as session:
                locs = session.query(Locataire).all()
                
                self.locataire_combo.clear()
                self.locataire_combo.addItem("", None)
                
                for loc in locs:
                    self.locataire_combo.addItem(f"{loc.nom} ({loc.raison_sociale or loc.cin})", loc.id)
                    
        except Exception as e:
            print(f"Erreur: {e}")
            
    def load_bureaux(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Bureau, Immeuble, Contrat
            from sqlalchemy.orm import joinedload
            
            db = get_database()
            with db.session_scope() as session:
                if self.contrat_id:
                    ctr = session.query(Contrat).get(self.contrat_id)
                    if ctr:
                        existing_bureau_ids = [b.id for b in ctr.bureaux]
                        
                        active_bureaux = session.query(Bureau).options(
                            joinedload(Bureau.immeuble)
                        ).filter(
                            ~Bureau.contrats.any(Contrat.est_resilie_col == False)
                        ).order_by(Bureau.numero).all()
                        
                        existing_bureaux = session.query(Bureau).options(
                            joinedload(Bureau.immeuble)
                        ).filter(Bureau.id.in_(existing_bureau_ids)).all()
                        
                        all_bureaux = active_bureaux + existing_bureaux
                    else:
                        all_bureaux = []
                else:
                    all_bureaux = session.query(Bureau).options(
                        joinedload(Bureau.immeuble)
                    ).filter(
                        ~Bureau.contrats.any(Contrat.est_resilie_col == False)
                    ).order_by(Bureau.numero).all()
                
                self.bureaux_list.clear()
                existing_ids = set()
                
                for bur in all_bureaux:
                    if bur.id in existing_ids:
                        continue
                    existing_ids.add(bur.id)
                    
                    img_name = bur.immeuble.nom if bur.immeuble else "N/A"
                    item = QListWidgetItem(f"#{bur.numero} - {img_name} ({bur.surface_m2 or 0} m²)")
                    item.setData(Qt.UserRole, bur.id)
                    self.bureaux_list.addItem(item)
                    
        except Exception as e:
            print(f"Erreur: {e}")
            
    def load_data(self):
        try:
            from app.database.connection import get_database
            from app.models.entities import Contrat
            
            db = get_database()
            with db.session_scope() as session:
                ctr = session.query(Contrat).get(self.contrat_id)
                if ctr:
                    idx = self.locataire_combo.findData(ctr.Locataire_id)
                    if idx >= 0:
                        self.locataire_combo.setCurrentIndex(idx)
                        
                    for i in range(self.bureaux_list.count()):
                        item = self.bureaux_list.item(i)
                        bur_id = item.data(Qt.UserRole)
                        if any(b.id == bur_id for b in ctr.bureaux):
                            item.setSelected(True)
                            
                    self.date_debut.setDate(QDate(ctr.date_debut.year, ctr.date_debut.month, ctr.date_debut.day))
                    
                    if ctr.date_derniere_augmentation:
                        self.date_derniere_augmentation.setDate(QDate(
                            ctr.date_derniere_augmentation.year, 
                            ctr.date_derniere_augmentation.month, 
                            ctr.date_derniere_augmentation.day
                        ))
                        
                    self.montant_premier_mois.setValue(float(ctr.montant_premier_mois or 0))
                    self.montant_mensuel.setValue(float(ctr.montant_mensuel or 0))
                    self.montant_caution.setValue(float(ctr.montant_caution or 0))
                    self.montant_pas_de_porte.setValue(float(ctr.montant_pas_de_porte or 0))
                    
                    self.compteur_steg_edit.setText(ctr.compteur_steg or "")
                    self.compteur_sonede_edit.setText(ctr.compteur_sonede or "")
                    self.conditions_edit.setText(ctr.conditions or "")
                    
                    self.est_resilie_col.setChecked(ctr.est_resilie_col or False)
                    if ctr.date_resiliation:
                        self.date_resiliation.setDate(QDate(
                            ctr.date_resiliation.year, 
                            ctr.date_resiliation.month, 
                            ctr.date_resiliation.day
                        ))
                    self.motif_resiliation_edit.setText(ctr.motif_resiliation or "")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            
    def validate_and_accept(self):
        loc_id = self.locataire_combo.currentData()
        
        if loc_id is None:
            QMessageBox.warning(self, "Validation", "Le locataire est obligatoire")
            return
            
        selected_bureaux = [item.data(Qt.UserRole) for item in self.bureaux_list.selectedItems()]
        if not selected_bureaux:
            QMessageBox.warning(self, "Validation", "Sélectionnez au moins un bureau")
            return
            
        try:
            from app.database.connection import get_database
            from app.models.entities import Contrat, Bureau, Locataire, StatutLocataire
            from app.repositories.contrat_repository import ContratRepository
            from sqlalchemy import func
            
            db = get_database()
            with db.session_scope() as session:
                if self.contrat_id:
                    repo = ContratRepository(session)
                    ctr = repo.get_by_id(self.contrat_id)
                    if ctr:
                        old_resilie = ctr.est_resilie_col
                        old_loc_id = ctr.Locataire_id
                        repo.update(ctr,
                            Locataire_id=loc_id,
                            date_debut=self.date_debut.date().toPython(),
                            est_resilie_col=self.est_resilie_col.isChecked(),
                            date_derniere_augmentation=self.date_derniere_augmentation.date().toPython() if self.date_derniere_augmentation.date().isValid() else None,
                            montant_premier_mois=self.montant_premier_mois.value(),
                            montant_mensuel=self.montant_mensuel.value(),
                            montant_caution=self.montant_caution.value(),
                            montant_pas_de_porte=self.montant_pas_de_porte.value(),
                            compteur_steg=self.compteur_steg_edit.text().strip() or None,
                            compteur_sonede=self.compteur_sonede_edit.text().strip() or None,
                            conditions=self.conditions_edit.toPlainText().strip() or None,
                            date_resiliation=self.date_resiliation.date().toPython() if self.date_resiliation.date().isValid() else None,
                            motif_resiliation=self.motif_resiliation_edit.toPlainText().strip() or None
                        )
                        
                        selected_bureaux_objs = session.query(Bureau).filter(Bureau.id.in_(selected_bureaux)).all()
                        ctr.bureaux = selected_bureaux_objs
                        session.flush()
                        
                        for check_loc_id in set([loc_id, old_loc_id]):
                            if check_loc_id:
                                active_count = session.query(func.count(Contrat.id)).filter(
                                    Contrat.Locataire_id == check_loc_id,
                                    Contrat.est_resilie_col == False
                                ).scalar()
                                loc = session.query(Locataire).get(check_loc_id)
                                if loc:
                                    loc.statut = StatutLocataire.ACTIF if active_count > 0 else StatutLocataire.HISTORIQUE
                else:
                    repo = ContratRepository(session)
                    ctr = repo.create(
                        Locataire_id=loc_id,
                        date_debut=self.date_debut.date().toPython(),
                        date_derniere_augmentation=self.date_derniere_augmentation.date().toPython() if self.date_derniere_augmentation.date().isValid() else None,
                        montant_premier_mois=self.montant_premier_mois.value(),
                        montant_mensuel=self.montant_mensuel.value(),
                        montant_caution=self.montant_caution.value(),
                        montant_pas_de_porte=self.montant_pas_de_porte.value(),
                        compteur_steg=self.compteur_steg_edit.text().strip() or None,
                        compteur_sonede=self.compteur_sonede_edit.text().strip() or None,
                        conditions=self.conditions_edit.toPlainText().strip() or None,
                        est_resilie_col=self.est_resilie_col.isChecked(),
                        date_resiliation=self.date_resiliation.date().toPython() if self.date_resiliation.date().isValid() else None,
                        motif_resiliation=self.motif_resiliation_edit.toPlainText().strip() or None
                    )
                    
                    selected_bureaux_objs = session.query(Bureau).filter(Bureau.id.in_(selected_bureaux)).all()
                    ctr.bureaux = selected_bureaux_objs
                    
                    loc = session.query(Locataire).get(loc_id)
                    if loc:
                        loc.statut = StatutLocataire.ACTIF
                    
                self.accept()
                
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
