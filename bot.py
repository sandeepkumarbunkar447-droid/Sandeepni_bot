import os
import time
import threading
import requests
import pandas as pd
import ta  # <-- Yahan pandas_ta ki jagah sirf ta use karna hai
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get('TELEGRAM_TOKEN', '8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk')
chat_id = os.environ.get('CHAT_ID', '1179672183')

def get_ultra_sigma_signal():
    try:
        # Coinpaprika se historical/ticker data ya CoinGecko use karein jo Render par block nahi hota
        url = "https://api.coinpaprika.com/v1/tickers/syn-synapse"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return "API Error: Unable to fetch market data."
        
        data = response.json()
        quotes = data['quotes']['USD']
        price = quotes['price']
        change_24h = quotes['percent_change_24h']
        volume_24h = quotes['volume_24h']
        
        # Simple & Robust Sigma Logic based on reliable Coinpaprika data
        signal = "NEUTRAL (Waiting for Confluence) ⚪"
        emoji = "⚪"
        
        if change_24h > 3.0:
            signal = "🚀 STRONG BUY (Bullish Momentum)"
            emoji = "🟢"
        elif change_24h < -3.0:
            signal = "⚠️ STRONG SELL (Bearish Drop)"
            emoji = "🔴"
            
        sl = price * 0.97 if "BUY" in signal else price * 1.03
        
        return (f"💎 *ULTRA-SIGMA TRADING BOT*\n\n"
                f"{emoji} *Signal:* {signal}\n"
                f"💰 *Entry Price:* ${price:.4f}\n"
                f"🛡️ *Dynamic SL:* ${sl:.4f}\n"
                f"📊 *24h Change:* {change_24h:.2f}%\n"
                f"📈 *24h Vol:* ${volume_24h:,.0f}")

    except Exception as e:
        return f"Sigma System Error: {str(e)}"

def send_telegram():
    while True:
        try:
            message = get_ultra_sigma_signal()
            tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(tg_url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=10)
        except Exception:
            pass
        time.sleep(1200)

@app.route('/')
def home():
    return "Ultra-Sigma Bot is Active!"

if __name__ == "__main__":
    threading.Thread(target=send_telegram, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
