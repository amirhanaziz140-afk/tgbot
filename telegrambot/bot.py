import telebot
from telebot import types
import openai
import os
from openpyxl import Workbook, load_workbook

# =============================
# ENV VARIABLES (Render)
# =============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_KEY

# =============================
# Mercedes модельдері
# =============================
cars = {
    "C-Class": "25 000 000 ₸",
    "E-Class": "35 000 000 ₸",
    "S-Class": "60 000 000 ₸",
    "G-Class": "120 000 000 ₸"
}

# =============================
# Excel файл жасау
# =============================
if not os.path.exists("clients.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Clients"
    ws.append(["Name", "Phone", "Car", "Date"])
    wb.save("clients.xlsx")

# =============================
# START
# =============================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚘 Модельдер")
    markup.add("🤖 AI кеңесші")
    markup.add("📋 Тест-драйв")

    bot.send_message(
        message.chat.id,
        "✨ Mercedes-Benz ресми менеджеріне қош келдіңіз!\nҚызметті таңдаңыз:",
        reply_markup=markup
    )

# =============================
# Модельдер
# =============================
@bot.message_handler(func=lambda m: m.text == "🚘 Модельдер")
def show_cars(message):
    text = "🚘 Қол жетімді модельдер:\n\n"
    for car, price in cars.items():
        text += f"{car} — {price}\n"
    bot.send_message(message.chat.id, text)

# =============================
# AI режим
# =============================
@bot.message_handler(func=lambda m: m.text == "🤖 AI кеңесші")
def ai_mode(message):
    bot.send_message(message.chat.id, "Сұрағыңызды жазыңыз:")

@bot.message_handler(func=lambda m: True)
def ai_chat(message):
    if message.text in ["🚘 Модельдер", "📋 Тест-драйв"]:
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional Mercedes-Benz sales consultant."},
                {"role": "user", "content": message.text}
            ]
        )

        bot.send_message(message.chat.id, response.choices[0].message.content)

    except Exception as e:
        bot.send_message(message.chat.id, "AI уақытша жұмыс істемейді.")

# =============================
# Тест-драйв
# =============================
@bot.message_handler(func=lambda m: m.text == "📋 Тест-драйв")
def test_drive(message):
    bot.send_message(message.chat.id, "Атыңыз:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    name = message.text
    bot.send_message(message.chat.id, "Телефон нөміріңіз:")
    bot.register_next_step_handler(message, get_phone, name)

def get_phone(message, name):
    phone = message.text
    bot.send_message(message.chat.id, "Қай модель?")
    bot.register_next_step_handler(message, get_car, name, phone)

def get_car(message, name, phone):
    car = message.text
    bot.send_message(message.chat.id, "Күні (мысалы: 15.02.2026 15:00):")
    bot.register_next_step_handler(message, save_data, name, phone, car)

def save_data(message, name, phone, car):
    date = message.text

    wb = load_workbook("clients.xlsx")
    ws = wb.active
    ws.append([name, phone, car, date])
    wb.save("clients.xlsx")

    bot.send_message(message.chat.id, "✅ Сұраныс сақталды! Біз сізбен байланысамыз.")

# =============================
# Admin ғана Excel көреді
# =============================
@bot.message_handler(commands=['clients'])
def send_excel(message):
    if message.chat.id == ADMIN_ID:
        with open("clients.xlsx", "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.send_message(message.chat.id, "⛔ Рұқсат жоқ")

# =============================
# RUN BOT
# =============================
print("Bot running...")
bot.infinity_polling()
