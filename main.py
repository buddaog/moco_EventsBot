import json
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.dispatcher import filters

# Загрузка конфигурации
with open("config.json", "r") as f:
    config = json.load(f)

TELEGRAM_TOKEN = config["telegram_token"]
ALLOWED_USERS = config.get("allowed_users", [])

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Список карт и ивентов
MAPS = [
    "Downtown", "Farm", "Ranch", "Fairgrounds", "Harbor",
    "Lab", "Bazaar", "Trainyard", "Boardwalk", "Park",
    "Studio", "Suburb", "Complex"
]

EVENT_TYPES = ["Overcharged", "Boss", "Escort", "Dojo", "Rift"]

# Команда /start
@dp.message_handler(CommandStart())
async def start_handler(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("⛔️ У вас нет доступа к этому боту.")
        return
    await message.answer("Привет! Напиши /events, чтобы выбрать карту и посмотреть ближайшие ивенты.")

# Команда /events
@dp.message_handler(Command("events"))
async def events_handler(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("⛔️ У вас нет доступа к этому боту.")
        return

    keyboard = InlineKeyboardMarkup(row_width=2)
    for name in MAPS:
        keyboard.insert(InlineKeyboardButton(text=name, callback_data=f"map_{name}"))

    await message.answer("Выбери карту:", reply_markup=keyboard)

# Обработка выбора карты
@dp.callback_query_handler(filters.Text(startswith="map_"))
async def map_callback_handler(query: types.CallbackQuery):
    map_name = query.data.replace("map_", "")

    keyboard = InlineKeyboardMarkup(row_width=2)
    for ev_type in EVENT_TYPES:
        keyboard.insert(InlineKeyboardButton(text=ev_type, callback_data=f"filter_{map_name}_{ev_type}"))

    await query.message.edit_text(f"Выбранная карта: {map_name}\nВыбери фильтры:", reply_markup=keyboard)

# Обработка выбора фильтра
@dp.callback_query_handler(filters.Text(startswith="filter_"))
async def filter_callback_handler(query: types.CallbackQuery):
    _, map_name, ev_type = query.data.split("_", 2)

    # Здесь можно подключить реальный сбор данных о событиях
    await query.message.edit_text(f"🔍 Ближайшие события на карте {map_name} типа {ev_type} будут здесь... (заглушка)")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
