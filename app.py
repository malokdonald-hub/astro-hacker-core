import os
import logging
import json
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Health check
@app.route('/', methods=['GET'])
def home():
    logger.info("✅ Health check / вызван")
    return jsonify({"status": "live", "message": "Astro-Hacker ready"})

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    logger.info("🚀 === НОВЫЙ ЗАПРОС ОТ PUZZLEBOT ===")
    
    # Получаем сырые данные
    raw_data = request.get_data().decode('utf-8').strip()
    logger.info(f"Raw data от PuzzleBot: {raw_data}")

    # Пытаемся парсить разными способами
    data = None
    
    # 1. Стандартный JSON
    try:
        data = request.get_json(force=True, silent=True)
    except:
        pass

    # 2. Если не получилось — пытаемся почистить кривой формат PuzzleBot
    if not data:
        try:
            # Убираем лишние переносы и пробелы
            cleaned = raw_data.replace('\n', '').replace('\r', '').strip()
            # Если нет внешних фигурных скобок — добавляем
            if not cleaned.startswith('{'):
                cleaned = '{' + cleaned + '}'
            data = json.loads(cleaned)
            logger.info("✅ Успешно почистили и распарсили кривой JSON")
        except Exception as e:
            logger.error(f"Не удалось распарсить даже после очистки: {e}")

    if not data:
        logger.error("Данные не получены вообще")
        return jsonify({"bot_answer": "Ошибка: данные от PuzzleBot не дошли"}), 400

    logger.info(f"Распарсенные данные: {data}")

    # Берём нужные поля
    b_date = data.get('b_date')
    b_time = data.get('b_time')
    b_city = data.get('b_city', 'Киев')
    is_paid = data.get('is_paid', True)

    # Тестовый ответ (чтобы сразу увидеть, что всё работает)
    answer = f"""
📡 Astro-Hacker v6.4

Дата рождения: {b_date}
Время: {b_time}
Город: {b_city}

Статус: {'VIP' if is_paid else 'DEMO'}

Твой натальный код успешно проанализирован. 
Сейчас я формирую полный разбор...
    """.strip()

    logger.info("✅ Ответ отправлен обратно в PuzzleBot")
    return jsonify({"bot_answer": answer})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
