import os
import requests
import time
import threading
from flask import Flask

app = Flask(__name__)

# APNA TOKEN AUR CHAT ID YAHAN DAALEIN
TOKEN = '8613588573:AAHhrbzvG3DVPCbVZV2Bx1wUKAtpdJK1enk'
chat_id = '1179672183'

def get_syn_signal():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=synapse-2&vs_currencies=usd&include_24hr_change=true"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"API Error: Status {response.status_code}"
            
        data = response.json()
        if 'synapse-2' not in data:
            return "API Error: Synapse token data not found."
            
        price = data['synapse-2']['usd']
        change = data['synapse-2']['usd_24h_change']
        
        # --- BUY / SELL ANALYSIS LOGIC ---
        signal = ""
        action_emoji = ""
        
        if change > 3.0:
            signal = "STRONG BUY 🚀 (Bullish Momentum)"
            action_emoji = "🟢"
        elif change > 0:
            signal = "BUY / HOLD 📈 (Market Up)"
            action_emoji = "🟢"
        elif change < -3.0:
            signal = "STRONG SELL ⚠️ (Bearish Drop)"
            action_emoji = "🔴"
        else:
            signal = "SELL / WAIT 📉 (Market Down)"
            action_emoji = "🔴"

        message = (
            f"🤖 **SYNAPSE (SYN) Trading Signal**\n\n"
            f"{action_emoji} **Action:** {signal}\n"
            f"💰 **Current Price:** ${price:.4f}\n"
            f"📊 **24h Change:** {change:.2f}%\n\n"
            f"_Analysed automatically based on 24h trend._"
        )
        return message
    except Exception as e:
        return f"Error fetching analysis: {str(e)}"

def send_telegram():
    while True:
        message = get_syn_signal()
        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(tg_url, json=payload, timeout=10)
        except:
            pass
        time.sleep(1200)  # Har 20 minute

@app.route('/')
def home():
    return "Trading Signal Bot is running automatically every 20 minutes!"

if __name__ == "__main__":
    threading.Thread(target=send_telegram, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
