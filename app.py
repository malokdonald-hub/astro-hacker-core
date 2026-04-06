import telebot
import openai
import os

# --- ТВОИ ОБНОВЛЕННЫЕ ДАННЫЕ ---
TELEGRAM_TOKEN = "8614133630:AAFj-F1xh4h5_2B-c2AvGD8gCqg2XX9nUeE"
OPENAI_API_KEY = "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"

# Инициализация бота и клиента OpenAI
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

print("--- БОТ ЗАПУЩЕН НАПРЯМУЮ ---")

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "🚀 **Astro-Hacker на связи!**\n\n"
        "Я больше не завишу от конструкторов. Пришли мне свои данные одним сообщением:\n"
        "🔹 Дата рождения\n"
        "🔹 Время\n"
        "🔹 Город\n\n"
        "И я сразу выдам тебе хак системы!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_input = message.text
    
    # Уведомление пользователя
    bot.send_message(chat_id, "📡 **Сигналы приняты.** Нейросеть подключается к эфиру...")
    
    try:
        # Запрос к нейросети
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты Astro-Hacker. Структура ответа: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг. Пиши дерзко и по делу."},
                {"role": "user", "content": f"Сделай разбор по этим данным: {user_input}"}
            ]
        )
        
        answer = response.choices[0].message.content
        bot.send_message(chat_id, answer)
        print(f"DEBUG: Ответ отправлен пользователю {chat_id}")

    except Exception as e:
        error_msg = f"⚠️ **Ошибка доступа:** {str(e)[:100]}"
        bot.send_message(chat_id, error_msg)
        print(f"DEBUG ERROR: {e}")

if __name__ == "__main__":
    # Запуск бота в режиме бесконечного опроса
    bot.infinity_polling()
