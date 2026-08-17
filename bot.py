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
        url = "https://api.coinpaprika.com/v1/coins/home-defiapp/ohlcv/latest"
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            return "Sigma System Error: Failed to fetch market candles."
            
        raw_data = response.json()
        df = pd.DataFrame(raw_data)
        
        # 1. Zero Tolerance for Bad Data (Converting everything to strict numbers)
        cols_to_convert = ['open', 'high', 'low', 'close', 'volume']
        for col in cols_to_convert:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna(subset=['close', 'high', 'low', 'volume'])
        df = df.sort_values('time_open')
        
        # 2. Institutional Grade RSI (Wilder's Smoothing)
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        
        avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 3. True Volatility ATR Calculation
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.ewm(span=14, adjust=False).mean()
        
        # 4. Extracting Final Valid Metrics
        curr_price = float(df['close'].iloc[-1])
        curr_rsi = float(df['rsi'].iloc[-1]) if not pd.isna(df['rsi'].iloc[-1]) else 50.0
        curr_atr = float(df['atr'].iloc[-1]) if not pd.isna(df['atr'].iloc[-1]) else (curr_price * 0.03)
        
        curr_vol = float(df['volume'].iloc[-1])
        avg_vol = float(df['volume'].tail(14).mean()) if len(df) >= 14 else curr_vol
        if avg_vol == 0: 
            avg_vol = 1.0
            
        vol_ratio = curr_vol / avg_vol
        
        # 5. Core Sigma Confluence Decision Engine
        signal = "WAITING FOR SIGMA CONFLUENCE ⚪"
        emoji = "⚪"
        
        if curr_rsi < 35 and vol_ratio > 1.0:
            signal = "🚀 STRONG BUY (Sigma Confluence)"
            emoji = "🟢"
        elif curr_rsi > 65 and vol_ratio > 1.0:
            signal = "⚠️ STRONG SELL (Sigma Confluence)"
            emoji = "🔴"
        
        sl = (curr_price - (curr_atr * 2)) if "BUY" in signal else (curr_price + (curr_atr * 2))
        
        return (f"💎 *ULTRA-SIGMA ENGINE v4.1*\n\n"
                f"{emoji} *Signal:* {signal}\n"
                f"💰 *Price:* ${curr_price:.4f}\n"
                f"🛡️ *Stop Loss:* ${sl:.4f}\n"
                f"📊 *RSI:* {curr_rsi:.1f} | *ATR:* {curr_atr:.4f}\n"
                f"📈 *Volume:* {vol_ratio:.1f}x Avg")

    except Exception as e:
        return f"Sigma Logic Error: {str(e)}"

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
    return "Ultra-Sigma Engine v4.1 Active!"

if __name__ == "__main__":
    threading.Thread(target=send_telegram, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
