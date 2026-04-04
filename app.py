import os
import requests
import openai
from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)

# --- ТВОИ ДАННЫЕ (ПРОВЕРЕНО) ---
TELEGRAM_TOKEN = "8614133630:AAHv3Qn4ufI6Mqfn9EB45T0n0EmWB0lgR28"
# Здесь мы просто берем строку из системы
AI_KEY = os.getenv("OPENAI_API_KEY")

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload)
        print(f"Telegram Log: {r.status_code}")
    except Exception as e:
        print(f"Telegram Error: {e}")

def process_and_reply(user_id, user_data, is_paid):
    try:
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Прямая передача ключа в клиент
        client = openai.OpenAI(api_key=AI_KEY)
        
        limit_instr = "VIP анализ" if is_paid else "DEMO анализ"
        system_prompt = "Ты Astro-Hacker. Структура: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{limit_instr}\nДанные: {user_data}"}
            ]
        )
        
        answer = response.choices[0].message.content
        send_telegram_message(user_id, answer)
        
    except Exception as e:
        print(f"AI Error Detail: {e}")
        send_telegram_message(user_id, "⚠️ Ошибка связи с нейросетью.")

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    data = request.json
    if not data or 'user_id' not in data:
        return "No ID", 400

    user_id = data.get('user_id')
    is_paid = data.get('is_paid', False)
    user_data = f"{data.get('b_date')} {data.get('b_time')} {data.get('b_city')}"

    Thread(target=process_and_reply, args=(user_id, user_data, is_paid)).start()
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
