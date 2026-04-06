import telebot
import openai
import os
import re
from flask import Flask
from threading import Thread
from telebot import types
from geopy.geocoders import Nominatim

# --- Инициализация ---
app = Flask('')
@app.route('/')
def home(): return "Astro-Navigator Live"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

TOKEN = "8614133630:AAFj-F1xh4h5_2B-c2AvGD8gCqg2XX9nUeE"
OPENAI_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = openai.OpenAI(api_key=OPENAI_KEY)
geolocator = Nominatim(user_agent="astro_navigator_bot")

user_states = {}

# --- Шаг 1: Приветствие ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_states[chat_id] = {'step': 'welcome', 'data': {}}
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 Построить мою карту", callback_data="start_collect"))
    
    text = ("Приветствую! 🌌 Я твой персональный Астро-Навигатор.\n\n"
            "Я — нейросеть, обученная на тысячах натальных карт. Помогу понять причины кризисов и увидеть возможности.\n\n"
            "Давай заглянем в твою карту? Это займет 1 минуту.")
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "start_collect")
def ask_date(call):
    chat_id = call.message.chat.id
    user_states[chat_id]['step'] = 'wait_date'
    bot.send_message(chat_id, "Для того чтобы я мог построить твою звездную навигацию, мне нужны твои данные. Начнем? ✨")
    bot.send_message(chat_id, "Напиши дату рождения в формате ДД.ММ.ГГГГ\n(например: 12.05.1990) 🌌")

# --- Шаг 2: Дата ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_date')
def handle_date(message):
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', message.text):
        user_states[message.chat.id]['data']['date'] = message.text
        user_states[message.chat.id]['step'] = 'wait_time'
        bot.send_message(message.chat.id, "В какое время ты родился? Напиши точное время в 24-часовом формате (например: 14:30) 🕒")
    else:
        bot.reply_to(message, "⚠️ Ошибка! Напиши дату строго в формате ДД.ММ.ГГГГ")

# --- Шаг 3: Время ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_time')
def handle_time(message):
    if re.match(r'^\d{2}:\d{2}$', message.text):
        user_states[message.chat.id]['data']['time'] = message.text
        user_states[message.chat.id]['step'] = 'wait_city'
        bot.send_message(message.chat.id, "В каком городе ты родился? 🌎")
    else:
        bot.reply_to(message, "⚠️ Ошибка! Напиши время в формате ЧЧ:ММ")

# --- Шаг 4: Город (С поиском как на скрине 5) ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_city')
def handle_city(message):
    chat_id = message.chat.id
    city_name = message.text
    bot.send_message(chat_id, "Ищу город в базе... 🔍")
    
    try:
        location = geolocator.geocode(city_name, language='ru')
        if location:
            user_states[chat_id]['data']['city'] = location.address
            user_states[chat_id]['data']['coords'] = f"({location.latitude}, {location.longitude})"
            user_states[chat_id]['step'] = 'confirm'
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("✅ Да, всё верно", "❌ Исправить")
            
            res_text = (f"Вот что нашли 🔎:\n\n"
                        f"📍 {location.address} {user_states[chat_id]['data']['coords']}\n\n"
                        f"Всё верно? Если да, я начинаю разбор!")
            bot.send_message(chat_id, res_text, reply_markup=markup)
        else:
            bot.send_message(chat_id, "😕 Город не найден. Попробуй написать название на кириллице или латинице еще раз.")
    except:
        bot.send_message(chat_id, "⚠️ Сервис поиска временно недоступен. Напиши город еще раз.")

# --- Шаг 5: Финал ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'confirm')
def handle_confirm(message):
    chat_id = message.chat.id
    if message.text == "✅ Да, всё верно":
        data = user_states[chat_id]['data']
        bot.send_message(chat_id, "📡 Принято! Генерирую твой Астро-Хак...", reply_markup=types.ReplyKeyboardRemove())
        
        prompt = f"Разбор: {data['date']}, {data['time']}, город {data['city']} {data.get('coords')}."
        Thread(target=ai_call, args=(chat_id, prompt)).start()
        del user_states[chat_id]
    else:
        bot.send_message(chat_id, "Давай начнем сначала. Жми /start")

def ai_call(chat_id, prompt):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Ты Astro-Hacker. Структура: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг."},
                      {"role": "user", "content": prompt}]
        )
        bot.send_message(chat_id, res.choices[0].message.content)
    except:
        bot.send_message(chat_id, "Ошибка связи с ИИ.")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
