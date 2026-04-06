import telebot
import openai
import os
import re
from flask import Flask
from threading import Thread
from telebot import types
from geopy.geocoders import Nominatim

# --- Сервер для Render ---
app = Flask('')
@app.route('/')
def home(): return "Astro-Bot Status: Online"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# --- Настройки (Проверь токен!) ---
TOKEN = "8614133630:AAFeXuWBuhi0KjBeb9j5OAIji-RFjWy-Jdw"
OPENAI_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = openai.OpenAI(api_key=OPENAI_KEY)
geolocator = Nominatim(user_agent="astro_navigator_v2")
user_states = {}

# --- Команды ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_states[chat_id] = {'step': 'welcome', 'data': {}}
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 Построить мою карту", callback_data="start_collect"))
    
    text = ("Приветствую! 🌌 Я твой персональный Астро-Навигатор.\n\n"
            "Давай заглянем в твою карту? Это займет 1 минуту.")
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "start_collect")
def ask_date(call):
    chat_id = call.message.chat.id
    user_states[chat_id]['step'] = 'wait_date'
    bot.send_message(chat_id, "Напиши дату рождения в формате **ДД.ММ.ГГГГ**\n(например: 12.05.1990) 🌌", parse_mode="Markdown")

# --- Сбор данных ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_date')
def handle_date(message):
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', message.text):
        user_states[message.chat.id]['data']['date'] = message.text
        user_states[message.chat.id]['step'] = 'wait_time'
        bot.send_message(message.chat.id, "В какое время ты родился? (например: 14:30) 🕒")
    else:
        bot.send_message(message.chat.id, "⚠️ Ошибка! Формат: ДД.ММ.ГГГГ")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_time')
def handle_time(message):
    if re.match(r'^\d{2}:\d{2}$', message.text):
        user_states[message.chat.id]['data']['time'] = message.text
        user_states[message.chat.id]['step'] = 'wait_city'
        bot.send_message(message.chat.id, "В каком городе ты родился? 🌎")
    else:
        bot.send_message(message.chat.id, "⚠️ Ошибка! Формат: ЧЧ:ММ")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_city')
def handle_city(message):
    chat_id = message.chat.id
    city_input = message.text
    user_states[chat_id]['data']['city'] = city_input # Сохраняем как есть на случай ошибки Geopy
    
    bot
