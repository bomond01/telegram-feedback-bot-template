import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [494860919, 818906596]

CATEGORY_KEYBOARD = [
    [InlineKeyboardButton("💡 Предложение", callback_data="category_Предложение")],
    [InlineKeyboardButton("🚨 Жалоба", callback_data="category_Жалоба")],
    [InlineKeyboardButton("❓ Вопрос", callback_data="category_Вопрос")],
]

user_categories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Выберите категорию обращения:",
        reply_markup=InlineKeyboardMarkup(CATEGORY_KEYBOARD)
    )

async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.split("_", 1)[1]
    user_categories[query.from_user.id] = category
    await query.edit_message_text(f"✅ Категория выбрана: {category}\nТеперь отправьте ваше сообщение, фото или файл.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    category = user_categories.get(user_id, "Без категории")

    for admin_id in ADMIN_IDS:
        if update.message.text:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📬 Новое сообщение\nКатегория: {category}\nОт пользователя @{update.effective_user.username or user_id}:\n\n{update.message.text}"
            )
        if update.message.photo:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=update.message.photo[-1].file_id,
                caption=f"📷 Фото от @{update.effective_user.username or user_id}\nКатегория: {category}"
            )
        if update.message.video:
            await context.bot.send_video(
                chat_id=admin_id,
                video=update.message.video.file_id,
                caption=f"🎥 Видео от @{update.effective_user.username or user_id}\nКатегория: {category}"
            )
        if update.message.document:
            await context.bot.send_document(
                chat_id=admin_id,
                document=update.message.document.file_id,
                caption=f"📎 Файл от @{update.effective_user.username or user_id}\nКатегория: {category}"
            )

    await update.message.reply_text("✅ Спасибо! Ваше сообщение отправлено администраторам.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_category, pattern="^category_"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()