import telebot
from telebot import types
from datetime import datetime
import sqlite3

TOKEN = "7752525254:AAFuFL7Ydzgpdn-NYX1PluJT3lN-iACfn2g"
bot = telebot.TeleBot(TOKEN)

CHANNELS = {
    "ua": "-1003477192024",
    "az": "-1003645851278",
    "sold": "-1003674727163"
}

def init_db():
    conn = sqlite3.connect('anoshty.db')
    cursor = conn.cursor()
    # أضفنا عمود status لمعرفة حالة الحساب (متاح/مبيوع)
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts 
                      (number TEXT PRIMARY KEY, channel_id TEXT, message_id INTEGER, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

def save_msg(number, channel_id, message_id, status="available"):
    conn = sqlite3.connect('anoshty.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO accounts VALUES (?, ?, ?, ?)", (number, channel_id, message_id, status))
    conn.commit()
    conn.close()

def get_status(number):
    conn = sqlite3.connect('anoshty.db')
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id, status FROM accounts WHERE number=?", (number,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_and_delete_msg(number):
    conn = sqlite3.connect('anoshty.db')
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id, message_id FROM accounts WHERE number=? AND status='available'", (number,))
    result = cursor.fetchone()
    if result:
        try:
            bot.delete_message(result[0], result[1])
            cursor.execute("DELETE FROM accounts WHERE number=?", (number,))
            conn.commit()
        except: pass
    conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("إضافة حساب جديد ➕", "مبيوع 💰")
    markup.add("استعلام عن رقم 🔍")
    bot.send_message(message.chat.id, "مرحباً Assaf، اختر العملية:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "استعلام عن رقم 🔍")
def ask_info(message):
    msg = bot.send_message(message.chat.id, "أرسل الرقم الذي تريد الاستعلام عنه (مثال: +994...):", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_info)

def process_info(message):
    num = message.text.strip()
    result = get_status(num)
    
    if not result:
        text = "❌ هذا الرقم غير موجود في سجلات البوت."
    else:
        channel_id, status = result
        if status == "sold":
            text = f"💰 حالة الرقم `{num}`: **تم بيعه مسبقاً**."
        elif channel_id == CHANNELS["az"]:
            text = f"✅ حالة الرقم `{num}`: **موجود حالياً في قناة أذربيجان**."
        elif channel_id == CHANNELS["ua"]:
            text = f"✅ حالة الرقم `{num}`: **موجود حالياً في قناة أوكرانيا**."
        else:
            text = "❓ حالة الرقم غير معروفة."
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    start(message)

@bot.message_handler(func=lambda m: m.text == "إضافة حساب جديد ➕")
def ask_new(message):
    msg = bot.send_message(message.chat.id, "أرسل البيانات (حساب/باسورد/رقم):", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_auto_post)

def process_auto_post(message):
    try:
        lines = message.text.split('\n')
        acc, pas, num = lines[0].strip(), lines[1].strip(), lines[2].strip()
        target = CHANNELS["az"] if num.startswith("+994") else CHANNELS["ua"] if num.startswith("+380") else None
        
        if not target: return bot.send_message(message.chat.id, "❌ رقم غير مدعوم!")
        
        get_and_delete_msg(num)
        caption = f"【｡_｡𝐍𝐞𝐰 𝐇𝐢𝐭 𝐒𝐀𝐅𝐄𝐔𝐌 𝐀𝐜𝐜𝐨𝐮𝐧𝐭｡_｡】\n【𝐚𝐜𝐜𝐨𝐮𝐧𝐭 】【{acc}\n【𝐩𝐚𝐬𝐬      】【{pas}\n【𝐍𝐮𝐦𝐛𝐞𝐫】【{num}\n【｡_｡  𝐀𝐛𝐨 𝐍𝐚𝐲𝐚   𝟎𝟗𝟗𝟐  𝟒𝟒𝟑  𝟓𝟓𝟒 ｡_｡】"
        
        sent = bot.send_message(target, caption)
        save_msg(num, target, sent.message_id, "available")
        bot.send_message(message.chat.id, "✅ تم النشر وحفظ البيانات كـ 'متاح'.")
    except: bot.send_message(message.chat.id, "❌ خطأ في التنسيق.")
    start(message)

@bot.message_handler(func=lambda m: m.text == "مبيوع 💰")
def ask_sold(message):
    msg = bot.send_message(message.chat.id, "أرسل (حساب/باسورد/رقم/مالك):", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_sold_post)

def process_sold_post(message):
    try:
        lines = message.text.split('\n')
        acc, pas, num, owner = lines[0].strip(), lines[1].strip(), lines[2].strip(), lines[3].strip()
        
        get_and_delete_msg(num) # حذف من قنوات العرض

        caption = f"【｡_｡𝐍𝐞𝐰 𝐇𝐢𝐭 𝐒𝐀𝐅𝐄𝐔𝐌 𝐀𝐜𝐜𝐨𝐮𝐧𝐭｡_｡】\n【𝐚𝐜𝐜𝐨𝐮𝐧𝐭 】【{acc}\n【𝐍𝐮𝐦𝐛𝐞𝐫】【{num}\n【𝐩𝐚𝐬𝐬      】【{pas}\n【𝐎𝐰𝐧𝐞𝐫   】【{owner}\n【𝐝𝐚𝐭𝐞       】【{datetime.now().strftime('%Y-%m-%d')}\n【｡_｡  𝐀𝐛𝐨 𝐍𝐚𝐲𝐚   𝟎𝟗𝟗𝟐  𝟒𝟒𝟑  𝟓𝟓𝟒 ｡_｡】"
        
        bot.send_message(CHANNELS["sold"], caption)
        save_msg(num, CHANNELS["sold"], 0, "sold") # تحديث حالته في القاعدة لمبيوع
        bot.send_message(message.chat.id, "✅ تم النشر في المبيوعات وتحديث الحالة.")
    except: bot.send_message(message.chat.id, "❌ خطأ في البيانات.")
    start(message)

bot.infinity_polling()
