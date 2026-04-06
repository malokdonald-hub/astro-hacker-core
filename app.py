import os
import logging
import re
import json
from flask import Flask, request

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Health check
@app.route('/', methods=['GET'])
def home():
    return "Astro-Hacker server is live ✅"

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    logger.info("🚀 === НОВЫЙ ЗАПРОС ОТ PUZZLEBOT ===")
    
    raw = request.get_data().decode('utf-8', errors='ignore').strip()
    logger.info(f"RAW DATA: {raw}")

    # Агрессивная очистка кривого JSON от PuzzleBot
    try:
        cleaned = re.sub(r':\s*([^",\s][^,\n}]*)', r': "\1"', raw)
        cleaned = cleaned.replace('""true""', 'true').replace('""false""', 'false')
        data = json.loads(cleaned)
        logger.info("✅ JSON успешно распарсен")
    except:
        data = {}

    b_date = data.get('b_date', 'не указано')
    b_time = data.get('b_time', 'не указано')
    b_city = data.get('b_city', 'не указано')

    # === ЧИСТЫЙ ТЕКСТ (именно то, что нужно PuzzleBot) ===
    answer = f"""
📡 Astro-Hacker v6.6

Дата рождения: {b_date}
Время рождения: {b_time}
Город: {b_city}

✅ Данные успешно получены.
Сейчас формирую твой полный астрологический разбор...
    """.strip()

    logger.info("✅ ЧИСТЫЙ ТЕКСТ ОТПРАВЛЕН В БОТ")
    return answer   # ←←← Это самое важное!


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
