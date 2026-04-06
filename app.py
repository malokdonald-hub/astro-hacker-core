import os
import logging
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Health check — чтобы видеть, жив ли сервер
@app.route('/', methods=['GET'])
def home():
    logger.info("✅ Health check / вызван")
    return jsonify({
        "status": "live",
        "message": "Astro-Hacker сервер работает. Отправляй POST на /astro_hack"
    })

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    logger.info("🚀 === НОВЫЙ ЗАПРОС ОТ PUZZLEBOT ===")
    logger.info(f"Headers: {dict(request.headers)}")
    
    raw_data = request.get_data()
    logger.info(f"Raw data: {raw_data}")
    
    try:
        data = request.json
        logger.info(f"Parsed JSON: {data}")
    except Exception as e:
        logger.error(f"Не удалось распарсить JSON: {e}")
        data = None

    if not data:
        logger.error("Данные не получены!")
        return jsonify({"bot_answer": "Ошибка: данные от PuzzleBot не дошли"}), 400

    # Логируем всё, что пришло
    b_date = data.get('b_date')
    b_time = data.get('b_time')
    b_city = data.get('b_city')
    is_paid = data.get('is_paid', True)

    logger.info(f"Дата: {b_date} | Время: {b_time} | Город: {b_city} | Paid: {is_paid}")

    # Тестовый ответ (чтобы проверить, доходит ли вообще)
    answer = f"""
📡 Astro-Hacker v6.3

Дата: {b_date}
Время: {b_time}
Город: {b_city}

Статус: {'VIP' if is_paid else 'DEMO'}
Анализ успешно сгенерирован (тестовый режим).
    """

    logger.info("✅ Ответ сформирован и отправлен обратно")
    return jsonify({"bot_answer": answer.strip()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
