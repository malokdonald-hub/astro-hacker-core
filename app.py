import os
import requests
from flask import Flask, request, jsonify
import openai
from threading import Thread

app = Flask(__name__)

# ТВОИ ДАННЫЕ
TELEGRAM_TOKEN = "ВСТАВЬ_СВОЙ_ТОКЕН_БОТА_ЗДЕСЬ"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def send_to_telegram(chat_id, text):
    """Прямая отправка сообщения пользователю через API Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    r = requests.post(url, json=payload)
    print(f"Direct Telegram Response: {r.status_code} - {r.text}")

def process_astro_data(user_id, context):
    """Фоновая задача: запрос к AI и отправка результата"""
    try:
        print(f"Starting AI for user {user_id}...")
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты астролог-хакер. Дай краткий, дерзкий прогноз на основе данных пользователя."},
                {"role": "user", "content": context}
            ]
        )
        answer = response.choices[0].message.content
        print("AI finished. Sending to Telegram...")
        send_to_telegram(user_id, answer)
    except Exception as e:
        print(f"Error in background process: {e}")

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"status": "error", "message": "no user_id"}), 400

    # Собираем данные
    context = f"Дата: {data.get('b_date')}, Время: {data.get('b_time')}, Город: {data.get('b_city')}"
    
    # ЗАПУСКАЕМ В ОТДЕЛЬНОМ ПОТОКЕ, чтобы PuzzleBot не ждал
    Thread(target=process_astro_data, args=(user_id, context)).start()
    
    # Мгновенно отвечаем PuzzleBot, что всё ок
    return jsonify({"status": "accepted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
