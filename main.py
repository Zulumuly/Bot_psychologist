from bot_logic.export import (
    export, cancel
)

from bot_logic.info import (
    info, info_buttons, info_back
)

from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters,
    CallbackQueryHandler
)

from bot_logic.links import (
    start, link, confirm, question1, question2, question3,
    CONFIRM, QUESTION1, QUESTION2, QUESTION3
)

from bot_logic.data import TOKEN
from keep_alive import keep_alive

keep_alive()


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
