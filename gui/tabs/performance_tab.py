# gui/tabs/performance_tab.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSplitter, QSizePolicy, QLabel, QTableView
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplcursors
import pandas as pd

from api.api import get_ohlcv
from analysis.technical_analysis import compute_indicators
from analysis.performance import compute_performance

class PerformanceTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config

        # Splitter vertical : top=chart (60%), bottom=table (40%)
        splitter = QSplitter(Qt.Vertical)

        # === Chart Section (60%) ===
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)

        # Symbole dropdown
        self.combo = QComboBox()
        for sym in config["symbols"]:
            self.combo.addItem(sym)
        chart_layout.addWidget(self.combo)

        # Matplotlib canvas
        self.fig = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chart_layout.addWidget(self.canvas)

        splitter.addWidget(chart_widget)
        splitter.setStretchFactor(0, 3)  # 3 parts vs 2

        # === Table Section (40%) ===
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)

        label = QLabel("Résumé backtest multi-périodes")
        table_layout.addWidget(label)

        self.table = QTableView()
        table_layout.addWidget(self.table)

        splitter.addWidget(table_widget)
        splitter.setStretchFactor(1, 2)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(splitter)

        # Connexion
        self.combo.currentTextChanged.connect(self.update)

        # Tracé initial
        if self.combo.count() > 0:
            self.update(self.combo.currentText())

    def update(self, symbol):
        """Recharge les données, backtest, et met à jour chart+table."""
        # 1) OHLCV + indicateurs
        df = get_ohlcv(symbol, self.config["timeframe"])
        if df is None or df.empty:
            return
        df = compute_indicators(df, self.config["indicators"])

        # 2) Performance
        returns = df["close"].pct_change().fillna(0)
        perf_df, stats = compute_performance(returns)

        # 3) Tracer le chart
        self.fig.clear()
        ax1 = self.fig.add_subplot(211)
        perf_df["equity"].plot(ax=ax1, title=f"Equity Curve – {symbol}")
        ax1.set_ylabel("Equity")

        ax2 = self.fig.add_subplot(212, sharex=ax1)
        perf_df["drawdown"].plot(ax=ax2, title="Drawdown")
        ax2.set_ylabel("Drawdown")

        # Rendre les dates lisibles
        for ax in (ax1, ax2):
            ax.xaxis.set_tick_params(rotation=30)
            ax.grid(True)

        # Curseur interactif
        mplcursors.cursor(ax1.lines + ax2.lines, hover=True)

        self.canvas.draw()

        # 4) Mettre à jour le table model
        # On transforme stats en DataFrame d’une seule ligne
        stats_df = pd.DataFrame([stats])
        # Utilise un model pandas pour QTableView
        model = PandasModel(stats_df)
        self.table.setModel(model)
        self.table.resizeColumnsToContents()

# Helper pour afficher un DataFrame dans QTableView
from PyQt5.QtCore import QAbstractTableModel, QVariant

class PandasModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            val = self._df.iloc[index.row(), index.column()]
            # formater pourcentages
            if "rate" in self._df.columns[index.column()]:
                return f"{val*100:.1f}%"
            return str(val)
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            else:
                return str(section)
        return QVariant()
