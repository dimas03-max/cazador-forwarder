import json
import subprocess

class TermuxAPIError(Exception):
    pass

def list_sms(limit=100):
    try:
        p = subprocess.run(
            ["termux-sms-list", "-l", str(limit)],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except FileNotFoundError:
        raise TermuxAPIError("termux-sms-list tidak ditemukan. Pastikan Termux:API terpasang.")
    except subprocess.TimeoutExpired:
        raise TermuxAPIError("termux-sms-list timeout.")
    if p.returncode != 0:
        raise TermuxAPIError((p.stderr or p.stdout or "Termux API gagal").strip())
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        raise TermuxAPIError("Output termux-sms-list bukan JSON valid.")
    return data if isinstance(data, list) else []

def check():
    list_sms(1)
    return True
