import os
from telegram import Bot

# Récupérer token et chat_id depuis l'environnement
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
if not TELEGRAM_TOKEN or not CHAT_ID:
    raise EnvironmentError("Telegram credentials not set. Export TELEGRAM_TOKEN and TELEGRAM_CHAT_ID.")

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram(message: str):
    """Envoie un message Telegram au chat configuré."""
    bot.send_message(chat_id=CHAT_ID, text=message)
