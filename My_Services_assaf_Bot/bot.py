#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================== الإعدادات ==================
BOT_TOKEN = "8290175126:AAFg_SymBuI1Qyn1Zl3ep3Tv2ldy0mHiP60"

CHANNELS = {
    "INSTAGRAM": -1002954264634,
    "FACEBOOK":  -1003552371492,
    "SAFEUM":    -1003341840224,
}

SIGNATURE = "【｡_｡  𝐀𝐛𝐨 𝐍𝐚𝐲𝐚   𝟎𝟗𝟗𝟐  𝟒𝟒𝟑  𝟓𝟓𝟒 ｡_｡】"

# ================== الحالة ==================
USER_STATE = {}  # chat_id -> {"active": bool, "channel": str}

logging.basicConfig(level=logging.INFO)

# ================== أدوات ==================
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
LONG_ID_RE = re.compile(r"\b\d{13,}\b")

# ================== الواجهات ==================
def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("▶️ تشغيل", callback_data="START"),
            InlineKeyboardButton("⏹ إيقاف", callback_data="STOP"),
        ]
    ])

def channel_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 Instagram", callback_data="INSTAGRAM"),
            InlineKeyboardButton("🟢 Facebook", callback_data="FACEBOOK"),
            InlineKeyboardButton("🟢 SAFEUM", callback_data="SAFEUM"),
        ]
    ])

# ================== الأوامر ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك 👋\nتحكم في البوت من الأزرار:",
        reply_markup=main_keyboard()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "START":
        USER_STATE[chat_id] = {"active": True, "channel": None}
        await query.edit_message_text(
            "تم تشغيل البوت ✅\nاختر القناة:",
            reply_markup=channel_keyboard()
        )

    elif query.data == "STOP":
        USER_STATE[chat_id] = {"active": False, "channel": None}
        await query.edit_message_text(
            "تم إيقاف البوت ⛔",
            reply_markup=main_keyboard()
        )

    elif query.data in CHANNELS:
        USER_STATE.setdefault(chat_id, {})["channel"] = query.data
        await query.edit_message_text(
            f"📌 تم اختيار {query.data}\nأرسل النص أو ملف txt الآن",
            reply_markup=main_keyboard()
        )

# ================== المعالجة ==================
def parse_instagram(text):
    email = EMAIL_RE.search(text)
    user = re.search(r"يوز.*?:\s*(\w+)", text)
    return user.group(1) if user else "", email.group(0) if email else ""

def parse_facebook(text):
    email = EMAIL_RE.search(text)
    if email:
        return email.group(0)
    id_ = LONG_ID_RE.search(text)
    return id_.group(0) if id_ else ""

def parse_safeum(text):
    m = re.search(r":\s*([A-Za-z0-9]{6,})", text)
    if m:
        return m.group(1)
    m2 = re.search(r"USERNAME\s*:\s*([A-Za-z0-9]{6,})", text, re.I)
    return m2.group(1) if m2 else ""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    state = USER_STATE.get(chat_id)

    if not state or not state.get("active"):
        await update.message.reply_text("⛔ البوت متوقف", reply_markup=main_keyboard())
        return

    channel = state.get("channel")
    if not channel:
        await update.message.reply_text("اختر القناة أولًا", reply_markup=channel_keyboard())
        return

    text = update.message.text or ""
    out = ""

    if channel == "INSTAGRAM":
        user, email = parse_instagram(text)
        out = f"""【｡_｡𝐍𝐞𝐰 𝐇𝐢𝐭 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 𝐀𝐜𝐜𝐨𝐮𝐧𝐭｡_｡】
【𝐮𝐬𝐞𝐫  :   {user}
【𝐆𝐦𝐚𝐢𝐥 : {email}
【𝐔𝐑𝐋  :
{SIGNATURE}"""

    elif channel == "FACEBOOK":
        val = parse_facebook(text)
        out = f"""【｡_｡𝐍𝐞𝐰 𝐇𝐢𝐭  𝐅𝐚𝐜𝐞  𝐈𝐃  𝐀𝐜𝐜𝐨𝐮𝐧𝐭｡_｡】
【 𝐈𝐃   : {val}
【𝐔𝐑𝐋  :
{SIGNATURE}"""

    elif channel == "SAFEUM":
        user = parse_safeum(text)
        out = f"""【｡_｡𝐍𝐞𝐰 𝐇𝐢𝐭 𝐒𝐀𝐅𝐄𝐔𝐌 𝐀𝐜𝐜𝐨𝐮𝐧𝐭｡_｡】
【𝐮𝐬𝐞𝐫    : {user}
【𝐰𝐡𝐚𝐭𝐬   :
{SIGNATURE}"""

    await context.bot.send_message(CHANNELS[channel], out)
    await update.message.reply_text("✅ تم الإرسال")

# ================== التشغيل ==================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

