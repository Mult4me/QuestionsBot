import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()  # Загрузка переменных из .env

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # исправлено имя переменной

QA_DATABASE = {
    "Что такое Telegram?": "Telegram — это мессенджер с поддержкой ботов.",
    "Кто создал Telegram?": "Telegram был создан Павлом Дуровым."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(text=question, callback_data=question)]
        for question in QA_DATABASE
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите вопрос:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    answer = QA_DATABASE.get(query.data, "Ответ не найден.")
    await query.edit_message_text(text=answer)

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
