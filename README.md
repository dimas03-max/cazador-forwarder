# CΛZΛDØR FORWARDER v3

SMS dan notifikasi WhatsApp → Telegram menggunakan Termux.

## Fitur

- 📩 Forward SMS ke Telegram
- 💬 Forward notifikasi WhatsApp ke Telegram
- 🛡️ Anti-duplicate SMS
- 🔄 Retry Telegram
- 📊 Statistik forwarding
- 🎛️ Telegram commands
- 🌐 WhatsApp Bridge
- ⚙️ Konfigurasi melalui `.env`
- 📱 Dirancang untuk Termux Android

## Struktur

```text
cazador-forwarder/
├── main.py
├── start.sh
├── install.sh
├── .env
├── .env.example
├── requirements.txt
├── setup.py
├── README.md
├── .gitignore
├── data/
├── logs/
├── sms/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── filters.py
│   ├── sms.py
│   ├── state.py
│   └── telegram.py
└── whatsapp/
    ├── __init__.py
    └── bridge.py


## Requirements

- Android
- Termux
- Termux:API
- Python 3
- Telegram Bot
- Aplikasi Android dengan Notification Access untuk WhatsApp

## Installation

Install package dasar:

```bash
pkg update
pkg install python termux-api git
E0F
