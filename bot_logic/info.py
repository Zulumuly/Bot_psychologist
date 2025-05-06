import pandas as pd

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)

from telegram.ext import (
    ContextTypes
)

from .text import TEXT_ADRESS, TEXT_FOR_FIRST_Q, TEXT_CONTACT, TEXT_CALL

# /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Как записаться на онлайн консультацию", callback_data="info_how")],
        [InlineKeyboardButton("📍 Адреса кабинетов онлайн", callback_data="info_terms")],
        [InlineKeyboardButton("📶 Как подключиться к встрече", callback_data="info_call")],
        [InlineKeyboardButton("ℹ️ Контакты", callback_data="info_about")]
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
    if query.data == "info_how":
        text = TEXT_FOR_FIRST_Q
    elif query.data == "info_terms":
        text = TEXT_ADRESS
    elif query.data == "info_call":
        text = TEXT_CALL
    elif query.data == "info_about":
        text = TEXT_CONTACT

    # Кнопка "Назад", чтобы вернуться в главное меню
    elif query.data == "info_back":
        text = "📘 Выберите интересующий раздел:"
        # Мы возвращаемся в главное меню с основными кнопками
        keyboard = [
            [InlineKeyboardButton("📝 Как записаться на консультацию", callback_data="info_how")],
            [InlineKeyboardButton("📍 Адреса кабинетов онлайн", callback_data="info_terms")],
            [InlineKeyboardButton("📶 Как подключиться к встрече", callback_data="info_call")],
            [InlineKeyboardButton("ℹ️ Контакты", callback_data="info_about")]
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
        [InlineKeyboardButton("📝 Как записаться на консультацию", callback_data="info_how")],
        [InlineKeyboardButton("📍 Адреса кабинетов онлайн", callback_data="info_terms")],
        [InlineKeyboardButton("📶 Как подключиться к встрече", callback_data="info_call")],
        [InlineKeyboardButton("ℹ️ Контакты", callback_data="info_about")]
    ]
    await query.edit_message_text("📘 Выберите интересующий раздел:", reply_markup=InlineKeyboardMarkup(keyboard))



