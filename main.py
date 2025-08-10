from flask import Flask, request, jsonify, render_template
import threading, json, os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

API_TOKEN = "5000073008:AAF7QHjWD9qpqIVzCZLjijztJzI6W79Qvb4/test"
DATA_FILE = "casino_data.json"
data_lock = threading.Lock()
user_data = {}

def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            user_data = json.load(f)
    else:
        user_data = {}
load_data()

def save_data():
    with data_lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_data, f)

def get_user(uid):
    if str(uid) not in user_data:
        user_data[str(uid)] = {"cakes": 5}
    return user_data[str(uid)]

# Telegram bot
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

main_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("🎲 Играть"),
    KeyboardButton("💰 Баланс")
)

@dp.message()
async def all_msgs(message: types.Message):
    if message.text == "💰 Баланс":
        entry = get_user(message.from_user.id)
        await message.answer(f"Баланс: {entry['cakes']} 🎂")
    elif message.text == "🎲 Играть":
        entry = get_user(message.from_user.id)
        entry["cakes"] += 2
        save_data()
        await message.answer(f"Ты выиграл! Баланс: {entry['cakes']} 🎂")
    else:
        await message.answer("Выбери действие", reply_markup=main_kb)

# Flask app
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_balance")
def get_balance():
    uid = request.args.get("user_id")
    entry = get_user(uid)
    return jsonify({"ok": True, "cakes": entry["cakes"]})

@app.route("/update_balance", methods=["POST"])
def update_balance():
    data = request.get_json()
    uid = data.get("user_id")
    delta = int(data.get("delta", 0))
    entry = get_user(uid)
    entry["cakes"] += delta
    save_data()
    return jsonify({"ok": True, "cakes": entry["cakes"]})

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(run_bot())
