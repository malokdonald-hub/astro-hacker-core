import os
import requests
import openai
from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)

# --- ТВОИ ДАННЫЕ ---
TELEGRAM_TOKEN = "8614133630:AAHv3Qn4ufI6Mqfn9EB45T0n0EmWB0lgR28"
# Ключ OpenAI вставляем в Dashboard Render (Variable Name: OPENAI_API_KEY)
openai.api_key = os.getenv("OPENAI_API_KEY")

def send_telegram_message(chat_id, text):
    """Отправка сообщения напрямую в Телеграм"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload)
        print(f"Telegram status: {r.status_code}, Response: {r.text}")
    except Exception as e:
        print(f"Telegram Error: {e}")

def process_and_reply(user_id, user_data, is_paid):
    """Логика AI и отправка"""
    try:
        # ТВОЙ ПРОМПТ (БЕЗ ИЗМЕНЕНИЙ)
        limit_instr = "СТАТУС: VIP. Глубокий анализ." if is_paid else "СТАТУС: DEMO. Кратко (3-4 предл.)."
        
        system_prompt = """
        SYSTEM PROMPT: ASTRO-HACKER AI (v.6.1)
        Роль: Ты — Astro-Hacker. Анализируй натальный код как чертеж.
        Тон: Вдохновляющий прагматизм.
        Структура: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг
        """
        
        user_content = f"{limit_instr}\nДанные: {user_data}"

        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        send_telegram_message(user_id, answer)
        
    except Exception as e:
        print(f"AI Error: {e}")
        send_telegram_message(user_id, "⚠️ Ошибка при чтении звезд. Попробуй позже.")

@app.route('/astro_hack', methods=['POST'])
def astro_hack():
    data = request.json
    if not data or 'user_id' not in data:
        return "No user_id", 400

    user_id = data.get('user_id')
    is_paid = data.get('is_paid', False)
    user_data = f"{data.get('b_date')} {data.get('b_time')} {data.get('b_city')}"

    # Запускаем расчет в фоне, чтобы PuzzleBot не ждал
    Thread(target=process_and_reply, args=(user_id, user_data, is_paid)).start()
    
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
