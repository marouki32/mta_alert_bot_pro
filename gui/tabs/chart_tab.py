# gui/tabs/chart_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplcursors

from api.api import get_ohlcv
from analysis.technical_analysis import compute_indicators

class ChartTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config

        # Layout vertical
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Dropdown pour choisir le symbole
        self.combo = QComboBox()
        for sym in config['symbols']:
            self.combo.addItem(sym)
        layout.addWidget(self.combo)

        # Canvas Matplotlib
        self.fig = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Quand on change de symbole, on redessine
        self.combo.currentTextChanged.connect(self.on_symbol_change)

        # Tracé initial
        if self.combo.count() > 0:
            self.on_symbol_change(self.combo.currentText())

    def on_symbol_change(self, symbol):
        # 1) Récupérer les données OHLCV
        df = get_ohlcv(symbol, self.config['timeframe'])
        # 2) Calculer les indicateurs
        df = compute_indicators(df, self.config['indicators'])

        # 3) Tracer
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(df.index, df['close'], label='Close')

        # tracer toutes les EMA
        for col in df.columns:
            if col.startswith('ema_'):
                ax.plot(df.index, df[col], label=col)

        # tracer Bollinger si présent
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            ax.plot(df.index, df['bb_upper'], '--', label='BB upper')
            ax.plot(df.index, df['bb_lower'], '--', label='BB lower')

        ax.set_title(symbol)
        ax.legend()
        ax.grid(True)

        # 4) Activer l’infobulle interactive au survol
        mplcursors.cursor(ax.lines, hover=True)

        # 5) Rafraîchir l’affichage
        self.canvas.draw()
