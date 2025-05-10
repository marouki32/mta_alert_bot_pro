# notifications/daily_digest.py

import sqlite3
from datetime import datetime, timedelta
from notifications.telegram_bot import send_telegram

def generate_daily_digest(db_path="data/alerts.db") -> str:
    """
    Construit un résumé des alertes des dernières 24 heures.
    Retourne le message prêt à envoyer sur Telegram.
    """
    # 1) Ouvrir la base
    conn = sqlite3.connect(db_path)
    # 2) Sélectionner les alertes récentes
    since = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    rows = conn.execute(
        "SELECT timestamp, symbol, score FROM alerts WHERE timestamp >= ? ORDER BY timestamp",
        (since,)
    ).fetchall()
    conn.close()

    # 3) Si aucune alerte
    if not rows:
        return "📭 Aucune alerte dans les dernières 24 heures."

    # 4) Construire le texte
    header = f"📊 Digest quotidien – {datetime.utcnow():%Y-%m-%d}\n"
    total   = len(rows)
    wins    = len([s for _,_,s in rows if s > 0])
    win_rate= round(100 * wins / total, 1)
    stats   = f"{total} alertes | Win rate : {win_rate}%\n\n"
    lines   = [f"{ts} – {sym} : {score:.2f}" for ts, sym, score in rows]
    body    = "\n".join(lines)
    return header + stats + body

def send_daily_digest():
    """
    Génère le digest et l'envoie sur Telegram.
    """
    message = generate_daily_digest()
    send_telegram(message)
