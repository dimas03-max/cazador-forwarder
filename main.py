#!/usr/bin/env python3

import os
import sys
import time
import signal
import subprocess
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

processes = []
running = True


def log(message):
    print(f"[CΛZΛDØR] {message}", flush=True)


def start_process(name, command):
    log(f"Starting {name}...")

    process = subprocess.Popen(
        command,
        cwd=BASE_DIR
    )

    processes.append((name, process))

    log(f"{name} started (PID {process.pid})")

    return process


def stop_all(signum=None, frame=None):
    global running

    if not running:
        return

    running = False

    log("Stopping all services...")

    for name, process in processes:
        if process.poll() is None:
            log(f"Stopping {name}...")
            process.terminate()

    time.sleep(1)

    for name, process in processes:
        if process.poll() is None:
            process.kill()

    log("CΛZΛDØR FORWARDER stopped.")
    sys.exit(0)


def main():

    signal.signal(signal.SIGINT, stop_all)
    signal.signal(signal.SIGTERM, stop_all)

    print()
    print("╔══════════════════════════════════════════╗")
    print("║        CΛZΛDØR FORWARDER v3             ║")
    print("╠══════════════════════════════════════════╣")
    print("║ SMS Forwarder      → Telegram            ║")
    print("║ WhatsApp Bridge    → Telegram            ║")
    print("╚══════════════════════════════════════════╝")
    print()

    # SMS FORWARDER
    sms = start_process(
        "SMS Forwarder",
        [sys.executable, "-m", "sms.main"]
    )

    # WHATSAPP BRIDGE
    whatsapp = start_process(
        "WhatsApp Bridge",
        [sys.executable, "-m", "whatsapp.bridge"]
    )

    print()
    log("==========================================")
    log(" SMS Forwarder : ONLINE")
    log(" WhatsApp      : ONLINE")
    log(" Telegram      : shared configuration")
    log("==========================================")
    print()

    while running:

        # Check SMS process
        if sms.poll() is not None:
            log(f"SMS Forwarder stopped (exit={sms.returncode})")

        # Check WhatsApp process
        if whatsapp.poll() is not None:
            log(f"WhatsApp Bridge stopped (exit={whatsapp.returncode})")

        # Kalau keduanya mati, launcher ikut berhenti
        if sms.poll() is not None and whatsapp.poll() is not None:
            log("All services stopped.")
            break

        time.sleep(2)

    stop_all()


if __name__ == "__main__":
    main()
