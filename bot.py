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
        # Binance API request
        url = "https://api.binance.com/api/v3/klines?symbol=SYNUSDT&interval=1h&limit=20"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return f"API Error: {response.status_code}"
            
        data = response.json()
        
        if not isinstance(data, list) or len(data) < 15:
            return f"API Error: Data format sahi nahi hai. Data length: {len(data)}"

        # RSI calculation
        closes = [float(candle[4]) for candle in data]
        delta = [closes[i+1] - closes[i] for i in range(len(closes)-1)]
        gain = [d if d > 0 else 0 for d in delta]
        loss = [-d if d < 0 else 0 for d in delta]
        
        avg_gain = sum(gain[-14:]) / 14
        avg_loss = sum(loss[-14:]) / 14
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        # Telegram message
        message = f"📊 SYN Live Update\nPrice: ${closes[-1]:.2f}\nRSI: {rsi:.2f}\n"
        if rsi < 35:
            message += "🚨 SIGNAL: BUY"
        elif rsi > 65:
            message += "🚨 SIGNAL: SELL"
        else:
            message += "Market: Neutral"

        # Sending to Telegram
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
    
