# gui/tabs/paper_trading_tab.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from api.api import get_ohlcv
from analysis.technical_analysis import compute_indicators
from analysis.paper_trading import run_paper_trading, simulate_binary_trading
from analysis.strategy_scoring import score_strategy

class PaperTradingTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        layout = QVBoxLayout(self)

        # Choix du symbole
        self.combo = QComboBox()
        for s in config["symbols"]:
            self.combo.addItem(s)
        layout.addWidget(self.combo)

        # Bouton
        self.btn = QPushButton("Démarrer Paper-Trading")
        self.btn.clicked.connect(self.on_run)
        layout.addWidget(self.btn)

        # Canvas
        self.fig    = Figure(figsize=(6,4))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

    def on_run(self):
        symbol = self.combo.currentText()
        df = get_ohlcv(symbol, self.config["timeframe"])
        if df is None or df.empty:
            QMessageBox.warning(self, "Paper-Trading", f"Aucune donnée pour {symbol}")
            return
        df = compute_indicators(df, self.config["indicators"])

        # 1) Calculer un score à chaque barre
        thr = self.config["alerts"]["score_threshold"]
        signals = []
        for i in range(len(df)):
            sub = df.iloc[: i+1]
            s = score_strategy(sub, patterns={})
            if s >= thr:    sig = "BUY"
            elif s <= -thr: sig = "SELL"
            else:           sig = None
            signals.append(sig)
        df["signal"] = signals

        # 2) Choix de la simulation
        if self.config.get("market_type","spot") == "binary":
            hist = simulate_binary_trading(df, self.config)
        else:
            hist = run_paper_trading(df, self.config)

        # 3) Tracer equity
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        dfh = hist.set_index("timestamp")
        eq  = dfh[dfh["action"]=="EQUITY"]["equity"]
        eq.plot(ax=ax, title=f"Paper-Trading – {symbol}")
        ax.set_ylabel("Equity"); ax.grid(True)
        self.canvas.draw()

        # 4) Console trades & final
        trades = hist[hist["action"].isin(["BUY","SELL"])]
        if not trades.empty:
            print("\n=== Trades ===")
            print(trades.to_string(index=False))
        print(f"\nValeur finale : {eq.iloc[-1]:,.2f}")

