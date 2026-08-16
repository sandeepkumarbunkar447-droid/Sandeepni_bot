import os
import time
import threading
import requests
import pandas as pd
import numpy as np
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get('TELEGRAM_TOKEN', '8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk')
chat_id = os.environ.get('CHAT_ID', '1179672183')

def get_full_sigma_analysis():
    try:
        url = "https://api.coinpaprika.com/v1/coins/syn-synapse/ohlcv/latest"
        response = requests.get(url, timeout=15)
        df = pd.DataFrame(response.json())
        
        # 1. Calculation Safety: Ensure data is sorted by time
        df = df.sort_values('time_open')
        
        # 2. Hardcore RSI Calculation (14-period)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0, 0))
        
        # EMA based RSI (Jada precise hota hai)
        avg_gain = gain.ewm(com=13, adjust=False).mean()
        avg_loss = loss.ewm(com=13, adjust=False).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 3. ATR Calculation (High-Low-Close Volatility)
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.ewm(span=14, adjust=False).mean()
        
        # Latest Values (No more NaN)
        curr_price = df['close'].iloc[-1]
        curr_rsi = df['rsi'].iloc[-1]
        curr_atr = df['atr'].iloc[-1]
        curr_vol = df['volume'].iloc[-1]
        avg_vol = df['volume'].rolling(window=14).mean().iloc[-1]
        
        # Confluence Logic
        signal = "WAITING FOR SIGMA CONFLUENCE ⚪"
        emoji = "⚪"
        
        if curr_rsi < 35 and curr_vol > avg_vol:
            signal = "🚀 STRONG BUY (Sigma Confluence)"
            emoji = "🟢"
        elif curr_rsi > 65 and curr_vol > avg_vol:
            signal = "⚠️ STRONG SELL (Sigma Confluence)"
            emoji = "🔴"
        
        sl = (curr_price - (curr_atr * 2)) if "BUY" in signal else (curr_price + (curr_atr * 2))
        
        return (f"💎 *ULTRA-SIGMA ENGINE v4*\n\n"
                f"{emoji} *Signal:* {signal}\n"
                f"💰 *Price:* ${curr_price:.4f}\n"
                f"🛡️ *Stop Loss:* ${sl:.4f}\n"
                f"📊 *RSI:* {curr_rsi:.1f} | *ATR:* {curr_atr:.4f}\n"
                f"📈 *Volume:* {curr_vol/avg_vol:.1f}x Avg")

    except Exception as e:
        return f"Sigma Logic Error: {str(e)}"

# Flask & Threading (Keep as is)
def send_telegram():
    while True:
        message = get_full_sigma_analysis()
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        time.sleep(1200)

@app.route('/')
def home():
    return "Ultra-Sigma Engine Active!"

if __name__ == "__main__":
    threading.Thread(target=send_telegram, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
