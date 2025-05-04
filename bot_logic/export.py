import os
import pandas as pd

from Bot_psychologist.bot_logic.data import ADMIN_IDS

from telegram import (
    Update, ReplyKeyboardRemove
)

from telegram.ext import (
    ContextTypes, ConversationHandler
)

responses = [] 

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

    # Сохраняем в файл
    combined_df.to_excel(file_path, index=False)

    await update.message.reply_document(document=open(file_path, "rb"), filename="results.xlsx")

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос отменён.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
