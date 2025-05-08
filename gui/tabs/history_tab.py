# gui/tabs/history_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
import sqlite3

class HistoryTab(QWidget):
    def __init__(self, config):
        super().__init__()
        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_history()

    def load_history(self):
        # Lecture SQLite
        conn = sqlite3.connect('data/alerts.db')
        cur = conn.cursor()
        cur.execute("SELECT timestamp, symbol, score FROM alerts ORDER BY timestamp DESC")
        rows = cur.fetchall()
        conn.close()

        # Remplir le QTableWidget
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Timestamp','Symbol','Score'])
        self.table.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,val in enumerate(row):
                self.table.setItem(i,j, QTableWidgetItem(str(val)))
        self.table.resizeColumnsToContents()
