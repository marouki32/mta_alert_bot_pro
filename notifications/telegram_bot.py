# notifications/telegram_bot.py

import os
import telegram

# Récupérer token et chat_id depuis l'environnement
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID        = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not CHAT_ID:
    # En l’absence de configuration, on désactive Telegram mais on n’échoue pas à l’import
    print("Warning: Telegram credentials not set. Telegram alerts will be disabled.")
    Bot = None
else:
    Bot = telegram.Bot(token=TELEGRAM_TOKEN)

def send_telegram(message: str):
    """
    Envoie un message sur Telegram si Bot est configuré,
    sinon logue en console.
    """
    if Bot:
        Bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        # debug ou log
        print(f"[Telegram disabled] {message}")
