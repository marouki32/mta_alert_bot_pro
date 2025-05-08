from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QApplication, QMessageBox, QSystemTrayIcon
from PyQt5.QtCore import QThreadPool
from gui.worker import Worker

from api.api import get_ohlcv
from analysis.technical_analysis import compute_indicators, detect_patterns
from analysis.strategy_scoring import score_strategy, DEFAULT_WEIGHTS
from notifications.telegram_bot import send_telegram

import sqlite3, csv, os
from datetime import datetime

class SurveillanceTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.threadpool = QThreadPool()

        layout = QVBoxLayout()
        self.symbol_list = QListWidget()
        for sym in config['symbols']:
            self.symbol_list.addItem(sym)
        if self.symbol_list.count()>0:
            self.symbol_list.setCurrentRow(0)
        layout.addWidget(self.symbol_list)

        self.btn_analyse = QPushButton("Analyser")
        self.btn_analyse.clicked.connect(self.start_analysis)
        layout.addWidget(self.btn_analyse)

        self.setLayout(layout)
        os.makedirs("data", exist_ok=True)

    def start_analysis(self):
        print("DEBUG ▶ start_analysis called")
        worker = Worker(self._run_analysis)
        worker.signals.result.connect(self.on_analysis_done)           # ← ici
        worker.signals.error.connect(lambda err: print(f"Worker error:\n{err[1]}"))
        self.threadpool.start(worker)

    def _run_analysis(self):
        # Exécuté dans le thread de fond
        current = self.symbol_list.currentItem()
        if current is None:
            return {"error":"Aucun symbole sélectionné."}
        symbol = current.text()

        df = get_ohlcv(symbol, self.config['timeframe'])
        df = compute_indicators(df, self.config['indicators'])
        patterns = detect_patterns(df)
        score = score_strategy(df, patterns)
        max_score = sum(w for w in DEFAULT_WEIGHTS.values() if w>0)
        confidence = score/max_score if max_score else 0

        print(f"DEBUG ▶ analysis done for {symbol}: score={score}, conf={confidence}")
        return {"symbol":symbol, "score":score, "confidence":confidence}

    def on_analysis_done(self, result):
        # Exécuté dans le thread GUI
        if "error" in result:
            QMessageBox.warning(self, "Erreur", result["error"])
            return

        symbol    = result["symbol"]
        score     = result["score"]
        confidence= result["confidence"]

        QMessageBox.information(
            self,
            "Résultat de l'analyse",
            f"Symbole : {symbol}\nScore : {score:.2f}\nConfiance : {int(confidence*100)} %"
        )

        thr = self.config['alerts']['confidence_threshold']
        if confidence >= thr:
            message = f"Alerte {symbol}: score={score:.2f}, confiance={int(confidence*100)}%"
            send_telegram(message)
            QApplication.beep()
            self.window().tray_icon.showMessage("MTA Alert Bot Pro", message, QSystemTrayIcon.Information, 5000)

            conn = sqlite3.connect('data/alerts.db')
            conn.execute("CREATE TABLE IF NOT EXISTS alerts (timestamp TEXT, symbol TEXT, score REAL)")
            conn.execute("INSERT INTO alerts(timestamp, symbol, score) VALUES (datetime('now'), ?, ?)",
                         (symbol, score))
            conn.commit(); conn.close()

            with open('data/alerts.csv','a',newline='') as f:
                csv.writer(f).writerow([datetime.now().isoformat(), symbol, round(score,2), int(confidence*100)])
