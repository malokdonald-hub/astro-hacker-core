import os
import requests
import openai
from flask import Flask, request
from threading import Thread

app = Flask(__name__)

# --- ДАННЫЕ УСТАНОВЛЕНЫ НАПРЯМУЮ ---
TELEGRAM_TOKEN = "8614133630:AAHv3Qn4ufI6Mqfn9EB45T0n0EmWB0lgR28"
# Ключ подтягивается из настроек Render (Environment Variables)
AI_KEY = os.getenv("OPENAI_API_KEY")

def send_telegram(chat_id, text):
    if not chat_id:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text})
        print(f"DEBUG TELEGRAM: {r.status_code}")
    except Exception as e:
        print(f"DEBUG TELEGRAM ERROR: {e}")

def process_and_reply(user_id, user_data):
    try:
        # Проверка ключа перед запуском
        if not AI_KEY:
            print("DEBUG ERROR: Ключ OpenAI не найден в настройках Render!")
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
        send_telegram(user_id, answer)
    except Exception as e:
        print(f"DEBUG AI ERROR: {str(e)}")
        send_telegram(user_id, "⚠️ Ошибка нейросети. Проверьте ключ или баланс.")

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    data = request.json or {}
    # Забираем ID (поддерживаем оба варианта названия)
    user_id = data.get('user_id') or data.get('platform_id')
    
    # Собираем данные, убирая None, если какое-то поле пустое
    b_date = data.get('b_date', '')
    b_time = data.get('b_time', '')
    b_city = data.get('b_city', '')
    user_info = f"{b_date} {b_time} {b_city}".strip()

    print(f"DEBUG SERVER: Received request for ID: {user_id}")

    if user_id and user_info:
        Thread(target=process_and_reply, args=(user_id, user_info)).start()
        return "OK", 200
    else:
        print("DEBUG SERVER ERROR: Missing user_id or user_data")
        return "Missing Data", 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
