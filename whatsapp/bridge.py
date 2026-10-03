from flask import Flask, request, jsonify
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": True,
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(data.get("description", "Telegram API error"))

    return data


@app.post("/whatsapp")
def whatsapp():
    data = request.get_json(silent=True) or {}

    sender = data.get("sender", "Unknown")
    message = data.get("message", "")

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    telegram_text = (
        "🟢 WHATSAPP\n\n"
        f"👤 Pengirim: {sender}\n"
        f"💬 Pesan:\n{message}\n\n"
        f"🕐 {timestamp}"
    )

    try:
        send_telegram(telegram_text)

        print(f"📤 WhatsApp → Telegram: {sender}")

        return jsonify({
            "ok": True,
            "telegram": True
        })

    except Exception as e:
        print(f"❌ Telegram gagal: {e}")

        return jsonify({
            "ok": False,
            "telegram": False,
            "error": str(e)
        }), 502


@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "service": "CΛZΛDØR WhatsApp Bridge"
    })


if __name__ == "__main__":
    print("CΛZΛDØR WHATSAPP BRIDGE v2")
    print("Listening: http://127.0.0.1:8888")

    app.run(
        host="127.0.0.1",
        port=8888,
        debug=False
    )
