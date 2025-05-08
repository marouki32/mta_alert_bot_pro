# gui/tabs/performance_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
import pandas as pd
from backtest_multi import load_config, run_backtest_multi, summarize

class PerformanceTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Table widget
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Charger et afficher les stats
        self.refresh()

    def refresh(self):
        # Charge config et backtest multi
        cfg = load_config()
        df = run_backtest_multi(cfg)
        stats = summarize(df)

        # Préparer le QTableWidget
        # colonnes : timeframe, period, total, alerts, win_rate, avg_confidence
        self.table.setColumnCount(len(stats.columns))
        self.table.setHorizontalHeaderLabels(list(stats.columns))
        self.table.setRowCount(len(stats))

        # Remplir
        for i, row in stats.iterrows():
            for j, col in enumerate(stats.columns):
                val = row[col]
                # formater win_rate en % et confid en %
                if col == 'win_rate':
                    disp = f"{val*100:.1f}%"
                elif col == 'avg_confidence':
                    disp = f"{val*100:.1f}%"
                else:
                    disp = str(val)
                self.table.setItem(i, j, QTableWidgetItem(disp))

        self.table.resizeColumnsToContents()
