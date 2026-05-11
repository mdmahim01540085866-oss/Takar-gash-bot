import telebot
import sqlite3
from flask import Flask
from threading import Thread
import os

# --- কনফিগারেশন ---
TOKEN = '8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY'
CHANNEL_ID = '-1003351496871' 
CHANNEL_LINK = 'https://t.me/+fWQHyEKJepA2Njll'
ADMIN_ID = 6871732560 

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask('')

@app.route('/')
def home():
    return "টাকার গাছ বট একদম সচল আছে মামা!"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def get_db():
    return sqlite3.connect('refer_data.db', check_same_thread=False)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, referred_by INTEGER, joined INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def is_joined(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 ব্যালেন্স", "👥 রেফার")
    markup.row("💳 উইথড্র", "📊 স্ট্যাটিস্টিক্স")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    init_db()
    args = message.text.split()
    ref_id = args[1] if len(args) > 1 else None
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, balance, referred_by, joined) VALUES (?, 0, ?, 0)", (user_id, ref_id))
        conn.commit()
    conn.close()

    if not is_joined(user_id):
        m = telebot.types.InlineKeyboardMarkup()
        m.add(telebot.types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=CHANNEL_LINK))
        m.add(telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="verify"))
        bot.send_message(user_id, "মামা, আগে জয়েন করে ভেরিফাই কর!", reply_markup=m)
    else:
        bot.send_message(user_id, "স্বাগতম মামা! মেনু ব্যবহার কর।", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    user_id = call.from_user.id
    if is_joined(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT referred_by, joined FROM users WHERE user_id=?", (user_id,))
        res = cursor.fetchone()
        if res and res[1] == 0:
            rid = res[0]
            if rid and int(rid) != user_id:
                cursor.execute("UPDATE users SET balance = balance + 10 WHERE user_id=?", (rid,))
                conn.commit()
                try: bot.send_message(rid, "🎉 মামা! ১ জন জয়েন করেছে। ১০ টাকা বোনাস পেয়েছো!")
                except: pass
            cursor.execute("UPDATE users SET joined = 1 WHERE user_id=?", (user_id,))
            conn.commit()
        conn.close()
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "ভেরিফিকেশন সফল মামা!", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "আগে জয়েন তো কর মামা!", show_alert=True)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.chat.id
    if not is_joined(user_id): return start(message)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    balance = res[0] if res else 0

    if message.text == "💰 ব্যালেন্স":
        bot.send_message(user_id, f"তোর বর্তমান ব্যালেন্স: {balance} টাকা।")
    elif message.text == "👥 রেফার":
        bot_user = bot.get_me().username
        bot.send_message(user_id, f"লিংক:\nhttps://t.me/{bot_user}?start={user_id}")
    elif message.text == "📊 স্ট্যাটিস্টিক্স":
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        bot.send_message(user_id, f"📊 মোট ইউজার: {total} জন।")
    elif message.text == "💳 উইথড্র":
        if balance < 1000:
            bot.send_message(user_id, "আগে ১০০০ পুরা করো মামা! তোমার ব্যালেন্সে পর্যাপ্ত টাকা নাই।")
        else:
            msg = bot.send_message(user_id, "মামা, ১০০০ টাকা হয়ে গেছে! এখন তোমার বিকাশ বা নগদ নাম্বারটা লিখে দাও।", reply_markup=telebot.types.ForceReply())
            bot.register_next_step_handler(msg, process_withdraw)
    conn.close()

def process_withdraw(message):
    user_id = message.chat.id
    number = message.text
    bot.send_message(user_id, f"মামা, তোমার নাম্বার ({number}) সেভ করা হয়েছে। এডমিন চেক করে পেমেন্ট করে দিবে।")
    bot.send_message(ADMIN_ID, f"📢 উইথড্র রিকোয়েস্ট!\nআইডি: {user_id}\nনাম্বার: {number}")

if __name__ == "__main__":
    init_db()
    Thread(target=run_flask).start()
    bot.infinity_polling()
