import os

import requests

MAX_BOT_TOKEN = os.getenv("MAX_BOT_TOKEN", "").strip()

WEBHOOK_URL = "ТВОЙ_CLOUDFLARE_URL/webhook"


def subscribe():
    url = "https://platform-api2.max.ru/subscriptions"
    headers = {
        "Authorization": MAX_BOT_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "url": WEBHOOK_URL,
        "update_types": ["message_created"]
    }

    print(f"Пытаюсь подписать бота на: {WEBHOOK_URL}")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Успех! MAX теперь будет присылать сообщения на твой сервер.")
        print("Ответ сервера:", response.json())
    except Exception as e:
        print("❌ Ошибка при подписке.")
        if hasattr(e, 'response') and e.response:
            print("Код ответа:", e.response.status_code)
            print("Текст ошибки:", e.response.text)
        else:
            print("Детали:", e)


if __name__ == "__main__":
    subscribe()