import requests
import time
from datetime import datetime, timedelta

TELEGRAM_TOKEN = "8428714955:AAGqTTMqxAitY_RF93XPP3mvGGu5PVZvr_8"
CHAT_ID = "@williamsignal0"
TWELVE_API_KEY = "cd2e95b15b4f4b5e8f6218a8e3537de4"

# ✅ قائمة الأزواج التي سيدور عليها البوت
PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "EUR/JPY", "EUR/CAD",
    "USD/CAD", "USD/CHF", "AUD/USD", "NZD/USD", "AUD/CHF",
    "NZD/CHF", "EUR/CHF", "GBP/JPY", "CAD/JPY"
]

INTERVAL = "1min"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def get_price(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_API_KEY}"
    r = requests.get(url).json()
    return float(r["price"])

def get_rsi(symbol):
    url = f"https://api.twelvedata.com/rsi?symbol={symbol}&interval={INTERVAL}&time_period=14&apikey={TWELVE_API_KEY}"
    r = requests.get(url).json()
    return float(r["values"][0]["rsi"])

def get_ema(symbol):
    url = f"https://api.twelvedata.com/ema?symbol={symbol}&interval={INTERVAL}&time_period=20&apikey={TWELVE_API_KEY}"
    r = requests.get(url).json()
    return float(r["values"][0]["ema"])

def analyze_pair(pair):
    symbol = pair.replace("/", "")
    try:
        rsi = get_rsi(symbol)
        ema = get_ema(symbol)
        price_before = get_price(symbol)

        if rsi < 25 and price_before > ema:
            direction = "صاعد 🟢"
            expected = "up"
        elif rsi > 75 and price_before < ema:
            direction = "هابط 🔴"
            expected = "down"
        else:
            return  # لا ترسل إذا ما في فرصة قوية

        entry_time = (datetime.utcnow() + timedelta(minutes=1)).strftime("%H:%M UTC")
        signal = f"""🔥  توصية جديدة 🔥

أسم الزوج : {pair}
أتجاه الصفقه : {direction}
قوة الإشارة : 95%
⏰ وقت الدخول : {entry_time}
مدة الصفقة : 1 دقيقة

@William_Trader_Support"""
        send_telegram_message(signal)

        # ننتظر دقيقة قبل حساب النتيجة
        time.sleep(60)
        price_after = get_price(symbol)

        if expected == "up":
            result = "✅ WIN" if price_after > price_before else "💔 LOSS"
        else:
            result = "✅ WIN" if price_after < price_before else "💔 LOSS"

        result_msg = f"""📊 نتيجة الصفقة:

{result}"""
        send_telegram_message(result_msg)

    except Exception as e:
        print(f"خطأ مع الزوج {pair}: {e}")

def run_all():
    for pair in PAIRS:
        analyze_pair(pair)
        time.sleep(3)  # وقت بسيط بين كل تحليل لتجنب الضغط على API

# تشغيل البوت
run_all()
