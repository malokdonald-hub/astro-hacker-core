import os
import requests
import openai
from flask import Flask, request
from threading import Thread

app = Flask(__name__)

# --- ДАННЫЕ (ПРОВЕРЕНО) ---
TELEGRAM_TOKEN = "8614133630:AAHv3Qn4ufI6Mqfn9EB45T0n0EmWB0lgR28"
AI_KEY = os.getenv("OPENAI_API_KEY")

def send_telegram_debug(chat_id, text):
    """Отправка сообщения с выводом результата в логи Render"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text})
        print(f"DEBUG TELEGRAM: Status {r.status_code}, Response: {r.text}")
    except Exception as e:
        print(f"DEBUG TELEGRAM ERROR: {e}")

def process_and_reply(user_id, user_data, is_paid):
    print(f"DEBUG AI: Starting process for user {user_id}")
    try:
        if not AI_KEY or "sk-" not in AI_KEY:
            print("DEBUG AI ERROR: API Key is missing or invalid in Render settings!")
            send_telegram_debug(user_id, "⚠️ Ошибка: Ключ OpenAI не настроен в Render.")
            return

        client = openai.OpenAI(api_key=AI_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты Astro-Hacker. Структура: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг"},
                {"role": "user", "content": f"Данные: {user_data}"}
            ]
        )
        
        answer = response.choices[0].message.content
        print("DEBUG AI: Response received from OpenAI")
        send_telegram_debug(user_id, answer)
        
    except Exception as e:
        error_detail = str(e)
        print(f"DEBUG AI CRITICAL ERROR: {error_detail}")
        # Отправляем тех. информацию прямо в бот, чтобы ты увидел ошибку
        send_telegram_debug(user_id, f"⚠️ Техническая ошибка OpenAI:\n{error_detail[:100]}")

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    data = request.json
    print(f"DEBUG SERVER: Received POST request: {data}")
    
    if not data or 'user_id' not in data:
        print("DEBUG SERVER ERROR: No user_id in request")
        return "No ID", 400

    user_id = data.get('user_id')
    user_data = f"{data.get('b_date')} {data.get('b_time')} {data.get('b_city')}"

    Thread(target=process_and_reply, args=(user_id, user_data, False)).start()
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
