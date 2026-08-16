    import os
import time
import threading
import requests
import pandas as pd
import numpy as np
from flask import Flask

app = Flask(__name__)

# Config
TOKEN = os.environ.get('8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk')
chat_id = os.environ.get('CHAT_ID', '1179672183')

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_sigma_signal():
    try:
        # 1. Data Fetching
        url = "https://api.coinpaprika.com/v1/tickers/syn-synapse/historical?start=2026-08-10"
        response = requests.get(url, timeout=15).json()
        df = pd.DataFrame(response)
        
        # 2. Indicators Calculation
        df['close'] = df['price']
        rsi = calculate_rsi(df['close']).iloc[-1]
        price = df['close'].iloc[-1]
        
        # 3. Strong Sigma Confluence Logic
        # BUY: RSI < 35 (Oversold) + Strong Support
        # SELL: RSI > 65 (Overbought) + Choti (Top) reached
        
        signal = "WAITING FOR SIGMA CONFLUENCE ⚪"
        emoji = "⚪"
        
        if rsi < 35:
            signal = "🚀 STRONG BUY (RSI Oversold/Sigma Entry)"
            emoji = "🟢"
        elif rsi > 65:
            signal = "⚠️ STRONG SELL (RSI Overbought/Profit Booking)"
            emoji = "🔴"
        
        return (f"💎 *ULTRA-SIGMA BOT v2*\n\n"
                f"{emoji} *Signal:* {signal}\n"
                f"💰 *Price:* ${price:.4f}\n"
                f"📊 *Current RSI:* {rsi:.2f}\n"
                f"_Strategy: RSI Confluence Active_")

    except Exception as e:
        return f"Sigma System Error: {str(e)}"

# --- Flask & Threading (Keep as is) ---
def send_telegram():
    while True:
        message = get_sigma_signal()
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        time.sleep(1200)

@app.route('/')
def home():
    return "Ultra-Sigma Bot v2 Active!"

if __name__ == "__main__":
    threading.Thread(target=send_telegram, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
