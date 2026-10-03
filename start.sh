#!/data/data/com.termux/files/usr/bin/bash

cd "$(dirname "$0")"

termux-wake-lock 2>/dev/null || true

echo ""
echo "=========================================="
echo "      CΛZΛDØR FORWARDER v3"
echo "=========================================="
echo ""
echo "📩 SMS        → Telegram"
echo "💬 WhatsApp   → Telegram"
echo ""

python main.py
