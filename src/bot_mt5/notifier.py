import requests

from .config import Settings


def send_telegram_alert(settings: Settings, message: str) -> None:
    if not settings.telegram_token or not settings.telegram_chat_id:
        return

    url = f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage"
    payload = {"chat_id": settings.telegram_chat_id, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=10)
    except requests.RequestException:
        pass
