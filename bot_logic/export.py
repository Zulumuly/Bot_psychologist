import os
import pandas as pd

from bot_logic.data import ADMIN_IDS

from telegram import (
    Update, ReplyKeyboardRemove
)

from openpyxl.utils import get_column_letter

from telegram.ext import (
    ContextTypes, ConversationHandler
)

from .links import responses

# /export (только для ADMIN_IDS)
async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет доступа к экспорту.")
        return

    if not responses:
        await update.message.reply_text("📭 Пока нет данных для экспорта.")
        return

    file_path = "export.xlsx"

    # Проверка: если файл уже существует – загружаем, иначе создаем
    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path)
        new_df = pd.DataFrame(responses)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = pd.DataFrame(responses)


    combined_df = combined_df.rename(columns={
        "username": "Никнейм",
        "category": "Психолог",
        "age": "Дата консультации",
        "time": "Время консультации",
        "date": "Дата заполнения"
    })

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        combined_df.to_excel(writer, index=False, sheet_name="Ответы")
        worksheet = writer.sheets["Ответы"]

    # Автоматическая ширина столбцов — ВНУТРИ блока writer
    for col_num, column in enumerate(combined_df.columns, 1):
        if combined_df[column].empty:
            max_length = len(column) + 2
        else:
            max_length = max(
                combined_df[column].astype(str).map(len).max(),
                len(column)
            ) + 2
        col_letter = get_column_letter(col_num)
        worksheet.column_dimensions[col_letter].width = max_length


    await update.message.reply_document(document=open(file_path, "rb"), filename="results.xlsx")

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос отменён.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
