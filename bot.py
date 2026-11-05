import os
import time

import requests

from main import check_fact, format_answer

TOKEN = os.getenv("MAX_BOT_TOKEN")
if not TOKEN:
    raise SystemExit("Не задана переменная окружения MAX_BOT_TOKEN")

API = "https://platform-api2.max.ru"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json"}


def get_updates(marker=None, timeout=30):
    params = {"timeout": timeout, "limit": 100}
    if marker:
        params["marker"] = marker
    r = requests.get(f"{API}/updates", headers=HEADERS, params=params, timeout=timeout + 10)
    r.raise_for_status()
    return r.json()


def send_message(chat_id, text):
    r = requests.post(
        f"{API}/messages",
        headers=HEADERS,
        params={"chat_id": chat_id},
        json={"text": text},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def main_loop():
    from keep_alive import keep_alive
    keep_alive()
    marker = None
    print("Бот запущен, жду сообщения...")

    while True:
        try:
            data = get_updates(marker=marker)
            marker = data.get("marker") or marker

            for upd in data.get("updates", []):
                if upd.get("update_type") != "message_created":
                    continue

                msg = upd.get("message") or {}
                body = msg.get("body") or {}
                text = (body.get("text") or msg.get("text") or "").strip()
                chat_id = (msg.get("recipient") or {}).get("chat_id") or upd.get("chat_id")

                if not text or chat_id is None:
                    continue

                print(f"-> {text[:60]}")
                reply = " ".join(format_answer(check_fact(text)).replace("=" * 50, "").split())
                send_message(chat_id, reply)

        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.HTTPError as e:
            print(f"HTTP {e.response.status_code}: {e.response.text}")
            time.sleep(5)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main_loop()
