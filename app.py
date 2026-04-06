import telebot
import openai
import os

# --- ТВОИ ДАННЫЕ (ВСТАВЛЕНЫ НАПРЯМУЮ) ---
TELEGRAM_TOKEN = "8614133630:AAHv3Qn4ufI6Mqfn9EB45T0n0EmWB0lgR28"
OPENAI_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Пришли мне свои данные (Дата, Время, Город), и я сделаю астро-разбор.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_data = message.text
    chat_id = message.chat.id
    
    bot.send_message(chat_id, "📡 Сигналы получены! Нейросеть расшифровывает твой код...")
    
    try:
        # Запрос к OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты Astro-Hacker. Структура ответа строго: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг"},
                {"role": "user", "content": f"Сделай разбор для данных: {user_data}"}
            ]
        )
        answer = response.choices[0].message.content
        bot.send_message(chat_id, answer)
        
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка: {str(e)[:100]}")

if __name__ == "__main__":
    print("Бот запущен напрямую...")
    bot.infinity_polling()
