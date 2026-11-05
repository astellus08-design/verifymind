"""VerifyMind — проверка учебных фактов через DeepSeek.
Без DEEPSEEK_API_KEY работает заглушка, с ключом — реальный запрос.
"""

import os
import json
import logging

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

FIELDS = ("verdict", "explanation", "source", "errors", "main")

PROMPT = (
    "Ты — строгий учитель-эксперт по школьной программе РФ. "
    "Проверяй факты ТОЛЬКО по учебникам и ФГОС. "
    "Если не уверен на 100% — отвечай 'Не уверен'. "
    "Не выдумывай источники. "
    "Отвечай СТРОГО в формате JSON с полями: "
    "verdict ('Верно'/'Неверно'/'Не уверен'), "
    "explanation (2-3 предложения), "
    "source (учебник, параграф, стандарт), "
    "errors (что неточно, или 'Ошибок не найдено'), "
    "main (краткий вывод одним предложением)."
)

EMPTY = {
    "verdict": "Не уверен",
    "explanation": "Вопрос пустой.",
    "source": "—",
    "errors": "Нет текста вопроса.",
    "main": "Введите вопрос.",
}


def check_fact(question):
    question = question.strip()
    if not question:
        return dict(EMPTY)

    if not API_KEY:
        logging.info("Ключа нет, отдаю заглушку для: %s", question)
        return {
            "verdict": "Не уверен",
            "explanation": "API-ключ не задан, поэтому реальная проверка не выполнялась.",
            "source": "—",
            "errors": "Проверка недоступна без DEEPSEEK_API_KEY.",
            "main": "Задайте DEEPSEEK_API_KEY, чтобы включить настоящую проверку.",
        }

    logging.info("Запрос к DeepSeek: %s", question)

    try:
        client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com", timeout=30)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": question},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=900,
        )
        content = resp.choices[0].message.content
        if not content:
            raise ValueError("пустой ответ")

        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("модель вернула не объект")

        return {f: str(data.get(f, "—")).strip() for f in FIELDS}

    except Exception as e:
        logging.error("DeepSeek: %s", e)
        return {
            "verdict": "Не уверен",
            "explanation": f"Не удалось получить ответ от модели: {e}",
            "source": "—",
            "errors": "Проверка не выполнена.",
            "main": "Попробуйте позже или проверьте настройки API.",
        }


def format_answer(r):
    line = "=" * 50
    return (
        f"\n{line}\n"
        f"🔍 ВЕРДИКТ: {r.get('verdict', '—')}\n"
        f"💡 ОБЪЯСНЕНИЕ: {r.get('explanation', '—')}\n"
        f"📚 ИСТОЧНИК: {r.get('source', '—')}\n"
        f"⚠️ ОШИБКИ: {r.get('errors', '—')}\n"
        f"✅ ГЛАВНОЕ: {r.get('main', '—')}\n"
        f"{line}\n"
    )


def main():
    mode = "DeepSeek" if API_KEY else "заглушка"
    print("=" * 50)
    print(f"  VerifyMind — режим: {mode}")
    print("=" * 50)
    print("Введите вопрос (или 'выход'):\n")

    while True:
        text = input("➤ Ваш вопрос: ").strip()
        if text.lower() in ("выход", "exit", "quit"):
            print("До встречи!")
            break
        if not text:
            print("⚠️ Пустой ввод. Повторите.\n")
            continue
        print(format_answer(check_fact(text)))


if __name__ == "__main__":
    main()