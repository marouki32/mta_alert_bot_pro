# notifications/telegram_bot.py

import os
from dotenv import load_dotenv

# Charge les variables d’environnement depuis le fichier .env (à la racine)
load_dotenv()

try:
    from telegram import Bot
except ImportError:
    Bot = None

# Récupérer token et chat_id depuis l'environnement
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID        = os.getenv('TELEGRAM_CHAT_ID')

# Si tout est présent et que la lib est dispo, instancie le bot
if Bot and TELEGRAM_TOKEN and CHAT_ID:
    bot = Bot(token=TELEGRAM_TOKEN)
else:
    bot = None
    print("Warning: Telegram credentials not set or python-telegram-bot missing. Telegram disabled.")

def send_telegram(message: str):
    """
    Envoie un message sur Telegram si bot configuré,
    sinon affiche en console.
    """
    if bot:
        bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        # debug ou log
        print(f"[Telegram disabled] {message}")
