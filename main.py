#!/usr/bin/env python3
import sys
import os
import json
from PyQt5.QtWidgets import QApplication
# scheduler pour le digest
from apscheduler.schedulers.background import BackgroundScheduler
from notifications.daily_digest import send_daily_digest
from gui.window import MainWindow

# 1) Configuration par défaut si le fichier n'existe pas
DEFAULT_CONFIG = {
    "symbols": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "BTC-USD"],
    "timeframe": "1h",
    "indicators": {
        "rsi": 14,
        "ema": [20, 50],
        "bollinger": {"window": 20, "std": 2}
    },
    "alerts": {
        "confidence_threshold": 0.75,
        "score_threshold": 2.0
    }
}

def ensure_config_file():
    """Crée data/config.json avec DEFAULT_CONFIG si absent."""
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", "config.json")
    if not os.path.isfile(path):
        with open(path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"⚙️  Fichier de configuration créé avec les valeurs par défaut ({path})")

def validate_config(cfg):
    """Vérifie que cfg a bien les clés et types attendus."""
    inds = cfg.get("indicators")
    if not isinstance(inds, dict):
        print("❌ ERREUR CONFIG: 'indicators' doit être un dict, pas une liste.")
        return False
    if "rsi" not in inds or not isinstance(inds["rsi"], int):
        print("❌ ERREUR CONFIG: 'indicators.rsi' manquant ou non entier.")
        return False
    if "ema" not in inds or not isinstance(inds["ema"], list):
        print("❌ ERREUR CONFIG: 'indicators.ema' manquant ou non liste.")
        return False
    bb = inds.get("bollinger")
    if not isinstance(bb, dict) or "window" not in bb or "std" not in bb:
        print("❌ ERREUR CONFIG: 'indicators.bollinger' doit être un dict avec 'window' et 'std'.")
        return False

    al = cfg.get("alerts")
    if not isinstance(al, dict) or "confidence_threshold" not in al:
        print("❌ ERREUR CONFIG: 'alerts.confidence_threshold' manquant.")
        return False

    syms = cfg.get("symbols")
    if not isinstance(syms, list) or len(syms) == 0:
        print("❌ ERREUR CONFIG: 'symbols' doit être une liste non vide.")
        return False

    return True

def load_and_validate_config():
    ensure_config_file()
    path = os.path.join("data", "config.json")
    with open(path) as f:
        cfg = json.load(f)
    if not validate_config(cfg):
        sys.exit(1)
    return cfg   # ← bien indenté dans la fonction

def main():
    # Charge et valide la config
    config = load_and_validate_config()

    # ── Scheduler pour digest quotidien Telegram ─────────────────────────────
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_digest, trigger="cron", hour=0, minute=0)
    scheduler.start()
    # ──────────────────────────────────────────────────────────────────────────

    # Démarrage de l'application PyQt5
    app = QApplication(sys.argv)

    # ── Charger le style sombre (dark.qss) ────────────────────────────────────
    qss = os.path.join(os.path.dirname(__file__), "dark.qss")
    if os.path.isfile(qss):
        with open(qss, "r") as f:
            app.setStyleSheet(f.read())
    # ──────────────────────────────────────────────────────────────────────────

    window = MainWindow(config)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
