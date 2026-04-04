import os
import requests
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Ключи берутся из переменных окружения Render
openai_api_key = os.getenv("OPENAI_API_KEY")

# ВСТАВЬ СВОЙ ТОКЕН НИЖЕ (между кавычками)
TELEGRAM_TOKEN = "ТВОЙ_ТОКЕН_ИЗ_BOTFATHER"

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    # Получаем данные от PuzzleBot
    data = request.json
    if not data:
        return "No Data", 400
    
    # Получаем ID пользователя для прямой отправки сообщения
    user_id = data.get('user_id')
    if not user_id:
        return "No User ID", 400

    # 1. Проверяем статус оплаты
    is_paid = data.get('is_paid', False)
    
    # 2. Инструкция по объему (ТВОЯ ЛОГИКА)
    if is_paid:
        limit_instruction = "СТАТУС: VIP. Дай максимально развернутый, глубокий анализ."
    else:
        limit_instruction = "СТАТУС: DEMO. Ответь ярко, но кратко (макс 3-4 предложения). В конце добавь: 'Чтобы получить полный разбор, нажми кнопку ниже 👇'"

    # ТВОЙ ПРОМПТ (БЕЗ ИЗМЕНЕНИЙ)
    system_prompt = """
    SYSTEM PROMPT: ASTRO-HACKER AI (v.6.1)
    Роль: Ты — Astro-Hacker. Анализируй натальный код как чертеж.
    Тон: Вдохновляющий прагматизм.
    Структура: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг
    """

    user_context = f"""
    {limit_instruction}
    USER DATA:
    Дата: {data.get('b_date')}, Время: {data.get('b_time')}, Город: {data.get('b_city')}
    """

    try:
        # Запрос к OpenAI
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_context}
            ],
            temperature=0.7
        )
        answer = response.choices[0].message.content

        # ОТПРАВКА НАПРЯМУЮ В ТЕЛЕГРАМ (РЕШЕНИЕ ТАЙМАУТА)
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(send_url, json={
            "chat_id": user_id,
            "text": answer,
            "parse_mode": "Markdown"
        })
        
        # PuzzleBot мгновенно получает 'OK' и не виснет
        return "OK", 200
    
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
