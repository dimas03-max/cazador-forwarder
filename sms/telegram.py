import time
import requests


class TelegramError(Exception):
    pass


class TelegramClient:
    def __init__(self, token, chat_id, timeout=15):
        self.base = f"https://api.telegram.org/bot{token}"
        self.chat_id = str(chat_id)
        self.timeout = timeout
        self.session = requests.Session()

    def _call(self, method, payload=None):
        try:
            r = self.session.post(
                f"{self.base}/{method}",
                json=payload or {},
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise TelegramError(f"network: {exc}") from exc

        try:
            data = r.json()
        except ValueError:
            raise TelegramError(
                f"HTTP {r.status_code}: respons bukan JSON"
            )

        if not data.get("ok"):
            raise TelegramError(
                data.get("description", f"HTTP {r.status_code}")
            )

        return data["result"]

    def get_me(self):
        return self._call("getMe")

    def send_message(self, text):
        return self._call("sendMessage", {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": True,
        })

    def get_updates(self, offset=None, timeout=2):
        payload = {
            "timeout": timeout,
            "allowed_updates": ["message"],
        }

        if offset is not None:
            payload["offset"] = offset

        return self._call("getUpdates", payload)

    def clear_pending_updates(self):
        updates = self.get_updates(timeout=0)

        if updates:
            return updates[-1]["update_id"] + 1

        return None

    def send_with_retry(self, text, attempts=4):
        delay = 2
        last = None

        for i in range(attempts):
            try:
                return self.send_message(text)

            except Exception as exc:
                last = exc

                if i < attempts - 1:
                    time.sleep(delay)
                    delay = min(delay * 2, 30)

        raise TelegramError(str(last))
