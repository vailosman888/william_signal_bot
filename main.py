import requests
import time
import os
from datetime import datetime, timedelta
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = "8428714955:AAGqTTMqxAitY_RF93XPP3mvGGu5PVZvr_8"
CHAT_ID = "@williamsignal0"
TWELVE_API_KEY = "cd2e95b15b4f4b5e8f6218a8e3537de4"

PAIR = "GBP/USD"
SYMBOL = PAIR.replace("/", "")
INTERVAL = "1min"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def get_price():
    url = f"https://api.twelvedata.com/price?symbol={SYMBOL}&apikey={TWELVE_API_KEY}"
    r = requests.get(url).json()
    return float(r["price"]) if "price" in r else None

def get_rsi():
    url = f"https://api.twelvedata.com/rsi?symbol={SYMBOL}&interval={INTERVAL}&time_period=14&apikey={TWELVE_API_KEY}"
    r = requests.get(url).json()
    return float(r["values"][0]["rsi"]) if "values" in r else None

def get_ema():
    url = f"https://api.twelvedata.com/ema?symbol={SYMBOL}&interval={INTERVAL}&time_period=20&apikey={TWELVE_API_KEY}"
    r = requests.get(url).json()
    return float(r["values"][0]["ema"]) if "values" in r else None

@app.route("/")
def webhook_trigger():
    try:
        rsi = get_rsi()
        ema = get_ema()
        price_before = get_price()

        if rsi is None or ema is None or price_before is None:
            return "❌ بيانات ناقصة، لم تُرسل توصية."

        if rsi < 25 and price_before > ema:
            direction = "صاعد 🟢"
            expected = "up"
        elif rsi > 75 and price_before < ema:
            direction = "هابط 🔴"
            expected = "down"
        else:
            return "🔍 لا توجد إشارة قوية حالياً."

        entry_time = (datetime.utcnow() + timedelta(minutes=1)).strftime("%H:%M UTC")

        msg = f"""🔥  توصية جديدة 🔥

أسم الزوج : {PAIR}
أتجاه الصفقه : {direction}
قوة الإشارة : 95%
⏰ وقت الدخول : {entry_time}
مدة الصفقة : 1 دقيقة

@William_Trader_Support"""
        send_telegram_message(msg)

        time.sleep(60)

        price_after = get_price()
        if price_after is None:
            return "⚠️ فشل بجلب السعر بعد دقيقة."

        if expected == "up":
            result = "✅ WIN" if price_after > price_before else "💔 LOSS"
        else:
            result = "✅ WIN" if price_after < price_before else "💔 LOSS"

        send_telegram_message(f"""📊 نتيجة الصفقة:\n\n{result}""")
        return "✅ تم إرسال الإشارة والنتيجة."

    except Exception as e:
        return f"❌ خطأ: {e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



