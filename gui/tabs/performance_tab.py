# gui/tabs/performance_tab.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import QThreadPool
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplcursors
import matplotlib.dates as mdates

from gui.worker import Worker
from api.api import get_ohlcv
from analysis.technical_analysis import compute_indicators
from analysis.performance import compute_performance
from backtest_multi import run_backtest_multi, summarize

class PerformanceTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.threadpool = QThreadPool()

        # ─── Layout principal ────────────────────────────────────
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # 1) Sélecteur Chart / Backtest (pas de stretch)
        self.combo = QComboBox()
        self.combo.addItem("--- Sélectionnez une vue ---")
        for s in config["symbols"]:
            self.combo.addItem(f"Chart:   {s}")
        for tf in config.get("timeframes", [config["timeframe"]]):
            self.combo.addItem(f"Backtest: {tf}")
        layout.addWidget(self.combo,       stretch=0)

        # 2) Zone graphique (≈ 60 % de la hauteur)
        self.fig    = Figure(figsize=(5,3))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas,      stretch=3)

        # 3) Tableau résumé (≈ 40 % de la hauteur)
        self.table  = QTableWidget()
        layout.addWidget(self.table,       stretch=2)

        # Connexion
        self.combo.currentTextChanged.connect(self.start_analysis)

        # Analyse initiale
        if self.combo.count()>0:
            self.start_analysis(self.combo.currentText())

    # ─── Lancement en arrière‑plan ───────────────────────────
    def start_analysis(self, key: str):
        if "Chart:" in key or "Backtest:" in key:
            worker = Worker(self.run_analysis, key)
            worker.signals.result.connect(self.on_result)
            worker.signals.error .connect(self.on_error)
            self.threadpool.start(worker)

    # ─── Code du Worker ──────────────────────────────────────
    def run_analysis(self, key: str):
        if key.startswith("Chart:"):
            sym = key.split(":")[1].strip()
            df  = get_ohlcv(sym, self.config["timeframe"])
            df  = compute_indicators(df, self.config["indicators"])
            returns = df["close"].pct_change().fillna(0)
            perf_df, stats = compute_performance(returns)
            return ("chart", sym, perf_df, stats)

        else:
            tf  = key.split(":")[1].strip()
            cfg2 = { **self.config, "timeframe": tf }
            df_bt   = run_backtest_multi(cfg2)
            summary = summarize(df_bt)
            return ("table", tf, summary)

    # ─── Gestion des résultats ──────────────────────────────
    def on_result(self, result):
        mode = result[0]
        if mode=="chart":
            _, sym, perf_df, stats = result
            self._update_chart(sym, perf_df, stats)
        else:
            _, tf, summary = result
            self._clear_chart()
            self._update_table(summary)

    def on_error(self, err):
        exc, _ = err
        QMessageBox.critical(self, "Erreur Performance", str(exc))

    # ─── Méthodes privées pour le chart ─────────────────────
    def _update_chart(self, sym, perf_df, stats):
        self.fig.clear()
        ax1 = self.fig.add_subplot(211)
        ax2 = self.fig.add_subplot(212)

        # Equity
        ax1.plot(perf_df.index, perf_df["equity"], label="Equity")
        ax1.set_title(f"Equity – {sym}")
        ax1.set_ylabel("Equity")
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax1.tick_params(axis='x', rotation=45)

        # Drawdown
        ax2.plot(perf_df.index, perf_df["drawdown"], label="Drawdown")
        ax2.set_title("Drawdown")
        ax2.set_ylabel("Drawdown")
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax2.tick_params(axis='x', rotation=45)

        # Stats text
        txt = "\n".join(f"{k}: {v:.2%}" for k,v in stats.items())
        ax1.text(0.01, 0.95, txt, transform=ax1.transAxes, va="top")

        # Curseurs interactifs
        mplcursors.cursor(ax1.lines + ax2.lines, hover=True)

        self.fig.tight_layout()
        self.canvas.draw()

    def _clear_chart(self):
        self.fig.clear()
        self.canvas.draw()

    # ─── Méthodes privées pour le tableau ───────────────────
    def _update_table(self, df):
        self.table.setColumnCount(len(df.columns))
        self.table.setRowCount(len(df))
        self.table.setHorizontalHeaderLabels(df.columns)

        for i, row in df.iterrows():
            for j, col in enumerate(df.columns):
                val  = row[col]
                text = f"{val:.2%}" if isinstance(val, float) else str(val)
                self.table.setItem(i, j, QTableWidgetItem(text))

        self.table.resizeColumnsToContents()
