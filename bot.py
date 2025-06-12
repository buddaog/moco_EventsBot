import logging
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import os

# Загрузка конфигурации
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = os.getenv("TELEGRAM_TOKEN", config["telegram_token"])
ALLOWED_USERS = config["allowed_users"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Пример списка карт
maps = [
    "Downtown", "Outskirts", "Highland", "Spine", "Chinatown", "Parkside",
    "Boardwalk", "Beach", "Overpass", "Undercity", "Cyberville", "Desert", "Lakeside"
]

# Пример событий
event_types = ["Overcharged", "Boss", "Escort", "Dojo", "Rift"]

# Заглушка — возвращает фиктивные ивенты
def get_events_for_map(selected_map, selected_types):
    return [f"{etype} Event on {selected_map} at 18:00" for etype in selected_types]

@dp.message_handler(commands=['start', 'events'])
async def show_maps(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        return
    keyboard = InlineKeyboardMarkup(row_width=2)
    for m in maps:
        keyboard.add(InlineKeyboardButton(m, callback_data=f"map:{m}"))
    await message.reply("Выберите карту:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("map:"))
async def choose_map(callback_query: types.CallbackQuery):
    selected_map = callback_query.data.split(":")[1]
    keyboard = InlineKeyboardMarkup(row_width=2)
    for e in event_types:
        keyboard.add(InlineKeyboardButton(e, callback_data=f"event:{selected_map}:{e}"))
    await callback_query.message.edit_text(f"Вы выбрали: {selected_map}
Теперь выберите тип ивента:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("event:"))
async def show_events(callback_query: types.CallbackQuery):
    _, selected_map, event_type = callback_query.data.split(":")
    events = get_events_for_map(selected_map, [event_type])
    await callback_query.message.edit_text(f"События на карте {selected_map} ({event_type}):

" + "
".join(events))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
