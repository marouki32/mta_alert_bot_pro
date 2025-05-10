# gui/tabs/chart_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QMessageBox
from PyQt5.QtCore import QThreadPool
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplcursors

from api.api import get_ohlcv
from analysis.technical_analysis import compute_indicators
from gui.worker import Worker

class ChartTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.threadpool = QThreadPool()

        # Layout
        layout = QVBoxLayout(self)

        # Dropdown symbole
        self.combo = QComboBox()
        for sym in config['symbols']:
            self.combo.addItem(sym)
        layout.addWidget(self.combo)

        # Matplotlib Figure & Canvas
        self.fig = Figure(figsize=(5,4))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Connect change
        self.combo.currentTextChanged.connect(self.start_plot)

        # Plot initial
        if self.combo.count()>0:
            self.start_plot(self.combo.currentText())

    def start_plot(self, symbol):
        """Lance le worker pour fetch & tracer."""
        worker = Worker(self.run_plot, symbol)
        worker.signals.error.connect(self.on_error)
        worker.signals.result.connect(self.on_plot_ready)
        self.threadpool.start(worker)

    def run_plot(self, symbol):
        """Code exécuté en thread de fond."""
        # 1) fetch
        df = get_ohlcv(symbol, self.config['timeframe'])
        if df is None or df.empty:
            raise ValueError(f"Aucune donnée pour {symbol}")
        # 2) indicateurs
        df = compute_indicators(df, self.config['indicators'])
        return (symbol, df)

    def on_plot_ready(self, result):
        """Mise à jour du plot dans le thread GUI."""
        symbol, df = result
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        # close
        ax.plot(df.index, df['close'], label='Close')
        # EMAs
        for col in df.columns:
            if col.startswith('ema_'):
                ax.plot(df.index, df[col], label=col)
        # Bollinger
        if 'bb_upper' in df and 'bb_lower' in df:
            ax.plot(df.index, df['bb_upper'], '--', label='BB upper')
            ax.plot(df.index, df['bb_lower'], '--', label='BB lower')
        ax.set_title(symbol)
        ax.legend()
        ax.grid(True)
        # interactive cursors
        mplcursors.cursor(ax.lines, hover=True)
        self.canvas.draw()

    def on_error(self, err):
        """Affiche l’erreur dans un QMessageBox."""
        e, tb = err
        QMessageBox.critical(self, "Erreur ChartTab", str(e))
