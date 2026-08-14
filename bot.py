import requests
from telegram import Bot
import asyncio
import time

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
        # Binance se zyada candles ka data lena taaki MACD aur RSI theek se calculate ho sake
        url = "https://api.binance.com/api/v3/klines?symbol=SYNUSDT&interval=1h&limit=50"
        response = requests.get(url).json()
        
        closes = [float(candle[4]) for candle in response]
        current_price = closes[-1]
        
        # 1. RSI Calculation (14 periods)
        delta = [closes[i+1] - closes[i] for i in range(len(closes)-1)]
        gain = [d if d > 0 else 0 for d in delta]
        loss = [-d if d < 0 else 0 for d in delta]
        avg_gain = sum(gain[-14:]) / 14
        avg_loss = sum(loss[-14:]) / 14
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        # 2. MACD Calculation (12, 26, 9)
        ema12 = calculate_ema(closes, 12)
        ema26 = calculate_ema(closes, 26)
        # Length match karne ke liye slice adjust karna
        macd_line = [e12 - e26 for e12, e26 in zip(ema12[len(ema12)-len(ema26):], ema26)]
        signal_line = calculate_ema(macd_line, 9)
        
        current_macd = macd_line[-1]
        current_signal = signal_line[-1]
        
        # 3. Strategy & Risk Management Logic
        signal = "⚪ Market Neutral. Intezaar karein."
        sl = 0
        tp = 0
        
        # Strong Buy: Jab RSI oversold ho aur MACD line signal line ke upar nikal rahi ho
        if rsi < 35 and current_macd > current_signal:
            signal = "🚨 STRONG BUY SIGNAL!"
            sl = current_price * 0.98  # 2% Stop Loss neeche
            tp = current_price * 1.04  # 4% Take Profit upar
        # Strong Sell: Jab RSI overbought ho aur MACD line signal line ke niche ja rahi ho
        elif rsi > 65 and current_macd < current_signal:
            signal = "🚨 STRONG SELL SIGNAL!"
            sl = current_price * 1.02  # 2% Stop Loss upar
            tp = current_price * 0.96  # 4% Take Profit neeche
            
        return current_price, rsi, current_macd, current_signal, signal, sl, tp
    
    except Exception as e:
        print("Error:", e)
        return None

async def main():
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
        else:
            print("Data fetch karne mein error aaya.")
            
        # Har 15 minute (900 seconds) mein update
        time.sleep(900)

if __name__ == "__main__":
    asyncio.run(main())
