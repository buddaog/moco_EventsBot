import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram import Router

with open("config.json", "r") as f:
    config = json.load(f)

TELEGRAM_TOKEN = config["telegram_token"]
ALLOWED_USERS = config.get("allowed_users", [])

MAPS = [
    "Downtown", "Farm", "Ranch", "Fairgrounds", "Harbor",
    "Lab", "Bazaar", "Trainyard", "Boardwalk", "Park",
    "Studio", "Suburb", "Complex"
]

EVENT_TYPES = ["Overcharged", "Boss", "Escort", "Dojo", "Rift"]

dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def start_cmd(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("⛔️ У вас нет доступа к этому боту.")
        return
    await message.answer("Привет! Напиши /events, чтобы выбрать карту и посмотреть ближайшие ивенты.")

@router.message(Command("events"))
async def events_cmd(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("⛔️ У вас нет доступа к этому боту.")
        return

    keyboard = InlineKeyboardBuilder()
    for name in MAPS:
        keyboard.button(text=name, callback_data=f"map_{name}")
    keyboard.adjust(2)
    await message.answer("Выбери карту:", reply_markup=keyboard.as_markup())

@router.callback_query(F.data.startswith("map_"))
async def map_selected(callback: types.CallbackQuery):
    map_name = callback.data.replace("map_", "")

    keyboard = InlineKeyboardBuilder()
    for ev_type in EVENT_TYPES:
        keyboard.button(text=ev_type, callback_data=f"filter_{map_name}_{ev_type}")
    keyboard.adjust(2)

    await callback.message.edit_text(
        f"Выбранная карта: {map_name}\nВыбери фильтры:",
        reply_markup=keyboard.as_markup()
    )

@router.callback_query(F.data.startswith("filter_"))
async def filter_selected(callback: types.CallbackQuery):
    _, map_name, ev_type = callback.data.split("_", 2)
    await callback.message.edit_text(
        f"🔍 Ближайшие события на карте {map_name} типа {ev_type} будут здесь... (заглушка)"
    )

async def main():
    bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
