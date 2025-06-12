import logging
import asyncio
import aiohttp
import re

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import hbold

TELEGRAM_TOKEN = "7736390099:AAHIDSncyfAPCx85XWB-4mxSw6dZCWhZdX0"

# Реальные карты
MAPS = [
    "Shrine Village", "Overgrown Ruins", "Infested Forest", "Cave Of Spirits", "Castle Walls",
    "Summoning Grounds", "Sewers", "Corrupted Village", "Corrupted Ruins", "Corrupted Forest",
    "Corrupted Cave", "Corrupted Castle", "Corrupted Shrine"
]

EVENT_TYPES = ["Overcharged", "Boss", "Rift", "Escort", "Dojo"]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

user_state = {}

@dp.message(commands=["start", "events"])
async def show_maps(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for map_name in MAPS:
        keyboard.add(InlineKeyboardButton(text=map_name, callback_data=f"map_{map_name}"))
    await message.answer("Выбери карту:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("map_"))
async def select_map(callback: types.CallbackQuery):
    map_name = callback.data[4:]
    user_state[callback.from_user.id] = {"map": map_name}
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    for event in EVENT_TYPES:
        keyboard.add(InlineKeyboardButton(text=event, callback_data=f"event_{event}"))
    await callback.message.edit_text(f"Карта: {map_name}\nВыбери тип ивента:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("event_"))
async def select_event(callback: types.CallbackQuery):
    event_type = callback.data[6:]
    user_id = callback.from_user.id
    selected_map = user_state.get(user_id, {}).get("map", "Unknown")

    await callback.message.edit_text(f"{hbold('Поиск событий...')}\nКарта: {selected_map}\nТип: {event_type}")
    
    events = await fetch_reddit_events(selected_map, event_type)
    if events:
        text = f"<b>Найдено {len(events)} событий:</b>\n\n" + "\n\n".join(events)
    else:
        text = "Нет подходящих событий на Reddit."
    await bot.send_message(chat_id=user_id, text=text)

async def fetch_reddit_events(map_name: str, event_type: str):
    url = "https://www.reddit.com/r/joinmoco/new.json?limit=20"
    headers = {"User-Agent": "moco-event-bot/0.1"}
    events = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                for post in data["data"]["children"]:
                    title = post["data"]["title"]
                    if re.search(rf"{map_name}.*{event_type}", title, re.IGNORECASE):
                        permalink = post["data"]["permalink"]
                        full_link = f"https://reddit.com{permalink}"
                        events.append(f"<a href='{full_link}'>{title}</a>")
    except Exception as e:
        logging.error(f"Ошибка парсинга Reddit: {e}")
    return events

if __name__ == "__main__":
    import asyncio
    from aiogram import Router
    router = Router()
    router.include_router(dp)
    asyncio.run(dp.start_polling(bot))
