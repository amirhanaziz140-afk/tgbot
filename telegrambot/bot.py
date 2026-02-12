import telebot
from telebot import types
import os
import openai
import csv
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_KEY")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)
openai.api_key = OPENAI_KEY

user_data = {}

cars = {
    "Toyota Camry": "12 000 000 ₸",
    "Hyundai Tucson": "10 500 000 ₸",
    "BMW X5": "25 000 000 ₸"
}

# START
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🚗 Машиналар", "📝 Заявка")
    bot.send_message(message.chat.id, "Қош келдіңіз! Таңдаңыз:", reply_markup=keyboard)

# Машиналар
@bot.message_handler(func=lambda m: m.text == "🚗 Машиналар")
def show_cars(message):
    text = "Қол жетімді машиналар:\n\n"
    for car, price in cars.items():
        text += f"{car} — {price}\n"
    bot.send_message(message.chat.id, text)

# Заявка бастау
@bot.message_handler(func=lambda m: m.text == "📝 Заявка")
def start_application(message):
    bot.send_message(message.chat.id, "Атыңыз:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.chat.id] = {"name": message.text}
    bot.send_message(message.chat.id, "Телефон номеріңіз:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    user_data[message.chat.id]["phone"] = message.text
    bot.send_message(message.chat.id, "Күні мен уақыты:")
    bot.register_next_step_handler(message, finish_application)

def finish_application(message):
    user_data[message.chat.id]["time"] = message.text
    data = user_data[message.chat.id]

    # CSV файлға сақтау
    with open("applications.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now(),
            data["name"],
            data["phone"],
            data["time"]
        ])

    # Админге жіберу
    admin_text = f"""
Жаңа заявка 🚗

Аты: {data['name']}
Телефон: {data['phone']}
Уақыты: {data['time']}
"""
    bot.send_message(ADMIN_ID, admin_text)

    bot.send_message(message.chat.id, "Заявка қабылданды ✅")

# AI жауап
@bot.message_handler(func=lambda message: True)
def ai_chat(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Сен автосалон менеджерісің."},
                {"role": "user", "content": message.text}
            ]
        )
        answer = response['choices'][0]['message']['content']
        bot.send_message(message.chat.id, answer)
    except:
        bot.send_message(message.chat.id, "AI уақытша жұмыс істемей тұр.")

bot.infinity_polling()
