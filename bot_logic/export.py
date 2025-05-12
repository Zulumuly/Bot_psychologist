import os
import pandas as pd

from bot_logic.data import ADMIN_IDS

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from openpyxl.utils import get_column_letter

from .links import responses

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет доступа к экспорту.")
        return

    if not responses:
        await update.message.reply_text("📭 Пока нет новых данных для экспорта.")
        return

    # Фильтруем только корректные записи
    required_keys = ["username", "category", "age", "time", "date"]
    filtered_responses = [r for r in responses if all(k in r for k in required_keys)]

    if len(filtered_responses) < len(responses):
        await update.message.reply_text("⚠️ Некоторые записи были пропущены из-за отсутствия нужных полей.")

    if not filtered_responses:
        await update.message.reply_text("❌ Нет корректных данных для экспорта.")
        return

    file_path = "export.xlsx"

    # Создаём DataFrame
    new_df = pd.DataFrame(filtered_responses)

    # Переименование столбцов
    new_df = new_df.rename(columns={
        "username": "Никнейм",
        "category": "Психолог",
        "age": "Дата консультации",
        "time": "Время консультации",
        "date": "Дата заполнения"
    })

    # Объединяем с уже существующим, если есть
    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    # Удаляем дубликаты
    combined_df.drop_duplicates(
        subset=["Никнейм", "Психолог", "Дата консультации", "Время консультации", "Дата заполнения"],
        inplace=True
    )

    # Сохраняем файл с автошириной
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        combined_df.to_excel(writer, index=False, sheet_name="Ответы")
        worksheet = writer.sheets["Ответы"]

        for col_num, column in enumerate(combined_df.columns, 1):
            series = combined_df[column]
            max_length = max(series.astype(str).apply(len).max(), len(str(column))) + 2
            col_letter = get_column_letter(col_num)
            worksheet.column_dimensions[col_letter].width = max_length

    await update.message.reply_document(document=open(file_path, "rb"), filename="results.xlsx")


# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос отменён.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
