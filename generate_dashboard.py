import os
import sqlite3
import subprocess
import jinja2

# 1) chemin absolu vers data/alerts.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # :contentReference[oaicite:4]{index=4}
DB_PATH  = os.path.join(BASE_DIR, "data", "alerts.db")

# 2) initialiser la base et la table
subprocess.run(["python", os.path.join(BASE_DIR, "init_db.py")], check=True)

# 3) se connecter à la base (table garantie)
conn = sqlite3.connect(DB_PATH)

# 4) (Optionnel) ré-création safe de la table — redondant mais sans danger
conn.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        timestamp TEXT,
        symbol    TEXT,
        score     REAL
    )
""")
conn.commit()

# 5) Charger les alertes
cur = conn.execute(
    "SELECT timestamp, symbol, score FROM alerts ORDER BY timestamp DESC LIMIT 50"
)
alerts = [{"timestamp": r[0], "symbol": r[1], "score": r[2]} for r in cur]
conn.close()

# 6) Calcul des stats
scores   = [a["score"] for a in alerts]
total    = len(scores)
win_rate = round(100 * len([s for s in scores if s>0]) / total,1) if total else 0
avg_score= sum(scores)/total if total else 0
stats    = {"total_alerts": total, "win_rate": win_rate, "avg_score": avg_score}

# 7) Rendu Jinja pour docs/*.md
env = jinja2.Environment(loader=jinja2.FileSystemLoader("docs"), autoescape=False)
for page in ["alerts.md","stats.md"]:
    tpl     = env.get_template(page)
    content = tpl.render(alerts=alerts, stats=stats)
    with open(os.path.join("docs", page),"w") as f:
        f.write(content)

print("✅ Dashboard sources updated.")
