# init_db.py

import os
import sqlite3

def init_database():
    # calculer le chemin absolu vers data/alerts.db
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir   = os.path.join(base_dir, "data")
    db_path  = os.path.join(db_dir, "alerts.db")

    # créer data/ s’il n’existe pas
    os.makedirs(db_dir, exist_ok=True)  # :contentReference[oaicite:1]{index=1}
    print(f"✅ Répertoire prêt : {db_dir}")

    # ouvrir (ou créer) la base
    conn = sqlite3.connect(db_path)     # :contentReference[oaicite:2]{index=2}
    print(f"✅ Base ouverte : {db_path}")

    # créer la table alerts si manquante
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            timestamp TEXT,
            symbol    TEXT,
            score     REAL
        )
    """)  # :contentReference[oaicite:3]{index=3}
    conn.commit()
    print("✅ Table ‘alerts’ prête")

    conn.close()

if __name__ == "__main__":
    init_database()
