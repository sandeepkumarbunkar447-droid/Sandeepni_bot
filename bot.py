import requests
from telegram import Bot
import asyncio
import time
import threading
from flask import Flask

# 1. Dummy Web Server (Render ke port error ko rokne ke liye)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# 2. Bot Details
TOKEN = '8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk'
chat_id = '1179672183'

bot = Bot(token=TOKEN)

def calculate_ema(prices, period):
    multiplier = 2 / (period + 1)
    ema = [sum(prices[:period]) / period]
    for price in prices[period:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    return ema

def get_advanced_analysis():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=SYNUSDT&interval=1h&limit=50"
        response = requests.get(url).json()
        closes = [float(candle[4]) for candle in response]
        current_price = closes[-1]
        
        delta = [closes[i+1] - closes[i] for i in range(len(closes)-1)]
        gain = [d if d > 0 else 0 for d in delta]
        loss = [-d if d < 0 else 0 for d in delta]
        avg_gain = sum(gain[-14:]) / 14
        avg_loss = sum(loss[-14:]) / 14
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        ema12 = calculate_ema(closes, 12)
        ema26 = calculate_ema(closes, 26)
        macd_line = [e12 - e26 for e12, e26 in zip(ema12[len(ema12)-len(ema26):], ema26)]
        signal_line = calculate_ema(macd_line, 9)
        
        current_macd = macd_line[-1]
        current_signal = signal_line[-1]
        
        signal = "⚪ Market Neutral. Intezaar karein."
        sl = 0
        tp = 0
        
        if rsi < 35 and current_macd > current_signal:
            signal = "🚨 STRONG BUY SIGNAL!"
            sl = current_price * 0.98
            tp = current_price * 1.04
        elif rsi > 65 and current_macd < current_signal:
            signal = "🚨 STRONG SELL SIGNAL!"
            sl = current_price * 1.02
            tp = current_price * 0.96
            
        return current_price, rsi, current_macd, current_signal, signal, sl, tp
    except Exception as e:
        print("Error:", e)
        return None

async def bot_loop():
    while True:
        data = get_advanced_analysis()
        if data:
            price, rsi, macd, sig_line, signal, sl, tp = data
            message = f"📊 **SYN Advanced Analysis**\n\n"
            message += f"💰 Current Price: ${price:.2f}\n"
            message += f"📈 RSI (14): {rsi:.2f}\n"
            message += f"📉 MACD: {macd:.2f} | Signal: {sig_line:.2f}\n\n"
            message += f"Status: {signal}\n"
            if sl > 0 and tp > 0:
                message += f"\n🛑 Stop-Loss: ${sl:.2f}\n"
                message += f"🎯 Target (TP): ${tp:.2f}\n"
            
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        time.sleep(900)

def start_bot():
    asyncio.run(bot_loop())

if __name__ == "__main__":
    # Bot ko background thread me chalana
    t = threading.Thread(target=start_bot)
    t.start()
    
    # Flask server ko main thread me chalana (Port 10000)
    run_flask()
    
