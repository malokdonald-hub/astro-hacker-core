import telebot
import openai
import os
import re
from flask import Flask
from threading import Thread
from telebot import types
from geopy.geocoders import Nominatim

# --- Сервер для поддержания жизни на Render ---
app = Flask('')
@app.route('/')
def home(): return "Astro-Bot is Live!"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# --- Настройки ---
TOKEN = "8614133630:AAFeXuWBuhi0KjBeb9j5OAIji-RFjWy-Jdw"
OPENAI_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = openai.OpenAI(api_key=OPENAI_KEY)
geolocator = Nominatim(user_agent="astro_navigator")
user_states = {}

# --- Логика опроса ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_states[chat_id] = {'step': 'welcome', 'data': {}}
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 Построить мою карту", callback_data="start_collect"))
    bot.send_message(chat_id, "Привет! Я твой Астро-Навигатор 🌌\nДавай начнем?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "start_collect")
def ask_date(call):
    user_states[call.message.chat.id]['step'] = 'wait_date'
    bot.send_message(call.message.chat.id, "Введите дату рождения (ДД.ММ.ГГГГ):")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_date')
def handle_date(message):
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', message.text):
        user_states[message.chat.id]['data']['date'] = message.text
        user_states[message.chat.id]['step'] = 'wait_time'
        bot.send_message(message.chat.id, "Введите время рождения (ЧЧ:ММ):")
    else:
        bot.send_message(message.chat.id, "Ошибка! Нужно ДД.ММ.ГГГГ")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_time')
def handle_time(message):
    if re.match(r'^\d{2}:\d{2}$', message.text):
        user_states[message.chat.id]['data']['time'] = message.text
        user_states[message.chat.id]['step'] = 'wait_city'
        bot.send_message(message.chat.id, "В каком городе вы родились?")
    else:
        bot.send_message(message.chat.id, "Ошибка! Нужно ЧЧ:ММ")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_city')
def handle_city(message):
    chat_id = message.chat.id
    location = geolocator.geocode(message.text, language='ru')
    if location:
        user_states[chat_id]['data']['city'] = location.address
        user_states[chat_id]['step'] = 'confirm'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✅ Да", "❌ Нет")
        bot.send_message(chat_id, f"Найдено: {location.address}\nВерно?", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Город не найден, попробуйте еще раз.")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'confirm')
def handle_confirm(message):
    if message.text == "✅ Да":
        data = user_states[message.chat.id]['data']
        bot.send_message(message.chat.id, "Генерирую разбор... Пожалуйста, подождите.", reply_markup=types.ReplyKeyboardRemove())
        def ai_call():
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "Ты Astro-Hacker. Структура: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг."},
                          {"role": "user", "content": f"Разбор для: {data}"}]
            )
            bot.send_message(message.chat.id, res.choices[0].message.content)
        Thread(target=ai_call).start()
        del user_states[message.chat.id]
    else:
        bot.send_message(message.chat.id, "Начнем сначала. Жми /start")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
