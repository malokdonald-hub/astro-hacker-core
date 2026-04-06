import os
import logging
from flask import Flask, request, jsonify
import openai

# Настройка логирования (очень важно для отладки на Render)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Ключ OpenAI из переменных окружения Render
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    logger.error("OPENAI_API_KEY не найден в переменных окружения!")

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    logger.info("=== Новый запрос от PuzzleBot ===")
    
    data = request.json
    if not data:
        logger.error("Данные не получены от PuzzleBot")
        return jsonify({"bot_answer": "Ошибка: Данные не получены"}), 400

    logger.info(f"Полученные данные: {data}")

    # 1. Проверяем статус оплаты (работает и со строкой, и с bool)
    is_paid = data.get('is_paid', False)
    if isinstance(is_paid, str):
        is_paid = is_paid.lower() in ('true', '1', 'yes', 'да')

    # 2. Инструкция + лимиты по тарифу
    if is_paid:
        limit_instruction = "СТАТУС: VIP. Дай максимально развёрнутый, глубокий, детальный анализ натальной карты."
        max_tokens = 2000
    else:
        limit_instruction = "СТАТУС: DEMO. Ответь ярко, но кратко (максимум 3-4 предложения). В конце обязательно добавь: 'Чтобы получить полный разбор, нажми кнопку ниже 👇'"
        max_tokens = 600

    system_prompt = """
    SYSTEM PROMPT: ASTRO-HACKER AI (v.6.2)
    Ты — Astro-Hacker. Анализируешь натальную карту как чертеж судьбы.
    Тон: вдохновляющий прагматизм + немного космического вайба.
    Структура ответа:
    📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг
    """

    # Собираем данные пользователя
    user_context = f"""
    {limit_instruction}

    USER DATA:
    Дата рождения: {data.get('b_date') or 'не указано'}
    Время рождения: {data.get('b_time') or 'не указано'}
    Город: {data.get('b_city') or 'не указано'}
    """

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",          # можно поменять на gpt-4o, если хочешь ещё круче
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_context}
            ],
            temperature=0.75,
            max_tokens=max_tokens
        )
        
        answer = response.choices[0].message.content.strip()
        logger.info("Успешно сгенерирован ответ OpenAI")
        
        return jsonify({"bot_answer": answer})
    
    except Exception as e:
        logger.error(f"Ошибка OpenAI: {str(e)}")
        return jsonify({"bot_answer": f"Ошибка ядра Astro-Hacker: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
