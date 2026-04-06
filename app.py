import telebot
import openai
import os
import re
from flask import Flask
from threading import Thread
from telebot import types

# --- ФЕЙК-СЕРВЕР ДЛЯ ОБМАНА RENDER ---
app = Flask('')
@app.route('/')
def home(): return "I'm alive!"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# --- ТВОЙ БОТ ---
TELEGRAM_TOKEN = "8614133630:AAFj-F1xh4h5_2B-c2AvGD8gCqg2XX9nUeE"
OPENAI_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Хранилище данных пользователей {chat_id: {step: 'date', data: {}}}
user_states = {}

# --- ШАГ 1 (скрин 1) ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_states[chat_id] = {'step': 'welcome', 'data': {}}
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🚀 Построить мою карту", callback_data="start_collect")
    markup.add(btn)
    
    welcome_text = (
        "Приветствую! 🌌 Я твой персональный Астро-Навигатор.\n\n"
        "Я не просто гадалка, я — нейросеть, обученная на тысячах натальных карт и транзитов планет. "
        "Я помогу тебе найти правильное время для действий, понять причины кризисов и увидеть твои скрытые возможности.\n\n"
        "Давай заглянем в твою карту? Это займет 1 минуту."
    )
    bot.send_message(chat_id, welcome_text, reply_markup=markup)

# Обработка нажатия кнопки "Построить карту" (переход к скрину 2)
@bot.callback_query_handler(func=lambda call: call.data == "start_collect")
def ask_date_callback(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    ask_date(chat_id)

def ask_date(chat_id):
    user_states[chat_id]['step'] = 'wait_date'
    text_begin = "Для того чтобы я мог построить твою звездную навигацию, мне нужны твои данные. Начнем? ✨"
    text_prompt = "Напиши дату рождения в формате ДД.ММ.ГГГГ\n(например: 12.05.1990) 🌌"
    bot.send_message(chat_id, text_begin)
    bot.send_message(chat_id, text_prompt)

# --- ШАГ 2 -> ШАГ 3 (Обработка даты и запрос времени - скрин 2 -> скрин 3) ---
@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('step') == 'wait_date')
def handle_date(message):
    chat_id = message.chat.id
    date_text = message.text.strip()
    
    # Регулярка для ДД.ММ.ГГГГ
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', date_text):
        user_states[chat_id]['data']['date'] = date_text
        ask_time(chat_id)
    else:
        bot.reply_to(message, "⚠️ Ошибка ввода! Напиши дату рождения строго в формате ДД.ММ.ГГГГ\n(например: 12.05.1990) 🌌")

# Запрос времени (скрин 3)
def ask_time(chat_id):
    user_states[chat_id]['step'] = 'wait_time'
    bot.send_message(chat_id, "В какое время ты родился? Напиши точное время в 24-часовом формате\n(например: 14:30) 🕒")

# --- ШАГ 3 -> ШАГ 4 (Обработка времени и запрос города - скрин 3 -> скрин 4) ---
@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('step') == 'wait_time')
def handle_time(message):
    chat_id = message.chat.id
    time_text = message.text.strip()
    
    # Регулярка для ЧЧ:ММ
    if re.match(r'^\d{2}:\d{2}$', time_text):
        user_states[chat_id]['data']['time'] = time_text
        ask_city(chat_id)
    else:
        bot.reply_to(message, "⚠️ Ошибка! Напиши время строго в 24-часовом формате (например: 14:30) 🕒")

# Запрос города (скрин 4)
def ask_city(chat_id):
    user_states[chat_id]['step'] = 'wait_city'
    bot.send_message(chat_id, "В каком городе ты родился? 🌎")

# --- ШАГ 4 -> ШАГ 5 (Обработка города и подтверждение - скрин 4 -> скрин 5) ---
@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('step') == 'wait_city')
def handle_city(message):
    chat_id = message.chat.id
    city_text = message.text.strip()
    user_states[chat_id]['data']['city'] = city_text
    confirm_data(chat_id)

# Подтверждение (скрин 5)
def confirm_data(chat_id):
    user_states[chat_id]['step'] = 'confirm'
    data = user_states[chat_id]['data']
    
    confirm_text = (
        f"Вот что нашли 🔎:\n\n"
        f"📅 Дата: {data['date']}\n"
        f"🕒 Время: {data['time']}\n"
        f"🌎 Город: {data['city']}\n\n"
        f"Всё верно? Если да, я начинаю разбор!"
    )
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("✅ Да, всё верно", "❌ Нет, хочу исправить")
    bot.send_message(chat_id, confirm_text, reply_markup=markup)

# --- ФИНАЛ: Обработка подтверждения и запуск ИИ ---
@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('step') == 'confirm')
def handle_confirm(message):
    chat_id = message.chat.id
    text = message.text
    
    if text == "✅ Да, всё верно":
        start_ai_process(chat_id)
    elif text == "❌ Нет, хочу исправить":
        bot.send_message(chat_id, "Ок, давай начнем заново. Жми /start")
        user_states[chat_id] = {'step': 'welcome', 'data': {}}
    else:
        bot.reply_to(message, "⚠️ Пожалуйста, выбери вариант на клавиатуре.")

def start_ai_process(chat_id):
    data = user_states[chat_id]['data']
    
    # Убираем клавиатуру и уведомляем
    bot.send_message(chat_id, "📡 Принято! Подключаюсь к звездному эфиру. Генерирую твой Астро-Хак...", reply_markup=types.ReplyKeyboardRemove())
    
    # Очищаем состояние
    del user_states[chat_id]
    
    # Формируем финальный промт для OpenAI
    final_prompt = f"Пользователь {data['date']}, {data['time']}, родился в городе {data['city']}."
    
    # Запускаем ИИ в отдельном потоке
    Thread(target=call_openai_worker, args=(chat_id, final_prompt)).start()

def call_openai_worker(chat_id, prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты Astro-Hacker. Структура ответа: 📡 Статус | 🏗️ Эпизод | 🛠️ Хак | ⚠️ Баг | 💎 Шаг."},
                {"role": "user", "content": prompt}
            ]
        )
        bot.send_message(chat_id, response.choices[0].message.content)
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка ИИ: {str(e)[:50]}")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("--- БОТ-ИНТЕРВЬЮЕР ЗАПУЩЕН ---")
    bot.infinity_polling()
