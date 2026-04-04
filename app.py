import os
import requests
from flask import Flask, request
import openai
import threading # Чтобы бот не ждал OpenAI

app = Flask(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = "ВСТАВЬ_СВОЙ_ТОКЕН"

def generate_and_send(user_id, user_context, is_paid):
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        
        limit_instr = "VIP. Глубокий анализ." if is_paid else "DEMO. Кратко (3-4 предл.)."
        
        system_prompt = "Ты — Astro-Hacker. Структура: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{limit_instr}\n{user_context}"}
            ],
            temperature=0.7
        )
        answer = response.choices[0].message.content

        # Шлем ответ напрямую в Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": user_id, "text": answer, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Error: {e}")

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    data = request.json
    if not data: return "No data", 400
    
    user_id = data.get('user_id')
    user_context = f"Дата: {data.get('b_date')}, Время: {data.get('b_time')}, Город: {data.get('b_city')}"
    is_paid = data.get('is_paid', False)

    # ЗАПУСКАЕМ В ОТДЕЛЬНОМ ПОТОКЕ (PuzzleBot получит ответ мгновенно)
    threading.Thread(target=generate_and_send, args=(user_id, user_context, is_paid)).start()
    
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
