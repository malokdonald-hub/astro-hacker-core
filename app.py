import os
import requests
import openai
from flask import Flask, request
from threading import Thread

app = Flask(__name__)

# --- ВСЕ ДАННЫЕ ВПИСАНЫ НАПРЯМУЮ ---
TELEGRAM_TOKEN = "8614133630:AAHv3Qn4ufI6Mqfn9EB45T0n0EmWB0lgR28"
AI_KEY = "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"

def send_telegram(chat_id, text):
    if not chat_id:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text})
    except:
        pass

def process_and_reply(user_id, user_data):
    try:
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
        send_telegram(user_id, f"Ошибка нейросети: {str(e)[:50]}")

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    # Получаем данные от PuzzleBot
    data = request.json or {}
    
    # Печатаем в лог всё, что пришло, чтобы видеть ошибки
    print(f"ПОЛУЧЕНО ОТ БОТА: {data}")
    
    user_id = data.get('user_id') or data.get('platform_id')
    user_info = f"{data.get('b_date')} {data.get('b_time')} {data.get('b_city')}"

    if user_id:
        Thread(target=process_and_reply, args=(user_id, user_info)).start()
        return "OK", 200
    return "No ID", 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
