# gui/tabs/performance_tab.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import QThreadPool
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplcursors

from gui.worker import Worker
from api.api import get_ohlcv
from analysis.technical_analysis import compute_indicators
from analysis.performance import compute_performance
from backtest_multi import load_config, run_backtest_multi, summarize

class PerformanceTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.threadpool = QThreadPool()

        layout = QVBoxLayout(self)

        # Dropdown timeframe (pour backtest_multi) ou symbole (pour chart)  
        self.combo = QComboBox()
        # on combine : d'abord paires symboles, puis timeframes
        for sym in config["symbols"]:
            self.combo.addItem(f"Chart: {sym}")
        for tf in config.get("timeframes", [config["timeframe"]]):
            self.combo.addItem(f"Backtest: {tf}")
        layout.addWidget(self.combo)

        # Canvas Matplotlib
        self.fig = Figure(figsize=(5,3))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas, stretch=2)

        # Table résumé
        self.table = QTableWidget()
        layout.addWidget(self.table, stretch=1)

        # Connect
        self.combo.currentTextChanged.connect(self.start_analysis)

        # Initial
        if self.combo.count()>0:
            self.start_analysis(self.combo.currentText())

    def start_analysis(self, key: str):
        worker = Worker(self.run_analysis, key)
        worker.signals.result.connect(self.on_result)
        worker.signals.error.connect(self.on_error)
        self.threadpool.start(worker)

    def run_analysis(self, key: str):
        # Distinction chart vs backtest
        if key.startswith("Chart:"):
            sym = key.split("Chart:")[1].strip()
            df = get_ohlcv(sym, self.config["timeframe"])
            if df is None or df.empty:
                raise ValueError(f"No data for {sym}")
            df = compute_indicators(df, self.config["indicators"])
            # compute returns/performance
            returns = df["close"].pct_change().fillna(0)
            perf_df, stats = compute_performance(returns)
            return ("chart", sym, perf_df, stats)
        else:
            # backtest_multi
            # key like "Backtest: 1h" → override timeframe in config
            tf = key.split("Backtest:")[1].strip()
            cfg2 = self.config.copy()
            cfg2["timeframe"] = tf
            df_bt = run_backtest_multi(cfg2)    # DataFrame multi‑periods
            summary = summarize(df_bt)          # DataFrame summary
            return ("table", tf, summary)

    def on_result(self, result):
        mode = result[0]
        if mode == "chart":
            _, sym, perf_df, stats = result
            self._update_chart(sym, perf_df, stats)
            # clear table
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
        else:
            _, tf, summary = result
            # clear chart
            self.fig.clear()
            self.canvas.draw()
            # update table
            self._update_table(summary)

    def on_error(self, err):
        e, tb = err
        QMessageBox.critical(self, "PerformanceTab Error", str(e))

    def _update_chart(self, symbol, perf_df, stats):
        self.fig.clear()
        ax1 = self.fig.add_subplot(211)
        perf_df["equity"].plot(ax=ax1, title=f"Equity – {symbol}")
        ax1.set_ylabel("Equity")
        ax2 = self.fig.add_subplot(212)
        perf_df["drawdown"].plot(ax=ax2, title="Drawdown")
        ax2.set_ylabel("Drawdown")
        # annotation stats
        txt = "\n".join(f"{k}: {v:.2%}" for k,v in stats.items())
        ax1.text(0.01,0.95,txt,transform=ax1.transAxes, va="top")
        mplcursors.cursor(ax1.lines+ax2.lines, hover=True)
        self.canvas.draw()

    def _update_table(self, df):
        cols = list(df.columns)
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.setRowCount(len(df))
        for i,row in df.iterrows():
            for j,col in enumerate(cols):
                val = row[col]
                disp = f"{val:.2%}" if isinstance(val,float) else str(val)
                self.table.setItem(i,j,QTableWidgetItem(disp))
        self.table.resizeColumnsToContents()
