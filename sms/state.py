import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

class State:
    def __init__(self, path, max_items=1000):
        self.path = Path(path)
        self.max_items = max_items
        self.data = {
            "processed": [],
            "stats": {
                "received": 0,
                "forwarded": 0,
                "failed": 0,
                "blocked": 0,
                "started_at": None,
            },
            "paused": False,
        }
        self.load()

    def load(self):
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except Exception:
                pass
        self.data.setdefault("processed", [])
        self.data.setdefault("stats", {})
        for k in ("received", "forwarded", "failed", "blocked"):
            self.data["stats"].setdefault(k, 0)
        self.data.setdefault("paused", False)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    @staticmethod
    def fingerprint(sms):
        raw = "|".join([
            str(sms.get("id", "")),
            str(sms.get("number") or sms.get("address") or ""),
            str(sms.get("body", "")),
            str(sms.get("received", "")),
        ])
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def seen(self, fp):
        return fp in self.data["processed"]

    def mark_processed(self, fp):
        self.data["processed"].append(fp)
        self.data["processed"] = self.data["processed"][-self.max_items:]

    def inc(self, key):
        self.data["stats"][key] = self.data["stats"].get(key, 0) + 1

    def set_started(self):
        self.data["stats"]["started_at"] = datetime.now(timezone.utc).isoformat()

    def status_text(self):
        s = self.data["stats"]
        return (
            "🤖 CΛZΛDØR DΞ LUZ FORWARDER\n\n"
            f"Status: {'⏸️ PAUSED' if self.data.get('paused') else '🟢 RUNNING'}\n"
            f"📨 Diterima: {s.get('received',0)}\n"
            f"📤 Diteruskan: {s.get('forwarded',0)}\n"
            f"❌ Gagal: {s.get('failed',0)}\n"
            f"🚫 Filter: {s.get('blocked',0)}"
        )
