import os
import requests
from flask import Flask

app = Flask(__name__)

# APNA TOKEN AUR CHAT ID YAHAN DAALEN
TOKEN = '8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk'
chat_id = '1179672183'

@app.route('/')
def home():
    return "Bot is alive and running!"

@app.route('/trigger')
def trigger_bot():
    try:
        # Binance ki API se SYN/USDT ka data lena
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=SYNUSDT"
        response = requests.get(url, timeout=10)
        
        # Agar symbol galat ho ya error aaye
        if response.status_code != 200:
            return f"API Error: Symbol shayad Binance par 'SYNUSDT' na ho (Status: {response.status_code})"
            
        data = response.json()
        price = float(data['lastPrice'])
        change = float(data['priceChangePercent'])

        # Message banana
        message = f"📊 SYNAPSE (SYN) Live Update\nPrice: ${price:.4f}\n24h Change: {change:.2f}%\n"
        if change > 0:
            message += "🟢 Market is Bullish (Up)"
        else:
            message += "🔴 Market is Bearish (Down)"

        # Telegram par bhejna
        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        res = requests.post(tg_url, json=payload).json()
        
        if res.get("ok"):
            return "Alert sent successfully to Telegram!"
        else:
            return f"Telegram API Error: {res.get('description')}"
            
    except Exception as e:
        return f"System Error: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
