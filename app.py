import telebot
import openai
import os
from flask import Flask
from threading import Thread

# --- ФЕЙК-СЕРВЕР ДЛЯ ОБМАНА RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run_flask():
    # Render дает порт в переменной окружения PORT
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# --- ТВОЙ БОТ ---
TELEGRAM_TOKEN = "8614133630:AAFj-F1xh4h5_2B-c2AvGD8gCqg2XX9nUeE"
OPENAI_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Astro-Hacker онлайн! Пришли данные для разбора.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "📡 Анализирую...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты Astro-Hacker. Структура: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг."},
                {"role": "user", "content": message.text}
            ]
        )
        bot.send_message(chat_id, response.choices[0].message.content)
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка: {str(e)[:50]}")

if __name__ == "__main__":
    # Запускаем сайт в фоне
    t = Thread(target=run_flask)
    t.start()
    # Запускаем бота в основном потоке
    print("--- БОТ ЗАПУЩЕН ---")
    bot.infinity_polling()
