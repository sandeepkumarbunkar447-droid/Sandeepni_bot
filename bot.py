import os
import time
import threading
import requests
import pandas as pd
import pandas_ta as ta
from flask import Flask

app = Flask(__name__)

# Render Environment Variables (Setting safe defaults)
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk')
chat_id = os.environ.get('CHAT_ID', '1179672183')

def get_ultra_sigma_signal():
    try:
        # 1. Binance API se Data (Accuracy ke liye 1h Interval)
        url = "https://api.binance.com/api/v3/klines?symbol=SYNUSDT&interval=1h&limit=200"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return "API Error: Unable to fetch market data."
        
        data = response.json()
        df = pd.DataFrame(data, columns=['t', 'o', 'h', 'l', 'close', 'vol', 'a', 'b', 'c', 'd', 'e', 'f'])
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['vol'] = df['vol'].astype(float)
        
        # 2. Indicators (The Confluence Strategy)
        rsi = ta.rsi(df['close'], length=14).iloc[-1]
        ema200 = ta.ema(df['close'], length=200).iloc[-1]
        bbands = ta.bbands(df['close'], length=20, std=2)
        atr = ta.atr(df['high'], df['low'], df['close'], length=14).iloc[-1]
        
        price = df['close'].iloc[-1]
        lower_bb = bbands['BBL_20_2.0'].iloc[-1]
        upper_bb = bbands['BBU_20_2.0'].iloc[-1]
        avg_vol = df['vol'].tail(20).mean()
        curr_vol = df['vol'].iloc[-1]
        
        # 3. Sigma Confluence Logic
        signal = "NEUTRAL (Waiting for Confluence) ⚪"
        emoji = "⚪"
        
        # BUY Logic: Bullish Trend (Price > EMA200) + RSI/BB Oversold + Volume Spike
        if price > ema200 and (rsi < 35 or price <= lower_bb) and curr_vol > avg_vol:
            signal = "🚀 STRONG BUY (Sigma Confluence)"
            emoji = "🟢"
        # SELL Logic: Bearish Trend (Price < EMA200) + RSI/BB Overbought + Volume Spike
        elif price < ema200 and (rsi > 65 or price >= upper_bb) and curr_vol > avg_vol:
            signal = "⚠️ STRONG SELL (Sigma Confluence)"
            emoji = "🔴"
            
        sl = (price - (atr * 1.5)) if "BUY" in signal else (price + (atr * 1.5))
        
        return (f"💎 *ULTRA-SIGMA TRADING BOT*\n\n"
                f"{emoji} *Signal:* {signal}\n"
                f"💰 *Entry Price:* ${price:.4f}\n"
                f"🛡️ *Dynamic SL:* ${sl:.4f}\n"
                f"📊 *RSI:* {rsi:.1f} | *EMA200:* ${ema200:.4f}\n"
                f"📈 *Vol:* {curr_vol/avg_vol:.1f}x Avg")

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
        time.sleep(1200) # 20 Minutes

@app.route('/')
def home():
    return "Ultra-Sigma Bot is Active!"

if __name__ == "__main__":
    threading.Thread(target=send_telegram, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
            
