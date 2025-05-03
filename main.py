import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
from qa_data import QA_DATABASE

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

user_context = {}  # Для хранения выбранной категории для каждого пользователя

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat:{cat}")]
                for cat in QA_DATABASE.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("cat:"):
        category = data[4:]
        user_context[query.from_user.id] = category
        questions = list(QA_DATABASE[category].keys())
        keyboard = [[InlineKeyboardButton(q[:50], callback_data=f"q:{q}")]
                    for q in questions]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите вопрос:", reply_markup=reply_markup)
    elif data.startswith("q:"):
        question = data[2:]
        category = user_context.get(query.from_user.id, "Все вопросы")
        answer = QA_DATABASE.get(category, {}).get(question) or next(
            (v for cat in QA_DATABASE.values() for k, v in cat.items() if k == question),
            "Ответ не найден."
        )
        await query.edit_message_text(text=f"<b>{question}</b>\n\n{answer}", parse_mode="HTML")

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
