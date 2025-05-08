# check_history.py

import sqlite3
import pandas as pd

# Connexion à la base SQLite
conn = sqlite3.connect('data/alerts.db')

# Lecture de la table alerts
df_sql = pd.read_sql_query("SELECT * FROM alerts", conn)
conn.close()

print("=== Contenu de data/alerts.db (SQLite) ===")
print(df_sql.to_string(index=False))

# Lecture du CSV
print("\n=== Contenu de data/alerts.csv ===")
df_csv = pd.read_csv('data/alerts.csv', header=None,
                     names=['timestamp','symbol','score','confidence'])
print(df_csv.to_string(index=False))
