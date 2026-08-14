import os
import requests
import time
import threading
from flask import Flask

app = Flask(__name__)

# APNA TOKEN AUR CHAT ID YAHAN DAALEIN
TOKEN = '8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk'
chat_id = '1179672183'

def get_syn_price():
    try:
        url = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=SYN&tsyms=USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        raw_data = data['RAW']['SYN']['USD']
        price = raw_data['PRICE']
        change = raw_data['CHANGEPCT24HOUR']
        return f"📊 SYNAPSE (SYN) Auto Update\nPrice: ${price:.4f}\n24h Change: {change:.2f}%\n"
    except Exception as e:
        return f"Error fetching data: {str(e)}"

def send_telegram():
    while True:
        message = get_syn_price()
        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(tg_url, json=payload)
        time.sleep(1200)  # Har 20 minute mein message bhejega (1200 seconds = 20 mins)

@app.route('/')
def home():
    return "Bot is running automatically every 20 minutes in background!"

if __name__ == "__main__":
    # Background thread shuru karna
    threading.Thread(target=send_telegram, daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
