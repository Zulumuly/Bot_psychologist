import pandas as pd
from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
from datetime import datetime

# Состояния
CONFIRM, QUESTION1, QUESTION2, QUESTION3 = range(4)

# Права на экспорт
ADMIN_IDS = [1040503223]  # user id можно посмотреть в боте userinfobot

# Ответы и ссылки
category_links = {
    "Татьяна Костина": "https://example.com/a",
    "Андрей Давыдов": "https://example.com/b",
    "Анна Кречетова": "https://example.com/c"
}

responses = []

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋\n\n"
        "🟢 /link – Получить ссылку\n"
        "🔵 /info – Посмотреть информацию"
    )

# /link
async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["✅ Продолжить", "❌ Отмена"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "ℹ️ Перед началом опроса:\n\n"
        "Убедитесь, что вы записались на консультацию через ПУЛЬС.\n"
        "По результату вы получите ссылку.\n\n"
        "Если всё понятно, нажмите 'Продолжить'.",
        reply_markup=markup
    )
    return CONFIRM

# Подтверждение
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "✅ Продолжить":
        keyboard = [["Татьяна Костина"], ["Андрей Давыдов"], ["Анна Кречетова"], ["Моего варианта нет"]]
        await update.message.reply_text("Вопрос 1: Выберите к какому психологу вы записались?:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return QUESTION1
    else:
        await update.message.reply_text("Опрос отменён.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

# Вопрос 1
async def question1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "Моего варианта нет":
        await update.message.reply_text(
            "❌ Вы записались к психологу, который не проводит онлайн консультации.\n\n"
            "Если хотите начать сначала – используйте /link",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    elif choice not in category_links:
        await update.message.reply_text("❗ Пожалуйста, выберите вариант из списка.")
        return QUESTION1

    context.user_data["category"] = choice
    await update.message.reply_text("Вопрос 2: На какую дату вы записались?", reply_markup=ReplyKeyboardRemove())
    return QUESTION2

# Вопрос 2
async def question2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    await update.message.reply_text("Вопрос 3: На какое время?")
    return QUESTION3

# Вопрос 3 и завершение
async def question3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text
    username = update.effective_user.username or "Без ника"
    user_id = update.effective_user.id
    category = context.user_data["category"]
    age = context.user_data["age"]
    city = context.user_data["city"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Удалить старую запись
    responses[:] = [r for r in responses if r["user_id"] != user_id]

    responses.append({
        "user_id": user_id,
        "username": username,
        "category": category,
        "age": age,
        "city": city,
        "date": date
    })

    link = category_links.get(category)
    await update.message.reply_text(f"✅ Спасибо! Ваша ссылка: {link}")
    return ConversationHandler.END

# /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    entry = next((r for r in responses if r["user_id"] == user_id), None)
    if entry:
        await update.message.reply_text(
            f"🧾 Информация:\n"
            f"Ник: @{entry['username']}\n"
            f"Категория: {entry['category']}\n"
            f"Возраст: {entry['age']}\n"
            f"Город: {entry['city']}\n"
            f"Дата: {entry['date']}"
        )
    else:
        await update.message.reply_text("ℹ️ Вы ещё не проходили опрос. Используйте /link")

# /export (только для ADMIN_IDS)
async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет доступа к экспорту.")
        return

    if not responses:
        await update.message.reply_text("📭 Пока нет данных для экспорта.")
        return

    df = pd.DataFrame(responses)
    df.to_excel("export.xlsx", index=False)

    await update.message.reply_document(document=open("export.xlsx", "rb"), filename="results.xlsx")

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос отменён.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token("8141969487:AAHbQVPhetHuw_o3aSSvkfO8jwu6gbfgI8Q").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("link", link)],
        states={
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
            QUESTION1: [MessageHandler(filters.TEXT & ~filters.COMMAND, question1)],
            QUESTION2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question2)],
            QUESTION3: [MessageHandler(filters.TEXT & ~filters.COMMAND, question3)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(conv_handler)

    print("🤖 Бот запущен...")
    app.run_polling()
