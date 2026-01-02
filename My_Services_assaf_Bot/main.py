import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from config import BOT_TOKEN, OWNER_ID
from data.bots_manager import create_bot, list_bots

logging.basicConfig(level=logging.INFO)

# ========== /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🫟 صانع بوت", callback_data="factory")],
        [InlineKeyboardButton("🎛 المتحكم", callback_data="controller")],
        [InlineKeyboardButton("➕ إضافة", callback_data="add")],
        [InlineKeyboardButton("✏️ تعديل", callback_data="edit")],
        [InlineKeyboardButton("🗑 حذف", callback_data="delete")]
    ]
    await update.message.reply_text(
        "🫟 أهلاً بك في بوت خدمات عساف\n\nاختر من الأزرار:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== الأزرار ==========
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # ===== صانع بوت =====
    if query.data == "factory":
        keyboard = [
            [InlineKeyboardButton("➕ إنشاء بوت جديد", callback_data="new_bot")],
            [InlineKeyboardButton("📋 قائمة بوتاتك", callback_data="my_bots")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
        ]
        await query.edit_message_text(
            "🏭 صانع البوتات\nاختر عملية:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ===== قائمة البوتات =====
    elif query.data == "my_bots":
        bots = list_bots()
        if not bots:
            await query.edit_message_text("❌ لا يوجد بوتات بعد")
            return

        text = "🤖 **بوتاتك:**\n\n"
        for i, (bot_id, name) in enumerate(bots.items(), 1):
            text += f"{i}. {name}\n🆔 `{bot_id}`\n\n"

        await query.edit_message_text(text, parse_mode="Markdown")

    # ===== إنشاء بوت جديد (مبدئي) =====
    elif query.data == "new_bot":
        await query.edit_message_text(
            "➕ إنشاء بوت جديد\n\n"
            "✳️ أرسل اسم البوت الآن.\n"
            "（المرحلة القادمة سنضيف الإدخال التفاعلي）"
        )

    # ===== رجوع =====
    elif query.data == "back":
        await start(query, context)

    # ===== باقي الأزرار =====
    else:
        await query.edit_message_text(
            f"⚙️ الخيار ({query.data}) قيد التطوير"
        )

# ========== التشغيل ==========
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("🤖 My_Services_assaf_Bot يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()

