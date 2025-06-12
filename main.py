import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import os

# 🔐 Ваш токен
TELEGRAM_TOKEN = "7736390099:AAHIDSncyfAPCx85XWB-4mxSw6dZCWhZdX0"

# 📍 Карты из Mo.co
maps = [
    "Shrine Village", "Overgrown Ruins", "Infested Forest", "Cave Of Spirits", "Castle Walls",
    "Summoning Grounds", "Sewers", "Corrupted Village", "Corrupted Ruins", "Corrupted Forest",
    "Corrupted Cave", "Corrupted Castle", "Corrupted Shrine"
]

# 🛠️ Инициализация
bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# 📦 Хендлер старт
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Используй /events чтобы посмотреть ивенты по картам.")

# 📦 Хендлер /events
@dp.message(Command("events"))
async def cmd_events(message: Message):
    keyboard = [
        [InlineKeyboardButton(text=map_name, callback_data=f"map:{map_name}")]
        for map_name in maps
    ]
    await message.answer("📍 Выбери карту:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

# 📦 Обработка выбора карты
@dp.callback_query(F.data.startswith("map:"))
async def on_map_selected(callback: CallbackQuery):
    map_name = callback.data.split("map:")[1]
    # ⚠️ Здесь заглушка — сюда вставим реальные данные позже
    await callback.message.edit_text(f"🗺 Карта: <b>{map_name}</b>\n\n🔍 Ивенты: (будет реализовано)", parse_mode="HTML")

# ▶️ Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
