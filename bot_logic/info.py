import pandas as pd

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)

from telegram.ext import (
    ContextTypes
)

# /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        #[InlineKeyboardButton("ℹ️ Психологи Московского банка", callback_data="info_about")],
        [InlineKeyboardButton("📝 Как записаться на онлайн консультацию", callback_data="info_how")],
        [InlineKeyboardButton("📍 Адреса кабинетов онлайн", callback_data="info_terms")]
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
    #if query.data == "info_about":
    #    text = "ℹ️ *Психологи*\n\nЗдесь ты можешь узнать всё о ..."
    if query.data == "info_how":
        text = """📝 *Как записаться на онлайн консультацию:*
        1. Зайдите в *Пульс* раздел *Мое здоровье* -> *психологическая поддержка* -> *записаться очно*
        2. Выберите нужный адрес
        3. Запишитесь на удобную дату и время
        """
    elif query.data == "info_terms":
        text = """📍 *Адреса кабинетов онлайн*
        - Давыдов Андрей ведет прием на *Старокачаловская д.10*
        - Кречетова Анна ведет прием на *Б. Андроньевская д.6*
        - Костина Татьяна ведет прием на *Расплетина д.1*
        """

    # Кнопка "Назад", чтобы вернуться в главное меню
    elif query.data == "info_back":
        text = "📘 Выберите интересующий раздел:"
        # Мы возвращаемся в главное меню с двумя основными кнопками
        keyboard = [
            #[InlineKeyboardButton("Психологи", callback_data="info_about")],
            [InlineKeyboardButton("Как записаться на консультацию", callback_data="info_how")],
            [InlineKeyboardButton("Адреса кабинетов онлайн", callback_data="info_terms")]
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
        #[InlineKeyboardButton("ℹ️ Психологи Московского банка", callback_data="info_about")],
        [InlineKeyboardButton("📝 Как записаться на консультацию", callback_data="info_how")],
        [InlineKeyboardButton("📍 Адреса кабинетов онлайн", callback_data="info_terms")]
    ]
    await query.edit_message_text("📘 Выберите интересующий раздел:", reply_markup=InlineKeyboardMarkup(keyboard))



