import logging
import signal
import sys
import time
from pathlib import Path

from .config import Config
from .telegram import TelegramClient, TelegramError
from .sms import list_sms, check as sms_check, TermuxAPIError
from .filters import allowed
from .state import State

STOP = False

def setup_logging(path, debug=False):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(path, encoding="utf-8")],
    )

def fmt_sms(sms):
    number = sms.get("number") or sms.get("address") or "Unknown"
    body = sms.get("body") or ""
    received = sms.get("received") or sms.get("date") or "-"
    return (
        "📩 SMS BARU\n\n"
        f"📱 Dari: {number}\n"
        f"🕒 Waktu: {received}\n\n"
        f"{body}"
    )

def handle_command(client, state, text):
    cmd = text.strip().split()[0].lower() if text.strip() else ""
    if cmd == "/status":
        client.send_with_retry(state.status_text())
        return
    if cmd == "/stats":
        client.send_with_retry(state.status_text())
        return
    if cmd == "/pause":
        state.data["paused"] = True
        state.save()
        client.send_with_retry("⏸️ Forwarder dijeda.")
        return
    if cmd == "/resume":
        state.data["paused"] = False
        state.save()
        client.send_with_retry("▶️ Forwarder dilanjutkan.")
        return
    if cmd == "/health":
        client.send_with_retry("❤️ HEALTH OK\n📡 Telegram: ONLINE\n📱 Termux API: ONLINE")
        return
    if cmd == "/help":
        client.send_with_retry(
            "🤖 Perintah:\n"
            "/status - status forwarder\n"
            "/stats - statistik\n"
            "/pause - jeda forwarding\n"
            "/resume - lanjutkan\n"
            "/health - cek kesehatan\n"
            "/help - bantuan"
        )

def main():
    global STOP
    print("=" * 54)
    print("   CΛZΛDØR DΞ LUZ FORWARDER")
    print("              v1.1.0")
    print("=" * 54)

    try:
        cfg = Config.from_env()
    except Exception as e:
        print(f"❌ Konfigurasi: {e}")
        return 1

    setup_logging(cfg.log_file, cfg.debug_mode)
    client = TelegramClient(cfg.telegram_bot_token, cfg.telegram_chat_id)
    state = State(cfg.state_file, cfg.max_processed_sms)
    state.set_started()
    state.save()

    try:
        me = client.get_me()
        logging.info("✅ Telegram terhubung: @%s", me.get("username", "-"))
        sms_check()
        logging.info("✅ Termux:API SMS tersedia")
    except Exception as e:
        logging.error("❌ Foundation check gagal: %s", e)
        return 1

    print("\n✅ SMS ENGINE ACTIVE")
    print("📡 Telegram : ONLINE")
    print("📱 Termux API: ONLINE")
    print("🛡️ Anti-duplicate: ON")
    print("🔄 Retry: ON")
    print("🎛️ Commands: /status /stats /pause /resume /health /help")
    print("\nTekan Ctrl+C untuk berhenti.\n")

    # Seed existing messages on first run so old SMS aren't dumped to Telegram.
    if not state.data["processed"]:
        try:
            existing = list_sms(100)
            for sms in existing:
                state.mark_processed(state.fingerprint(sms))
            state.save()
            logging.info("🧹 First run: %d SMS lama ditandai sebagai processed.", len(existing))
        except Exception as e:
            logging.warning("Seed SMS lama gagal: %s", e)

    try:
        offset = client.clear_pending_updates()
    except Exception as e:
        logging.warning("📡 Telegram belum tersedia: %s", e)
        offset = None

    def stop_handler(signum, frame):
        nonlocal offset
        global STOP
        STOP = True

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    telegram_online = True
    next_telegram_retry = 0

    while not STOP:
                # Telegram connection + commands
        now = time.time()

        if now >= next_telegram_retry:
            try:
                updates = client.get_updates(
                    offset=offset,
                    timeout=2,
                )

                if not telegram_online:
                    logging.info("📡 Telegram ONLINE kembali.")

                telegram_online = True
                next_telegram_retry = 0

                for upd in updates:
                    offset = upd["update_id"] + 1

                    msg = upd.get("message", {})
                    chat = str(
                        msg.get("chat", {}).get("id", "")
                    )
                    text = msg.get("text", "")

                    if (
                        chat == str(cfg.telegram_chat_id)
                        and text.startswith("/")
                    ):
                        try:
                            handle_command(
                                client,
                                state,
                                text,
                            )
                        except Exception as e:
                            logging.warning(
                                "Command gagal: %s",
                                e,
                            )

            except Exception as e:
                if telegram_online:
                    logging.warning(
                        "📡 Telegram OFFLINE: %s",
                        e,
                    )

                telegram_online = False
                next_telegram_retry = time.time() + 10

        if not state.data.get("paused"):
            try:
                messages = list_sms(100)
                changed = False

                for sms in reversed(messages):
                    fp = state.fingerprint(sms)
                    if state.seen(fp):
                       continue

                    state.inc("received")

                    ok, reason = allowed(sms, cfg)
                    if not ok:
                        state.inc("blocked")
                        state.mark_processed(fp)
                        changed = True
                        continue

                    try:
                        client.send_with_retry(fmt_sms(sms))
                        state.inc("forwarded")
                        state.mark_processed(fp)
                        changed = True
                        logging.info("📤 SMS diteruskan dari %s", sms.get("number") or sms.get("address") or "?")
                    except Exception as e:
                        state.inc("failed")
                        logging.error("❌ Gagal forward SMS: %s", e)

                if changed:
                    state.save()
            except TermuxAPIError as e:
                logging.warning("SMS API: %s", e)
            except Exception as e:
                logging.warning("SMS loop: %s", e)

        time.sleep(cfg.check_interval)

    state.save()
    logging.info("👋 Forwarder dihentikan.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
