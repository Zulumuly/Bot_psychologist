from telegram.ext import (
    ContextTypes, ConversationHandler
)

from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
)

from .data import category_links
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
        "ℹ️ Важно!\n\n"
        "Для участия в опросе запишитесь на консультацию через «ПУЛЬС», только тогда ссылка будет активной.\n",
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
            "❌ Вы записались к психологу, который не проводит онлайн консультации.\n\n",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    elif choice not in category_links:
        await update.message.reply_text("❗ Пожалуйста, выберите вариант из списка.")
        return QUESTION1


    context.user_data["category"] = choice
    await update.message.reply_text(
        "Вопрос 2: На какую дату вы записались?\n\n"
        "_Введите дату в формате ДД.ММ.ГГГГ (например, 12.05.2025)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return QUESTION2

# Вопрос 2
async def question2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Проверка формата даты
    try:
        parsed_date = datetime.strptime(text, "%d.%m.%Y")
        context.user_data["age"] = parsed_date.strftime("%d.%m.%Y")
    except ValueError:
        await update.message.reply_text(
            "❗ Неверный формат даты. Введите дату в формате *ДД.ММ.ГГГГ* (например, 12.05.2025).",
            parse_mode="Markdown"
        )
        return QUESTION2
    
    # Кнопки с вариантами времени
    keyboard = [
        ["11:00", "12:00", "13:00", "14:00"],
        ["16:00", "17:00", "18:00", "19:00"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text("Вопрос 3: На какое время?", reply_markup=markup)
    return QUESTION3

# Вопрос 3 и завершение
async def question3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["time"] = update.message.text
    username = update.effective_user.username or "Без ника"
    category = context.user_data["category"]
    age = context.user_data["age"]
    time = context.user_data["time"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    responses.append({
        "username": username,
        "category": category,
        "age": age,
        "time": time,
        "date": date
    })

    link = category_links.get(category)
    await update.message.reply_text(f"✅ Спасибо! Ваша ссылка на онлайн консультацию: {link}")
    return ConversationHandler.END