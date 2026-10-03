#!/data/data/com.termux/files/usr/bin/bash

set -e

echo ""
echo "=========================================="
echo "      CΛZΛDØR FORWARDER INSTALLER"
echo "=========================================="
echo ""

echo "[1/5] Checking Python..."

if ! command -v python >/dev/null 2>&1; then
    echo "❌ Python belum terinstall."
    echo "Jalankan:"
    echo "pkg install python"
    exit 1
fi

python --version

echo ""
echo "[2/5] Checking Termux:API..."

if ! command -v termux-sms-list >/dev/null 2>&1; then
    echo "⚠️ Termux:API command tidak ditemukan."
    echo ""
    echo "Install:"
    echo "pkg install termux-api"
    echo ""
    echo "Dan pastikan aplikasi Termux:API juga terinstall."
    exit 1
fi

echo "✅ Termux:API tersedia"

echo ""
echo "[3/5] Installing Python dependencies..."

if [ -f requirements.txt ]; then
    python -m pip install -r requirements.txt
fi

echo ""
echo "[4/5] Creating directories..."

mkdir -p data
mkdir -p logs
mkdir -p sms
mkdir -p whatsapp

echo "✅ Directories ready"

echo ""
echo "[5/5] Checking configuration..."

if [ ! -f .env ]; then

    if [ -f .env.example ]; then
        cp .env.example .env
        echo "⚠️ .env dibuat dari .env.example"
    else
        touch .env
        echo "⚠️ .env dibuat kosong"
    fi

    echo ""
    echo "PENTING:"
    echo "Edit .env dan isi konfigurasi Telegram kamu."
fi

chmod +x start.sh
chmod +x main.py

echo ""
echo "=========================================="
echo "        INSTALLATION COMPLETE"
echo "=========================================="
echo ""
echo "Jalankan:"
echo ""
echo "    ./start.sh"
echo ""
echo "Untuk berhenti:"
echo ""
echo "    CTRL+C"
echo ""
