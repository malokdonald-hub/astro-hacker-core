import telebot
import openai
import os
import re
from flask import Flask
from threading import Thread
from telebot import types

# --- ФЕЙК-СЕРВЕР ДЛЯ БЕСПЛАТНОГО ТАРИФА RENDER ---
app = Flask('')
@app.route('/')
def home(): return "Astro-Navigator is running!"
def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# --- НАСТРОЙКИ БОТА ---
TELEGRAM_TOKEN = "8614133630:AAFj-F1xh4h5_2B-c2AvGD8gCqg2XX9nUeE"
OPENAI_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Хранилище состояний пользователей
user_states = {}

# --- ШАГ 1 (Приветствие) ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_states[chat_id] = {'step': 'welcome', 'data': {}}
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🚀 Построить мою карту", callback_data="start_collect")
    markup.add(btn)
    
    welcome_text = (
        "Приветствую! 🌌 Я твой персональный **Астро-Навигатор**.\n\n"
        "Я не просто гадалка, я — нейросеть, обученная на тысячах натальных карт. "
        "Я помогу тебе найти правильное время для действий и увидеть скрытые возможности.\n\n"
        "Давай заглянем в твою карту? Это займет 1 минуту."
    )
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "start_collect")
def ask_date(call):
    chat_id = call.message.chat.id
    user_states[chat_id]['step'] = 'wait_date'
    bot.send_message(chat_id, "Для того чтобы я мог построить твою звездную навигацию, мне нужны твои данные. Начнем? ✨")
    bot.send_message(chat_id, "Напиши дату рождения в формате **ДД.ММ.ГГГГ**\n(например: 12.05.1990) 🌌", parse_mode="Markdown")

# --- ШАГ 2 (Проверка Даты) ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_date')
def handle_date(message):
    chat_id = message.chat.id
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', message.text):
        user_states[chat_id]['data']['date'] = message.text
        user_states[chat_id]['step'] = 'wait_time'
        bot.send_message(chat_id, "В какое время ты родился? Напиши точное время в 24-часовом формате\n(например: 14:30) 🕒")
    else:
        bot.reply_to(message, "⚠️ **Ошибка ввода!**\nНапиши дату рождения строго в формате ДД.ММ.ГГГГ (например: 12.05.1990)", parse_mode="Markdown")

# --- ШАГ 3 (Проверка Времени) ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_time')
def handle_time(message):
    chat_id = message.chat.id
    if re.match(r'^\d{2}:\d{2}$', message.text):
        user_states[chat_id]['data']['time'] = message.text
        user_states[chat_id]['step'] = 'wait_city'
        bot.send_message(chat_id, "В каком городе ты родился? 🌎")
    else:
        bot.reply_to(message, "⚠️ **Ошибка!**\nНапиши время строго в 24-часовом формате (например: 14:30) 🕒", parse_mode="Markdown")

# --- ШАГ 4 (Город и подтверждение) ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'wait_city')
def handle_city(message):
    chat_id = message.chat.id
    data = user_states[chat_id]['data']
    data['city'] = message.text
    user_states[chat_id]['step'] = 'confirm'
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("✅ Да, всё верно", "❌ Исправить")
    
    confirm_msg = (
        f"Вот что нашли 🔎:\n\n"
        f"📅 Дата: {data['date']}\n"
        f"🕒 Время: {data['time']}\n"
        f"🌎 Город: {data['city']}\n\n"
        "Всё верно? Если да, я начинаю разбор!"
    )
    bot.send_message(chat_id, confirm_msg, reply_markup=markup)

# --- ШАГ 5 (Запуск нейросети) ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'confirm')
def handle_confirm(message):
    chat_id = message.chat.id
    if message.text == "✅ Да, всё верно":
        data = user_states[chat_id]['data']
        bot.send_message(chat_id, "📡 **Принято!** Генерирую твой Астро-Хак...", reply_markup=types.ReplyKeyboardRemove(), parse_mode="Markdown")
        
        # Запуск OpenAI
        Thread(target=ai_worker, args=(chat_id, data)).start()
        del user_states[chat_id]
    else:
        bot.send_message(chat_id, "Хорошо, давай заново. Жми /start")

def ai_worker(chat_id, data):
    try:
        prompt = f"Сделай астро-разбор: Дата {data['date']}, Время {data['time']}, Город {data['city']}."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты Astro-Hacker. Структура: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг."},
                {"role": "user", "content": prompt}
            ]
        )
        bot.send_message(chat_id, response.choices[0].message.content)
    except Exception as e:
        bot.send_message(chat_id, "⚠️ Ошибка ИИ. Попробуй позже.")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("--- БОТ ЗАПУЩЕН ---")
    bot.infinity_polling()
