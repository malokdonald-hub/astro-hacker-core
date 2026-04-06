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
    return jsonify({"status": "live", "message": "Astro-Hacker ready"})

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    logger.info("🚀 === НОВЫЙ ЗАПРОС ОТ PUZZLEBOT ===")
    
    raw_data = request.get_data().decode('utf-8', errors='ignore').strip()
    logger.info(f"RAW DATA: {raw_data}")

    # === АГРЕССИВНЫЙ ФИКС НЕВАЛИДНОГО JSON ОТ PUZZLEBOT ===
    data = None
    try:
        # Пытаемся почистить и добавить кавычки вокруг строк
        cleaned = re.sub(r':\s*([^",\s][^,\n}]*)', r': "\1"', raw_data)
        cleaned = cleaned.replace('""true""', 'true').replace('""false""', 'false')
        cleaned = cleaned.replace('""', '"')
        data = json.loads(cleaned)
        logger.info("✅ JSON успешно исправлен и распарсен")
    except Exception as e1:
        logger.warning(f"Первый фикс не сработал: {e1}")
        try:
            # Запасной вариант: просто убираем всё лишнее и пробуем
            cleaned = re.sub(r'\s+', ' ', raw_data)
            cleaned = re.sub(r':\s*([^\s,}]+)', r': "\1"', cleaned)
            data = json.loads(cleaned)
        except Exception as e2:
            logger.error(f"Все фиксы провалились: {e2}")
            return jsonify({"bot_answer": f"Ошибка парсинга данных.\nRaw: {raw_data}"}), 400

    logger.info(f"Распарсенные данные: {data}")

    b_date = data.get('b_date')
    b_time = data.get('b_time')
    b_city = data.get('b_city', 'Киев')
    is_paid = data.get('is_paid', True)

    # === ТЕСТОВЫЙ ОТВЕТ (чтобы сразу увидеть результат) ===
    answer = f"""
📡 Astro-Hacker v6.5

Дата рождения: {b_date}
Время рождения: {b_time}
Город: {b_city}

Статус: {'VIP' if is_paid else 'DEMO'}

✅ Данные успешно получены и обработаны.
Сейчас формирую твой полный астрологический разбор...
    """.strip()

    logger.info("✅ Ответ отправлен обратно в бот")
    return jsonify({"bot_answer": answer})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
