import sqlite3
from datetime import datetime, timedelta
from notifications.telegram_bot import send_telegram

def generate_daily_digest(db_path="data/alerts.db") -> str:
    conn = sqlite3.connect(db_path)
    since = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    rows = conn.execute(
        "SELECT timestamp, symbol, score FROM alerts WHERE timestamp >= ? ORDER BY timestamp",
        (since,)
    ).fetchall()
    conn.close()

    if not rows:
        return "📭 Aucune alerte dans les dernières 24 heures."

    header = f"📊 Digest quotidien – {datetime.utcnow():%Y-%m-%d}\n"
    total   = len(rows)
    wins    = len([s for _,_,s in rows if s > 0])
    win_rate= round(100 * wins / total, 1)
    stats   = f"{total} alertes | Win rate : {win_rate}%\n\n"
    lines   = [f"{ts} – {sym} : {score:.2f}" for ts, sym, score in rows]
    return header + stats + "\n".join(lines)

def send_daily_digest():
    msg = generate_daily_digest()
    send_telegram(msg)
