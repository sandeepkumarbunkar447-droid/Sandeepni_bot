import os
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

# Yahan apna Bot Token aur Chat ID daalein
TOKEN = '8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk'
chat_id = '1179672183'

@app.route('/trigger')
def trigger_bot():
    try:
        # 1. Binance se RSI calculate karna
        url = "https://api.binance.com/api/v3/klines?symbol=SYNUSDT&interval=1h&limit=15"
        response = requests.get(url).json()
        closes = [float(candle[4]) for candle in response]
        delta = [closes[i+1] - closes[i] for i in range(len(closes)-1)]
        gain = [d if d > 0 else 0 for d in delta]
        loss = [-d if d < 0 else 0 for d in delta]
        avg_gain = sum(gain) / 14
        avg_loss = sum(loss) / 14
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi = 100 - (100 / (1 + rs))

        # 2. Message banana
        message = f"📊 SYN Live Update:\nCurrent RSI: {rsi:.2f}\n"
        if rsi < 30:
            message += "🚨 SIGNAL: BUY (Oversold)"
        elif rsi > 70:
            message += "🚨 SIGNAL: SELL (Overbought)"
        else:
            message += "Market Neutral. Wait."

        # 3. Seedha Telegram API ko request bhejna (Bina kisi library ke)
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
        return f"Error: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
