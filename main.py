import os
import hashlib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
from qa_data import QA_DATABASE

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

user_context = {}  # Хранит: {user_id: {category, index, show_answer}}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat:{cat}")]
                for cat in QA_DATABASE.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("cat:"):
        category = data[4:]
        user_context[user_id] = {"category": category, "index": 0, "show_answer": False}
        await show_question(query, user_id)
        return

    if user_id not in user_context:
        await query.edit_message_text("Сначала выберите категорию. /start")
        return

    action = data
    if action == "next":
        user_context[user_id]["index"] += 1
        user_context[user_id]["show_answer"] = False
    elif action == "prev":
        user_context[user_id]["index"] = max(0, user_context[user_id]["index"] - 1)
        user_context[user_id]["show_answer"] = False
    elif action == "show_answer":
        user_context[user_id]["show_answer"] = True
    elif action == "back_to_cat":
        await start(query, context)
        return

    await show_question(query, user_id)

async def show_question(query, user_id):
    context_data = user_context[user_id]
    category = context_data["category"]
    index = context_data["index"]
    show_answer = context_data["show_answer"]

    questions = list(QA_DATABASE[category].items())
    total = len(questions)

    if index >= total:
        index = total - 1
        user_context[user_id]["index"] = index

    question, answer = questions[index]
    text = f"<b>{question}</b>"
    if show_answer:
        text += f"\n\n{answer}"

    keyboard = [
        [
            InlineKeyboardButton("⬅️ Предыдущий", callback_data="prev"),
            InlineKeyboardButton("Показать ответ" if not show_answer else "Ответ показан", callback_data="show_answer"),
            InlineKeyboardButton("Следующий ➡️", callback_data="next")
        ],
        [InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_to_cat")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="HTML")

def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    if os.getenv('PELLA_MODE', 'false').lower() == 'true':
        port = int(os.getenv('PORT', 8080))
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=os.getenv('WEBHOOK_URL'),
            secret_token='YOUR_SECRET_TOKEN'
        )
    else:
        app.run_polling()

if __name__ == '__main__':
    run_bot()
