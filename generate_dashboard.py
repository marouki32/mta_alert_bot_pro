# generate_dashboard.py

import sqlite3
from datetime import datetime
import jinja2
import os

# 1) Charger les alertes depuis SQLite
conn = sqlite3.connect("data/alerts.db")
cur = conn.execute(
    "SELECT timestamp, symbol, score FROM alerts ORDER BY timestamp DESC LIMIT 50"
)
alerts = [
    {"timestamp": row[0], "symbol": row[1], "score": row[2]}
    for row in cur
]
conn.close()

# 2) Calculer des stats simples
scores = [a["score"] for a in alerts]
total = len(scores)
win = len([s for s in scores if s > 0])
win_rate = round(100 * win / total, 1) if total else 0
avg = sum(scores) / total if total else 0

stats = {
    "total_alerts": total,
    "win_rate": win_rate,
    "avg_score": avg
}

# 3) Rendu Jinja sur les .md
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("docs"),
    autoescape=False
)
for page in ["alerts.md", "stats.md"]:
    template = env.get_template(page)
    content = template.render(alerts=alerts, stats=stats)
    with open(os.path.join("docs", page), "w") as f:
        f.write(content)

print("Dashboard sources updated.")
