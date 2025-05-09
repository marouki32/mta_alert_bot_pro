# init_db.py

import os
import sqlite3

def init_database():
    # 1) Construire le chemin absolu vers data/alerts.db
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, "data")
    db_path = os.path.join(db_dir, "alerts.db")

    # 2) Créer le dossier data/ s’il n’existe pas
    os.makedirs(db_dir, exist_ok=True)
    print(f"✅ Répertoire créé ou existant : {db_dir}")

    # 3) Se connecter (va créer alerts.db s’il n’existe pas)
    conn = sqlite3.connect(db_path)
    print(f"✅ Base de données ouverte : {db_path}")

    # 4) Créer la table alerts si besoin
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            timestamp TEXT,
            symbol    TEXT,
            score     REAL
        )
    """)
    conn.commit()
    print("✅ Table ‘alerts’ créée ou déjà existante")

    conn.close()

if __name__ == "__main__":
    init_database()
