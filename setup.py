import getpass
from pathlib import Path

def ask(prompt, default=""):
    value = input(f"{prompt}" + (f" [{default}]" if default else "") + ": ").strip()
    return value or default

def main():
    print("=" * 54)
    print(" CΛZΛDØR DΞ LUZ FORWARDER - SETUP")
    print("=" * 54)
    token = getpass.getpass("Telegram Bot Token: ").strip()
    chat_id = ask("Telegram Chat ID")
    interval = ask("Check interval (detik)", "5")
    allowed = ask("Allowed numbers (opsional, koma)", "")
    blocked = ask("Blocked numbers (opsional, koma)", "")
    keywords = ask("Keywords (opsional, koma)", "")
    block_keywords = ask("Blocked keywords (opsional, koma)", "")

    env = f"""TELEGRAM_BOT_TOKEN={token}
TELEGRAM_CHAT_ID={chat_id}
CHECK_INTERVAL={interval}
DEBUG_MODE=false
LANGUAGE=id
ALLOWED_NUMBERS={allowed}
BLOCKED_NUMBERS={blocked}
KEYWORDS={keywords}
BLOCK_KEYWORDS={block_keywords}
MAX_PROCESSED_SMS=1000
STATE_FILE=data/state.json
LOG_FILE=logs/forwarder.log
"""
    Path(".env").write_text(env, encoding="utf-8")
    print("\n✅ .env berhasil dibuat.")
    print("Jalankan: python -m src.main")

if __name__ == "__main__":
    main()
