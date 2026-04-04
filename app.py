import os
import requests
import openai
from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)

# --- ТВОИ ДАННЫЕ ---
TELEGRAM_TOKEN = "8614133630:AAHv3Qn4ufI6Mqfn9EB45T0n0EmWB0lgR28"
# Берем из Environment Variables на Render
AI_KEY = os.getenv("OPENAI_API_KEY")

def send_telegram_message(chat_id, text):
    """Отправка сообщения через API Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # Мы убрали parse_mode Markdown, чтобы сообщение не блокировалось из-за символов
    payload = {
        "chat_id": chat_id, 
        "text": text
    }
    try:
        r = requests.post(url, json=payload)
        # Это отобразится в логах Render
        print(f"Telegram Send Status: {r.status_code}, Response: {r.text}")
    except Exception as e:
        print(f"Telegram Error: {e}")

def process_and_reply(user_id, user_data, is_paid):
    """Логика AI"""
    try:
        # Проверка наличия ключа
        if not AI_KEY:
            print("ERROR: OpenAI Key is missing in Render Settings!")
            return

        client = openai.OpenAI(api_key=AI_KEY)
        
        limit_instr = "VIP анализ." if is_paid else "DEMO анализ."
        system_prompt = "Ты Astro-Hacker. Структура: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{limit_instr}\nДанные пользователя: {user_data}"}
            ],
            timeout=45 # Добавили время на ожидание ответа
        )
        
        answer = response.choices[0].message.content
        send_telegram_message(user_id, answer)
        
    except Exception as e:
        # Если здесь будет ошибка API OpenAI, мы увидим её в логах
        error_msg = f"AI Error Detail: {str(e)}"
        print(error_msg)
        send_telegram_message(user_id, "⚠️ Ошибка нейросети. Проверьте баланс или ключ OpenAI.")

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    data = request.json
    if not data or 'user_id' not in data:
        return "No user_id", 400

    user_id = data.get('user_id')
    is_paid = data.get('is_paid', False)
    # Собираем данные в одну строку
    user_info = f"Дата: {data.get('b_date')}, Время: {data.get('b_time')}, Город: {data.get('b_city')}"

    # Запускаем в фоне
    Thread(target=process_and_reply, args=(user_id, user_info, is_paid)).start()
    
    return "OK", 200

if __name__ == '__main__':
    # Порт для Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
