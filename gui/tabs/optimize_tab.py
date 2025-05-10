# gui/tabs/optimize_tab.py

import subprocess
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableView, QMessageBox
)
from PyQt5.QtCore import QThreadPool, QAbstractTableModel, Qt
from gui.worker import Worker

class PandasModel(QAbstractTableModel):
    """Model Qt pour afficher un pandas.DataFrame."""
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            val = self._df.iat[index.row(), index.column()]
            return f"{val:.4f}" if isinstance(val, float) else str(val)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            else:
                return str(section + 1)

class OptimizeTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.threadpool = QThreadPool()

        layout = QVBoxLayout(self)

        # Bouton pour lancer l'optimisation
        self.btn = QPushButton("Lancer optimisation")
        layout.addWidget(self.btn)

        # Tableau pour les résultats
        self.table = QTableView()
        layout.addWidget(self.table)

        self.btn.clicked.connect(self.start_optimization)

    def start_optimization(self):
        """Démarre le worker qui exécutera optimize_params.py."""
        self.btn.setEnabled(False)
        worker = Worker(self.run_optimize)
        worker.signals.result.connect(self.on_result)
        worker.signals.error.connect(self.on_error)
        self.threadpool.start(worker)

    def run_optimize(self):
        """Execute optimize_params.py et retourne le chemin du CSV généré."""
        proc = subprocess.run(
            ["python3", "optimize_params.py"],
            capture_output=True, text=True
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr)
        # Récupérer la ligne “Results saved to …”
        for line in reversed(proc.stdout.splitlines()):
            if line.startswith(" Results saved to") or line.startswith("Results saved to"):
                return line.split("Results saved to ")[1]
        raise RuntimeError("Chemin du CSV non trouvé dans la sortie.")

    def on_result(self, csv_path):
        """Charge le CSV et l’affiche dans le QTableView."""
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            QMessageBox.critical(self, "Erreur lecture CSV", str(e))
            self.btn.setEnabled(True)
            return
        # Trier et ne garder que le top 10
        df_top = df.sort_values("win_rate", ascending=False).head(10)
        model = PandasModel(df_top)
        self.table.setModel(model)
        self.btn.setEnabled(True)

    def on_error(self, err):
        """Affiche l’erreur si optimisation échoue."""
        e, tb = err
        QMessageBox.critical(self, "Erreur optimisation", tb)
        self.btn.setEnabled(True)
