# gui/tabs/export_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
import pandas as pd
import sqlite3
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from notifications.exporter import export_to_excel, export_to_pdf

class ExportTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Bouton Excel
        self.btn_excel = QPushButton("Exporter l'historique en Excel")
        self.btn_excel.clicked.connect(self.export_excel)
        layout.addWidget(self.btn_excel)

        # Bouton PDF
        self.btn_pdf = QPushButton("Exporter l'historique en PDF")
        self.btn_pdf.clicked.connect(self.export_pdf)
        layout.addWidget(self.btn_pdf)

    def load_history_df(self):
        # Charge la table SQLite dans un DataFrame
        conn = sqlite3.connect('data/alerts.db')
        df = pd.read_sql_query("SELECT * FROM alerts ORDER BY timestamp DESC", conn)
        conn.close()
        return df

    def export_excel(self):
        df = self.load_history_df()
        # Boîte de dialogue pour choisir le fichier
        path, _ = QFileDialog.getSaveFileName(self, "Enregistrer Excel", "", "Excel Files (*.xlsx)")
        if not path:
            return
        try:
            df.to_excel(path, index=False)
            QMessageBox.information(self, "Export Excel", f"Succès : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Excel", str(e))

    def export_pdf(self):
        df = self.load_history_df()
        path, _ = QFileDialog.getSaveFileName(self, "Enregistrer PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        try:
            # Construction du PDF
            doc = SimpleDocTemplate(path, pagesize=letter)
            styles = getSampleStyleSheet()
            elems = []

            # Titre
            elems.append(Paragraph("Historique des alertes", styles['Title']))

            # Préparer les données pour Table
            data = [df.columns.tolist()] + df.values.tolist()
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ]))
            elems.append(table)

            doc.build(elems)
            QMessageBox.information(self, "Export PDF", f"Succès : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur PDF", str(e))
