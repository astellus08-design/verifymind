"""VerifyMind — веб-сервер (FastAPI).
POST /webhook принимает сообщение, отвечает вердиктом.
Проверку делает check_fact из main.py.
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Request

from main import check_fact, format_answer

app = FastAPI(title="VerifyMind API")


@app.get("/")
def root():
    return {"status": "ok", "message": "Бот работает"}


@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(400, "Ожидается JSON")

    text = data.get("text") or data.get("message", {}).get("text") or ""
    if not text:
        return {"status": "error", "detail": "Нет текста в сообщении"}

    # Для мессенджера склеиваем в одну строку и убираем линии "====="
    reply = format_answer(check_fact(text))
    reply = " ".join(reply.replace("=" * 50, "").split())

    return {"status": "ok", "reply": reply}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)