# gui/tabs/paper_trading_tab.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QPushButton, QSizePolicy
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from api.api import get_ohlcv
from analysis.technical_analysis import compute_indicators
from analysis.paper_trading import run_paper_trading


class PaperTradingTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config

        layout = QVBoxLayout(self)

        # Sélecteur de symbole
        self.combo = QComboBox()
        for s in config['symbols']:
            self.combo.addItem(s)
        layout.addWidget(self.combo)

        # Bouton lancer
        self.btn = QPushButton("Démarrer Paper-Trading")
        self.btn.clicked.connect(self.on_run)
        layout.addWidget(self.btn)

        # Canvas pour equity curve
        self.fig = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        # remplir l’espace
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas)

    def on_run(self):
        symbol = self.combo.currentText()

        # 1) Récupérer les données et calculer indicateurs
        df = get_ohlcv(symbol, self.config['timeframe'])
        if df is None or df.empty:
            print(f"Aucune donnée pour {symbol}")
            return
        df = compute_indicators(df, self.config['indicators'])

        # 2) Lancer la simulation
        hist = run_paper_trading(df, self.config)

        # 3) Tracer l’equity curve
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # filtrer uniquement les enregistrements d’equity
        df_hist = hist.set_index('timestamp')
        equity_series = df_hist[df_hist['action'] == 'EQUITY']['equity']
        equity_series.plot(ax=ax, title=f"Paper-Trading – {symbol}")

        ax.set_ylabel("Equity")
        ax.grid(True)
        self.canvas.draw()

        # 4) Afficher le résumé des trades en console
        trades = hist[hist['action'].isin(['BUY', 'SELL'])]
        print("\n=== Trades exécutés ===")
        print(trades.to_string(index=False))
        final = equity_series.iloc[-1]
        print(f"\nValeur finale du portefeuille : {final:.2f}")

