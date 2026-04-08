import os
import logging
import re
import json
from flask import Flask, request, jsonify
import openai

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.error("OPENAI_API_KEY не найден!")

@app.route('/', methods=['GET'])
def home():
    return "Astro-Hacker server is live"

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    logger.info("🚀 Новый запрос от PuzzleBot")

    raw = request.get_data().decode('utf-8', errors='ignore').strip()

    # Парсим кривой JSON от PuzzleBot
    try:
        cleaned = re.sub(r':\s*([^",\s][^,\n}]*)', r': "\1"', raw)
        data = json.loads(cleaned)
    except:
        data = {}

    b_date = data.get('b_date', '—')
    b_time = data.get('b_time', '—')
    b_city = data.get('b_city', '—')

    # ==================== НАСТОЯЩИЙ ПРОМПТ ====================
    system_prompt = """
Ты — Astro-Hacker, жёсткий и вдохновляющий астролог.
Анализируй натальную карту как чертеж судьбы.
Тон: вдохновляющий прагматизм + немного космического вайба.
Структура ответа:
📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг
"""

    user_prompt = f"""
Дата рождения: {b_date}
Время рождения: {b_time}
Город рождения: {b_city}

Дай максимально точный и красивый анализ.
"""

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.75,
            max_tokens=1200
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Ошибка OpenAI: {e}")
        answer = "Ошибка при генерации анализа. Попробуй позже."

    logger.info("✅ Ответ OpenAI сформирован")
    return jsonify({"text": answer})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
