# notifications/telegram_bot.py

import os
import requests

# 1) Charger les credentials
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID        = os.getenv("TELEGRAM_CHAT_ID")

# 2) Construire l’URL de base
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

if not TELEGRAM_TOKEN or not CHAT_ID:
    print("Warning: Telegram credentials not set. Telegram alerts disabled.")
    ENABLED = False
else:
    ENABLED = True

def send_telegram(message: str):
    """
    Envoie un message sur Telegram de manière synchrone via requests.
    """
    if not ENABLED:
        print(f"[Telegram disabled] {message}")
        return

    url = BASE_URL + "/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        # log l’erreur sans bloquer l’UI
        print(f"[Telegram error] {e}")
