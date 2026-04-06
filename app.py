import telebot
import openai
import os
import re
from flask import Flask
from threading import Thread
from telebot import types
from geopy.geocoders import Nominatim

app = Flask('')
@app.route('/')
def home(): return "OK"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

TOKEN = "8614133630:AAFeXuWBuhi0KjBeb9j5OAIji-RFjWy-Jdw"
OPENAI_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = openai.OpenAI(api_key=OPENAI_KEY)
geolocator = Nominatim(user_agent="astro_final_fix")
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_states[chat_id] = {'step': 'date', 'data': {}}
    bot.send_message(chat_id, "Привет! Введите дату рождения (ДД.ММ.ГГГГ):")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'date')
def h_date(message):
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', message.text):
        user_states[message.chat.id]['data']['date'] = message.text
        user_states[message.chat.id]['step'] = 'time'
        bot.send_message(message.chat.id, "Введите время (ЧЧ:ММ):")
    else:
        bot.send_message(message.chat.id, "Формат: ДД.ММ.ГГГГ")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'time')
def h_time(message):
    if re.match(r'^\d{2}:\d{2}$', message.text):
        user_states[message.chat.id]['data']['time'] = message.text
        user_states[message.chat.id]['step'] = 'city'
        bot.send_message(message.chat.id, "В каком городе вы родились?")
    else:
        bot.send_message(message.chat.id, "Формат: ЧЧ:ММ")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'city')
def h_city(message):
    chat_id = message.chat.id
    city = message.text
    bot.send_message(chat_id, "Минутку... 🔍")
    try:
        # Защита от GeocoderUnavailable (как в image_c762c2.jpg)
        loc = geolocator.geocode(city, timeout=10)
        res_city = loc.address if loc else city
    except:
        res_city = city
    
    user_states[chat_id]['data']['city'] = res_city
    user_states[chat_id]['step'] = 'confirm'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("✅ Да", "❌ Заново")
    bot.send_message(chat_id, f"Город: {res_city}. Верно?", reply_markup=markup)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'confirm')
def h_conf(message):
    if message.text == "✅ Да":
        data = user_states[message.chat.id]['data']
        bot.send_message(message.chat.id, "Генерирую разбор через ИИ...", reply_markup=types.ReplyKeyboardRemove())
        def run_ai():
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Сделай астро-разбор: {data}"}]
            )
            bot.send_message(message.chat.id, res.choices[0].message.content)
        Thread(target=run_ai).start()
        del user_states[message.chat.id]
    else:
        bot.send_message(message.chat.id, "Жми /start")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
