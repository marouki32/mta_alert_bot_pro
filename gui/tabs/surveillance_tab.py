# gui/tabs/surveillance_tab.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget,
    QApplication, QMessageBox, QSystemTrayIcon
)
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

        # Thread‐pool pour l’analyse asynchrone
        self.threadpool = QThreadPool()

        # Layout et widgets
        layout = QVBoxLayout()
        self.symbol_list = QListWidget()
        for sym in config['symbols']:
            self.symbol_list.addItem(sym)
        if self.symbol_list.count() > 0:
            self.symbol_list.setCurrentRow(0)
        layout.addWidget(self.symbol_list)

        self.btn_analyse = QPushButton("Analyser")
        self.btn_analyse.clicked.connect(self.start_analysis)
        layout.addWidget(self.btn_analyse)

        self.setLayout(layout)

        # Créer le dossier data/ s’il n’existe pas
        os.makedirs("data", exist_ok=True)

    def start_analysis(self):
        """Lance l’analyse dans un thread de fond."""
        print("DEBUG ▶ start_analysis called")
        worker = Worker(self._run_analysis)
        worker.signals.result.connect(self.on_analysis_done)
        worker.signals.error.connect(lambda err: print(f"Worker error:\n{err[1]}"))
        self.threadpool.start(worker)

    def _run_analysis(self):
        """Code d’analyse exécuté en thread de fond."""
        current = self.symbol_list.currentItem()
        if current is None:
            return {"error": "Aucun symbole sélectionné."}
        symbol = current.text()

        # 1) OHLCV
        df = get_ohlcv(symbol, self.config['timeframe'])

        # 2) Indicateurs
        df = compute_indicators(df, self.config['indicators'])

        # 3) Patterns & score
        patterns = detect_patterns(df)
        score = score_strategy(df, patterns)
        max_score = sum(w for w in DEFAULT_WEIGHTS.values() if w > 0)
        confidence = score / max_score if max_score else 0

        print(f"DEBUG ▶ analysis done for {symbol}: score={score:.2f}, conf={confidence:.2f}")
        return {"symbol": symbol, "score": score, "confidence": confidence}

    def on_analysis_done(self, result):
        """Traitement des résultats dans le thread GUI."""
        if "error" in result:
            QMessageBox.warning(self, "Erreur", result["error"])
            return

        symbol     = result["symbol"]
        score      = result["score"]
        confidence = result["confidence"]

        # Popup résultat
        QMessageBox.information(
            self,
            "Résultat de l'analyse",
            f"Symbole : {symbol}\nScore : {score:.2f}\nConfiance : {int(confidence*100)} %"
        )

        # Si above threshold, envoi alertes
        thr = self.config['alerts']['confidence_threshold']
        if confidence >= thr:
            message = f"Alerte {symbol}: score={score:.2f}, confiance={int(confidence*100)}%"

            # Telegram
            send_telegram(message)

            # Son système
            QApplication.beep()

            # Notification tray
            tray = self.window().tray_icon
            tray.showMessage("MTA Alert Bot Pro", message, QSystemTrayIcon.Information, 5000)

            # Historique SQLite
            conn = sqlite3.connect('data/alerts.db')
            conn.execute(
                "CREATE TABLE IF NOT EXISTS alerts (timestamp TEXT, symbol TEXT, score REAL)"
            )
            conn.execute(
                "INSERT INTO alerts(timestamp, symbol, score) VALUES (datetime('now'), ?, ?)",
                (symbol, score)
            )
            conn.commit()
            conn.close()

            # Journal CSV
            with open('data/alerts.csv', 'a', newline='') as f:
                csv.writer(f).writerow([
                    datetime.now().isoformat(),
                    symbol,
                    round(score, 2),
                    int(confidence * 100)
                ])
