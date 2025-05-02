import pandas as pd
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

# Состояния
QUESTION1, QUESTION2, QUESTION3 = range(3)

# Хранилище
responses = []

# Главное меню
def main_menu():
    keyboard = [
        [KeyboardButton("📝 Ответить на вопросы")],
        [KeyboardButton("📄 Посмотреть информацию")],
        [KeyboardButton("📤 Экспорт Excel")],
        [KeyboardButton("❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для сбора информации.\nВыбери действие из меню:",
        reply_markup=main_menu()
    )
    return ConversationHandler.END

# Обработка меню
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📝 Ответить на вопросы":
        keyboard = [["Татьяна Костина"], ["Анна Кречетова"], ["Андрей Давыдов"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Вопрос 1: Выбери психолога:", reply_markup=reply_markup)
        return QUESTION1

    elif text == "📄 Посмотреть информацию":
        username = update.effective_user.username
        entry = next((r for r in responses if r["Username"] == username), None)
        if entry:
            await update.message.reply_text(
                f"👤 Категория: {entry['Category']}\n🎂 Возраст: {entry['Age']}\n🏙️ Город: {entry['City']}",
                reply_markup=main_menu()
            )
        else:
            await update.message.reply_text("❗ Вы ещё не заполняли анкету.", reply_markup=main_menu())
        return ConversationHandler.END

    elif text == "📤 Экспорт Excel":
        return await export(update, context)

    elif text == "❌ Отмена":
        await update.message.reply_text("Операция отменена.", reply_markup=main_menu())
        return ConversationHandler.END

    else:
        await update.message.reply_text("Пожалуйста, выбери действие из меню.")
        return ConversationHandler.END

# Обработка 1-го вопроса (выбор категории)
async def question1_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected = update.message.text
    context.user_data["category"] = selected
    await update.message.reply_text("Вопрос 2: На какую дату ты записался")
    return QUESTION2

# Вопрос 2
async def question2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    await update.message.reply_text("Вопрос 3: На какое время?")
    return QUESTION3

# Вопрос 3 + вывод ссылки
async def question3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text
    username = update.effective_user.username

    # Сохраняем
    responses[:] = [r for r in responses if r["Username"] != username]
    responses.append({
        "Username": username,
        "Category": context.user_data["category"],
        "Age": context.user_data["age"],
        "City": context.user_data["city"]
    })

    # Ссылка по категории
    links = {
        "🔵 Вариант A": "https://example.com/a",
        "🟢 Вариант B": "https://example.com/b",
        "🔴 Вариант C": "https://example.com/c"
    }
    link = links.get(context.user_data["category"], "https://example.com/default")

    await update.message.reply_text(
        f"✅ Спасибо за ответы!\n🔗 Вот твоя ссылка: {link}",
        reply_markup=main_menu()
    )
    return ConversationHandler.END

# Экспорт в Excel
async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not responses:
        await update.message.reply_text("Нет данных для экспорта.", reply_markup=main_menu())
        return ConversationHandler.END

    df = pd.DataFrame(responses)
    path = "responses.xlsx"
    df.to_excel(path, index=False)

    await update.message.reply_document(document=open(path, "rb"), caption="📥 Данные в Excel.", reply_markup=main_menu())
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.", reply_markup=main_menu())
    return ConversationHandler.END

# Запуск
if __name__ == '__main__':
    app = ApplicationBuilder().token("8141969487:AAHbQVPhetHuw_o3aSSvkfO8jwu6gbfgI8Q").build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
        states={
            QUESTION1: [MessageHandler(filters.TEXT & ~filters.COMMAND, question1_choice)],
            QUESTION2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question2)],
            QUESTION3: [MessageHandler(filters.TEXT & ~filters.COMMAND, question3)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("✅ Бот запущен.")
    app.run_polling()
