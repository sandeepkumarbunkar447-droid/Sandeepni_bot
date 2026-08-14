import os
import requests
from flask import Flask

app = Flask(__name__)

# APNA TOKEN AUR CHAT ID YAHAN DAALEN
TOKEN = '8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk'
chat_id = '1179672183'

@app.route('/')
def home():
    return "Bot is alive and running!"

@app.route('/trigger')
def trigger_bot():
    try:
        # CoinGecko API se SYN ka live price lena (Render friendly)
        url = "https://api.coingecko.com/api/v3/simple/price?ids=synapse&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return f"API Error: {response.status_code}"
            
        data = response.json()
        price = data['synapse']['usd']
        change = data['synapse']['usd_24h_change']

        # Message banana
        message = f"📊 SYN Live Update (CoinGecko)\nPrice: ${price:,.2f}\n24h Change: {change:.2f}%\n"
        if change > 0:
            message += "🟢 Market is Bullish (Up)"
        else:
            message += "🔴 Market is Bearish (Down)"

        # Telegram par bhejna
        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        res = requests.post(tg_url, json=payload).json()
        
        if res.get("ok"):
            return "Alert sent successfully to Telegram!"
        else:
            return f"Telegram API Error: {res.get('description')}"
            
    except Exception as e:
        return f"System Error: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
