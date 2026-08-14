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
        # CoinCap API for Synapse (SYN)
        url = "https://api.coincap.io/v2/assets/synapse"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'data' not in data:
            return "API Error: Synapse data not found."
            
        asset = data['data']
        price = float(asset['priceUsd'])
        change = float(asset['changePercent24Hr'])
        
        message = f"📊 SYNAPSE (SYN) Auto Update\nPrice: ${price:.4f}\n24h Change: {change:.2f}%\n"
        if change > 0:
            message += "🟢 Market is Bullish (Up)"
        else:
            message += "🔴 Market is Bearish (Down)"
            
        return message
    except Exception as e:
        return f"Error fetching data: {str(e)}"

def send_telegram():
    while True:
        message = get_syn_price()
        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(tg_url, json=payload)
        time.sleep(1200)  # Har 20 minute

@app.route('/')
def home():
    return "Bot is running automatically every 20 minutes in background!"

if __name__ == "__main__":
    threading.Thread(target=send_telegram, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
