import os
import time
import threading
import requests
import pandas as pd
from flask import Flask

app = Flask(__name__)

# Config - Render par environment variables set hain
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk')
chat_id = os.environ.get('CHAT_ID', '1179672183')

def get_full_sigma_analysis():
    try:
        # 1. OHLCV Data fetch (Historical Candlesticks)
        url = "https://api.coinpaprika.com/v1/coins/syn-synapse/ohlcv/latest"
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            return "Sigma System Error: Failed to fetch API data."
            
        data = response.json()
        df = pd.DataFrame(data)
        
        # 2. Manual Candle Calculations (Pure & Robust)
        # RSI Calculation (14 periods)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR Calculation (Volatility meter - 14 periods)
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()
        
        # Current Metrics
        curr_price = df['close'].iloc[-1]
        curr_rsi = df['rsi'].iloc[-1]
        curr_atr = df['atr'].iloc[-1]
        curr_vol = df['volume'].iloc[-1]
        avg_vol = df['volume'].tail(14).mean()
        
        # 3. Sigma Logic (Hardcore Confluence)
        signal = "WAITING FOR SIGMA CONFLUENCE ⚪"
        emoji = "⚪"
        
        # BUY: RSI < 35 (Oversold) + High Volume
        if curr_rsi < 35 and curr_vol > avg_vol:
            signal = "🚀 STRONG BUY (Sigma Confluence)"
            emoji = "🟢"
        # SELL: RSI > 65 (Overbought/Choti) + High Volume
        elif curr_rsi > 65 and curr_vol > avg_vol:
            signal = "⚠️ STRONG SELL (Sigma Confluence)"
            emoji = "🔴"
        
        sl = (curr_price - (curr_atr * 2)) if "BUY" in signal else (curr_price + (curr_atr * 2))
        
        return (f"💎 *ULTRA-SIGMA ENGINE v3*\n\n"
                f"{emoji} *Signal:* {signal}\n"
                f"💰 *Price:* ${curr_price:.4f}\n"
                f"🛡️ *Stop Loss:* ${sl:.4f}\n"
                f"📊 *RSI:* {curr_rsi:.1f} | *ATR:* {curr_atr:.4f}\n"
                f"📈 *Volume:* {curr_vol/avg_vol:.1f}x Avg")

    except Exception as e:
        return f"Sigma System Error: {str(e)}"

# Flask & Threading setup
def send_telegram():
    while True:
        try:
            message = get_full_sigma_analysis()
            tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(tg_url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=10)
        except Exception:
            pass
        time.sleep(1200)

@app.route('/')
def home():
    return "Ultra-Sigma Engine Active!"

if __name__ == "__main__":
    threading.Thread(target=send_telegram, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
