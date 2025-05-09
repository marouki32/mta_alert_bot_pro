# generate_dashboard.py

import sqlite3
import sqlite3, subprocess
import jinja2
import os

DB_PATH = "data/alerts.db"

# Initialise la base et la table
subprocess.run(["python", "init_db.py"], check=True)

# Assure-toi que le dossier existe
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 1) Ouvre (ou crée) la base, et crée la table s’il n’y en a pas
conn = sqlite3.connect(DB_PATH)
conn.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        timestamp TEXT,
        symbol    TEXT,
        score     REAL
    )
""")
conn.commit()

# 2) Charge les dernières alertes (sera vide si aucune)
cur = conn.execute(
    "SELECT timestamp, symbol, score FROM alerts ORDER BY timestamp DESC LIMIT 50"
)
alerts = [{"timestamp": r[0], "symbol": r[1], "score": r[2]} for r in cur]
conn.close()

# 3) Statistiques
scores = [a["score"] for a in alerts]
total    = len(scores)
win       = len([s for s in scores if s>0])
win_rate  = round(100*win/total,1) if total else 0
avg_score = sum(scores)/total if total else 0

stats = {
    "total_alerts": total,
    "win_rate":     win_rate,
    "avg_score":    avg_score
}

# 4) Rendu Jinja sur les MD
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("docs"),
    autoescape=False
)
for page in ["alerts.md","stats.md"]:
    tpl     = env.get_template(page)
    content = tpl.render(alerts=alerts, stats=stats)
    with open(os.path.join("docs", page),"w") as f:
        f.write(content)

print("✅ Dashboard sources updated.")
