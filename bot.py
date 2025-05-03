# bot.py

import pandas as pd
from data import category_links, TOKEN 

from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters, CallbackQueryHandler
)
from datetime import datetime

# Состояния
CONFIRM, QUESTION1, QUESTION2, QUESTION3 = range(4)

responses = []

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋\n\n"
        "🟢 /link – Получить ссылку на онлайн консультацию\n"
        "🔵 /info – Посмотреть информацию о психологах в Московском банке"
    )

# /link
async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["✅ Продолжить", "❌ Отмена"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "ℹ️ Перед началом опроса:\n\n"
        "Убедитесь, что вы записались на консультацию через *ПУЛЬС*.\n"
        "Если не записаться через Пульс, ссылка будет неактивной."
        "По результату вы получите ссылку.\n\n",
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
            "Если хотите пройти опрос сначала – используйте /link",
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
    context.user_data["time"] = update.message.text
    username = update.effective_user.username or "Без ника"
    user_id = update.effective_user.id
    category = context.user_data["category"]
    age = context.user_data["age"]
    time = context.user_data["time"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Удалить старую запись
    responses[:] = [r for r in responses if r["user_id"] != user_id]

    responses.append({
        "user_id": user_id,
        "username": username,
        "category": category,
        "age": age,
        "time": time,
        "date": date
    })

    link = category_links.get(category)
    await update.message.reply_text(f"✅ Спасибо! Ваша ссылка: {link}")
    return ConversationHandler.END

# /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ℹ️ Психологи Московского банка", callback_data="info_about")],
        [InlineKeyboardButton("📝 Как записаться на консультацию", callback_data="info_how")],
        [InlineKeyboardButton("📍 Адреса кабинетов", callback_data="info_terms")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📘 Выберите интересующий раздел:", reply_markup=reply_markup)

# Обработчик кнопок в меню информации
async def info_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()


    # Задаём дефолтное сообщение для обработки несуществующих значений
    text = "ℹ️ Ошибка. Неизвестный запрос."

    # В зависимости от нажатой кнопки показываем нужную информацию
    if query.data == "info_about":
        text = "ℹ️ *Психологи*\n\nЗдесь ты можешь узнать всё о ..."
    elif query.data == "info_how":
        text = """📝 *Как записаться на консультацию:*
        1. В *Пульсе* зайдите раздел *Мое здоровье*
        2. Выберите психологическая поддержка - *записаться очно*
        3. Далее измените адрес 
        4. Запишитесь на понравившеюся дату и время
        """
    elif query.data == "info_terms":
        text = """📍 *Адреса кабинетов*
        - Старокачаловская д.10, м. Бульвар Д. Донского
        - Андроньевская д.6, м. Таганская
        - Расплетина д.1, м.
        """

    # Кнопка "Назад", чтобы вернуться в главное меню
    elif query.data == "info_back":
        text = "📘 Выберите интересующий раздел:"
        # Мы возвращаемся в главное меню с двумя основными кнопками
        keyboard = [
            [InlineKeyboardButton("Психологи", callback_data="info_about")],
            [InlineKeyboardButton("Как записаться на консультацию", callback_data="info_how")],
            [InlineKeyboardButton("Адреса кабинетов", callback_data="info_terms")]
        ]
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Кнопка назад для возвращения в меню информации
    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="info_back")]
    ]
    await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
# Обработчик для кнопки "Назад"
async def info_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Главное меню информации
    keyboard = [
        [InlineKeyboardButton("ℹ️ Психологи Московского банка", callback_data="info_about")],
        [InlineKeyboardButton("📝 Как записаться на консультацию", callback_data="info_how")],
        [InlineKeyboardButton("📍 Адреса кабинетов", callback_data="info_terms")]
    ]
    await query.edit_message_text("📘 Выберите интересующий раздел:", reply_markup=InlineKeyboardMarkup(keyboard))

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
    app = ApplicationBuilder().token(TOKEN).build()

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
    app.add_handler(CallbackQueryHandler(info_buttons))
    app.add_handler(CallbackQueryHandler(info_back, pattern="info_back"))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(conv_handler)

    print("🤖 Бот запущен...")
    app.run_polling()
