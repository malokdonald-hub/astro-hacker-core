import os
import requests
import openai
from flask import Flask, request
from threading import Thread

app = Flask(__name__)

# --- НАСТРОЙКИ (ПРОВЕРЕНО) ---
TELEGRAM_TOKEN = "8614133630:AAHv3Qn4ufI6Mqfn9EB45T0n0EmWB0lgR28"
AI_KEY = os.getenv("OPENAI_API_KEY")

def send_telegram(chat_id, text):
    """Отправка сообщения в Телеграм"""
    if not chat_id:
        print("DEBUG ERROR: Попытка отправить сообщение без chat_id")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text})
        print(f"DEBUG TELEGRAM: Отправлено. Статус: {r.status_code}")
    except Exception as e:
        print(f"DEBUG TELEGRAM ERROR: {e}")

def process_and_reply(user_id, user_data):
    """Запрос к OpenAI и пересылка ответа"""
    print(f"DEBUG AI: Начинаю обработку для ID {user_id}")
    try:
        if not AI_KEY:
            print("DEBUG AI ERROR: Ключ OpenAI отсутствует в настройках Render!")
            send_telegram(user_id, "⚠️ Ошибка: API ключ не настроен.")
            return

        client = openai.OpenAI(api_key=AI_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты Astro-Hacker. Структура: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг"},
                {"role": "user", "content": f"Данные пользователя: {user_data}"}
            ]
        )
        answer = response.choices[0].message.content
        print(f"DEBUG AI: Ответ от OpenAI получен.")
        send_telegram(user_id, answer)
        
    except Exception as e:
        print(f"DEBUG AI ERROR: {str(e)}")
        send_telegram(user_id, f"⚠️ Ошибка нейросети: {str(e)[:100]}")

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    # 1. Логируем входящие сырые данные (для отладки)
    raw_data = request.get_data(as_text=True)
    print(f"RAW DATA FROM BOT: {raw_data}")
    
    # 2. Пытаемся распарсить JSON
    data = request.json or {}
    
    # 3. Достаем ID (пробуем все варианты)
    user_id = data.get('user_id') or data.get('platform_id')
    
    b_date = data.get('b_date', 'не указана')
    b_time = data.get('b_time', 'не указано')
    b_city = data.get('b_city', 'не указан')
    user_info = f"Дата: {b_date}, Время: {b_time}, Город: {b_city}"

    print(f"DEBUG SERVER: Распознан ID: {user_id}")

    if user_id and user_id != "":
        Thread(target=process_and_reply, args=(user_id, user_info)).start()
        return "OK", 200
    else:
        print("DEBUG SERVER ERROR: ID пользователя не найден в запросе.")
        return f"Error: No ID received. Raw data: {raw_data[:50]}", 400

if __name__ == '__main__':
    # Render использует порт из переменной окружения PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
