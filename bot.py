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
        
        # Indicators using 'ta' library (Zero Errors on Render)
        rsi = ta.momentum.rsi(df['close'], window=14).iloc[-1]
        ema200 = ta.trend.ema_indicator(df['close'], window=200).iloc[-1]
        
        bb_indicator = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
        lower_bb = bb_indicator.bollinger_lband().iloc[-1]
        upper_bb = bb_indicator.bollinger_hband().iloc[-1]
        
        atr_indicator = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14)
        atr = atr_indicator.average_true_range().iloc[-1]
        
        price = df['close'].iloc[-1]
        avg_vol = df['vol'].tail(20).mean()
        curr_vol = df['vol'].iloc[-1]
        
        # Sigma Confluence Logic
        signal = "NEUTRAL (Waiting for Confluence) ⚪"
        emoji = "⚪"
        
        if price > ema200 and (rsi < 35 or price <= lower_bb) and curr_vol > avg_vol:
            signal = "🚀 STRONG BUY (Sigma Confluence)"
            emoji = "🟢"
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
        time.sleep(1200)

@app.route('/')
def home():
    return "Ultra-Sigma Bot is Active!"

if __name__ == "__main__":
    threading.Thread(target=send_telegram, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
