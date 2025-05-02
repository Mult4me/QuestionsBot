import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Конфигурация бота
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# База вопросов и ответов
QA_DATABASE = {
    "Что такое тест-кейс?": "Тест-кейс — это документ, описывающий совокупность шагов, конкретных условий и параметров, необходимых для проверки реализации тестируемой функции.",
    "Что такое баг-репорт?": "Баг-репорт — это документ, описывающий ситуацию или последовательность действий, приведшую к некорректной работе объекта тестирования.",
    "Что такое регрессионное тестирование?": "Регрессионное тестирование — это вид тестирования, направленный на проверку изменений, внесённых в приложение или окружающую среду.",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    keyboard = [[InlineKeyboardButton("Начать тест", callback_data="start_test")]]
    await update.message.reply_text(
        "Добро пожаловать в бота для изучения тестирования!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_test":
        # Начинаем тест с первого вопроса
        question = list(QA_DATABASE.keys())[0]
        context.user_data['current_index'] = 0
        
        buttons = [
            [InlineKeyboardButton("Показать ответ", callback_data="show_answer")],
            [InlineKeyboardButton("Следующий вопрос", callback_data="next_question")]
        ]
        await query.edit_message_text(
            text=f"Вопрос:\n{question}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif query.data == "show_answer":
        # Показываем ответ на текущий вопрос
        index = context.user_data['current_index']
        question = list(QA_DATABASE.keys())[index]
        answer = QA_DATABASE[question]
        
        buttons = [[InlineKeyboardButton("Следующий вопрос", callback_data="next_question")]]
        await query.edit_message_text(
            text=f"Вопрос:\n{question}\n\nОтвет:\n{answer}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif query.data == "next_question":
        # Переходим к следующему вопросу
        current_index = context.user_data['current_index']
        next_index = (current_index + 1) % len(QA_DATABASE)
        question = list(QA_DATABASE.keys())[next_index]
        context.user_data['current_index'] = next_index
        
        buttons = [
            [InlineKeyboardButton("Показать ответ", callback_data="show_answer")],
            [InlineKeyboardButton("Следующий вопрос", callback_data="next_question")]
        ]
        await query.edit_message_text(
            text=f"Вопрос:\n{question}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

def main() -> None:
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    
    # Запуск бота в режиме polling
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()