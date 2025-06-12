import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]
ALLOWED_USERS = config["allowed_users"]
EVENTS_DATA = config["events"]  # эмуляция базы

MAPS = [
    "Crashlands", "Sunset Mall", "Cascade Swamps", "Ironclad Industries", "Tech Junkyard",
    "Glitchwood Grove", "The Underbelly", "Forgotten Docks", "Scorched Summit",
    "Moonlight Temple", "Sporewood", "Eclipsed Highlands", "Ashen Wastes"
]

EVENT_TYPES = ["Overcharged", "Boss", "Rift", "Escort", "Dojo", "Wave"]

user_filters = {}  # user_id: [selected_types]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    keyboard = [[InlineKeyboardButton(m, callback_data=f"map:{m}")] for m in MAPS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери карту:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("map:"):
        map_name = data.split(":")[1]
        keyboard = [
            [InlineKeyboardButton(f"{'✅' if t in user_filters.get(query.from_user.id, EVENT_TYPES) else '☐'} {t}", callback_data=f"filter:{map_name}:{t}")]
            for t in EVENT_TYPES
        ]
        keyboard.append([InlineKeyboardButton("✅ Показать события", callback_data=f"show:{map_name}")])
        await query.edit_message_text(f"Выбранная карта: {map_name}
Выбери фильтры:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("filter:"):
        _, map_name, event_type = data.split(":")
        uid = query.from_user.id
        user_filters.setdefault(uid, list(EVENT_TYPES))
        if event_type in user_filters[uid]:
            user_filters[uid].remove(event_type)
        else:
            user_filters[uid].append(event_type)
        keyboard = [
            [InlineKeyboardButton(f"{'✅' if t in user_filters[uid] else '☐'} {t}", callback_data=f"filter:{map_name}:{t}")]
            for t in EVENT_TYPES
        ]
        keyboard.append([InlineKeyboardButton("✅ Показать события", callback_data=f"show:{map_name}")])
        await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))

    elif data.startswith("show:"):
        map_name = data.split(":")[1]
        uid = query.from_user.id
        filters = user_filters.get(uid, EVENT_TYPES)
        matched = [e for e in EVENTS_DATA if e["map"] == map_name and e["type"] in filters]
        if not matched:
            await query.edit_message_text("Нет активных событий на этой карте по заданным фильтрам.")
            return
        msg = f"🎯 События на карте: {map_name}

"
        for e in matched:
            msg += f"• {e['type']} – {e['status']} ({e['reported']})
"
        await query.edit_message_text(msg)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("events", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
