import os
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

# Yahan apna Token aur Chat ID dalein
TOKEN = '8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk'
chat_id = '1179672183'

@app.route('/trigger')
def trigger_bot():
    try:
        # Binance API se data lena
        url = "https://api.binance.com/api/v3/klines?symbol=SYNUSDT&interval=1h&limit=20"
        response = requests.get(url)
        data = response.json()
        
        # Safety Check: Agar data list nahi hai ya khali hai
        if not isinstance(data, list) or len(data) < 15:
            return "Error: Binance API se data nahi mila ya list choti hai."

        closes = [float(candle[4]) for candle in data]
        
        # RSI Calculation with Safety Check
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

        # Message banana
        message = f"📊 SYN Live Update:\nCurrent RSI: {rsi:.2f}\n"
        if rsi < 30:
            message += "🚨 SIGNAL: BUY (Oversold)"
        elif rsi > 70:
            message += "🚨 SIGNAL: SELL (Overbought)"
        else:
            message += "Market Neutral. Wait."

        # Telegram par bhejna
        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        res = requests.post(tg_url, json=payload).json()
        
        if res.get("ok"):
            return "Alert sent successfully to Telegram!"
        else:
            return f"Telegram Error: {res}"
            
    except Exception as e:
        return f"Code Error: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
