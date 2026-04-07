import os
import logging
import re
import json
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Health check
@app.route('/', methods=['GET'])
def home():
    return "Astro-Hacker server is live"

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    logger.info("🚀 Новый запрос от PuzzleBot (интегрированная переменная)")

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

    answer = f"""
📡 Astro-Hacker v6.8

Дата рождения: {b_date}
Время рождения: {b_time}
Город: {b_city}

Твой натальный код успешно загружен.
Сейчас формирую полный астрологический разбор...
    """.strip()

    # Важно: возвращаем JSON с ключом "text"
    return jsonify({"text": answer})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
