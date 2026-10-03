import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def csv_env(name: str):
    return [x.strip() for x in os.getenv(name, "").split(",") if x.strip()]

@dataclass
class Config:
    telegram_bot_token: str
    telegram_chat_id: str
    check_interval: int = 5
    debug_mode: bool = False
    language: str = "id"
    allowed_numbers: list = None
    blocked_numbers: list = None
    keywords: list = None
    block_keywords: list = None
    max_processed_sms: int = 1000
    state_file: str = "data/state.json"
    log_file: str = "logs/forwarder.log"

    @classmethod
    def from_env(cls):
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        if not token or token == "your_bot_token_here":
            raise ValueError("TELEGRAM_BOT_TOKEN belum diatur.")
        if not chat_id or chat_id == "your_chat_id_here":
            raise ValueError("TELEGRAM_CHAT_ID belum diatur.")
        return cls(
            telegram_bot_token=token,
            telegram_chat_id=chat_id,
            check_interval=max(1, int(os.getenv("CHECK_INTERVAL", "5"))),
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
            language=os.getenv("LANGUAGE", "id"),
            allowed_numbers=csv_env("ALLOWED_NUMBERS"),
            blocked_numbers=csv_env("BLOCKED_NUMBERS"),
            keywords=csv_env("KEYWORDS"),
            block_keywords=csv_env("BLOCK_KEYWORDS"),
            max_processed_sms=max(100, int(os.getenv("MAX_PROCESSED_SMS", "1000"))),
            state_file=os.getenv("STATE_FILE", "data/state.json"),
            log_file=os.getenv("LOG_FILE", "logs/forwarder.log"),
        )
