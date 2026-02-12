import telebot
from telebot import types
import os
from openpyxl import Workbook, load_workbook

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

# 🚘 Mercedes модельдері
cars = {
    "C": ("C-Class", 25000000),
    "E": ("E-Class", 35000000),
    "S": ("S-Class", 60000000),
    "G": ("G-Class", 120000000),
}

# 📂 Excel жасау
if not os.path.exists("clients.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.append(["Name", "Phone", "Car", "Date"])
    wb.save("clients.xlsx")

# 🟢 START
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚘 Модельдер", "💰 Бюджет бойынша таңдау")
    markup.add("📋 Тест-драйв")

    bot.send_message(
        message.chat.id,
        "✨ Mercedes-Benz ресми цифрлық менеджеріне қош келдіңіз!",
        reply_markup=markup
    )

# 🚘 Модельдер
@bot.message_handler(func=lambda m: m.text == "🚘 Модельдер")
def show_cars(message):
    text = "🚘 Қол жетімді модельдер:\n\n"
    for key, (name, price) in cars.items():
        text += f"{name} — {price:,} ₸\n"
    bot.send_message(message.chat.id, text)

# 💰 Бюджет
@bot.message_handler(func=lambda m: m.text == "💰 Бюджет бойынша таңдау")
def ask_budget(message):
    bot.send_message(message.chat.id, "Бюджетіңізді жазыңыз (мысалы: 30000000):")

@bot.message_handler(func=lambda m: m.text.isdigit())
def recommend_car(message):
    budget = int(message.text)

    recommended = None
    for key, (name, price) in cars.items():
        if budget >= price:
            recommended = name

    if recommended:
        bot.send_message(
            message.chat.id,
            f"💎 Сізге {recommended} ұсынылады.\nСтатус, комфорт және технология балансы мінсіз.\n\nСізге тест-драйв ұйымдастырайық па?"
        )
    else:
        bot.send_message(message.chat.id, "Өкінішке орай бұл бюджетке модель жоқ.")

# 📋 Тест-драйв
@bot.message_handler(func=lambda m: m.text == "📋 Тест-драйв")
def test_drive(message):
    bot.send_message(message.chat.id, "Атыңыз:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    name = message.text
    bot.send_message(message.chat.id, "Телефон:")
    bot.register_next_step_handler(message, get_phone, name)

def get_phone(message, name):
    phone = message.text
    bot.send_message(message.chat.id, "Қай модель?")
    bot.register_next_step_handler(message, get_car, name, phone)

def get_car(message, name, phone):
    car = message.text
    bot.send_message(message.chat.id, "Күні (15.02.2026 15:00):")
    bot.register_next_step_handler(message, save_data, name, phone, car)

def save_data(message, name, phone, car):
    date = message.text

    wb = load_workbook("clients.xlsx")
    ws = wb.active
    ws.append([name, phone, car, date])
    wb.save("clients.xlsx")

    bot.send_message(message.chat.id, "✅ Сұраныс қабылданды!")

# 📊 Excel тек admin көреді
@bot.message_handler(commands=['clients'])
def send_excel(message):
    if message.chat.id == ADMIN_ID:
        with open("clients.xlsx", "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.send_message(message.chat.id, "⛔ Рұқсат жоқ")

print("Bot running...")
bot.infinity_polling()
