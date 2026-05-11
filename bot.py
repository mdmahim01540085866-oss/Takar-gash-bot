import telebot
import sqlite3
from flask import Flask
from threading import Thread
import os

# আপনার তথ্যসমূহ
TOKEN = '8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY'
CHANNEL_ID = '-1003351496871' 
CHANNEL_LINK = 'https://t.me/+fWQHyEKJepA2Njll'
ADMIN_ID = 6871732560 # আপনার নিজের টেলিগ্রাম আইডি এখানে দিন

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "সচল আছে!"

def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ডাটাবেস ---
def init_db():
    conn = sqlite3.connect('refer_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER, referred_by INTEGER)''')
    conn.commit()
    conn.close()

def check_join(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# --- মেনু ---
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 ব্যালেন্স", "👥 রেফার")
    markup.row("💳 উইথড্র", "📊 স্ট্যাটিস্টিক্স")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    args = message.text.split()
    refer_id = args[1] if len(args) > 1 else None

    conn = sqlite3.connect('refer_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user_id, 0, refer_id))
        conn.commit()
    conn.close()

    if not check_join(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=CHANNEL_LINK))
        markup.add(telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="verify"))
        bot.send_message(user_id, "সম্মানিত ইউজার মামা, আমাদের বটের সেবা পেতে প্রথমে নিচের চ্যানেলে জয়েন করুন এবং ভেরিফাই বাটনে ক্লিক করুন।", reply_markup=markup)
    else:
        bot.send_message(user_id, "স্বাগতম মামা! আপনি সফলভাবে লগইন করেছেন।", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    user_id = call.from_user.id
    if check_join(user_id):
        conn = sqlite3.connect('refer_data.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT referred_by FROM users WHERE user_id=?", (user_id,))
        res = cursor.fetchone()
        
        # যদি রেফার লিংকে এসে থাকে এবং আগে ভেরিফাই না হয়ে থাকে
        if res and res[0]:
            ref_id = res[0]
            cursor.execute("UPDATE users SET balance = balance + 10 WHERE user_id=?", (ref_id,))
            cursor.execute("UPDATE users SET referred_by = NULL WHERE user_id=?", (user_id,))
            conn.commit()
            try: bot.send_message(ref_id, "মামা! আপনার রেফার লিংকে একজন জয়েন করেছে। আপনি ১০ টাকা বোনাস পেয়েছেন।")
            except: pass
        
        conn.close()
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "ভেরিফিকেশন সফল! এখন আপনি বট ব্যবহার করতে পারবেন।", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "মামা, আগে জয়েন করুন!", show_alert=True)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.chat.id
    if not check_join(user_id):
        return start(message)

    conn = sqlite3.connect('refer_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cursor.fetchone()[0]
    conn.close()

    if message.text == "💰 ব্যালেন্স":
        bot.send_message(user_id, f"আপনার বর্তমান ব্যালেন্স: {balance} টাকা।")
    
    elif message.text == "👥 রেফার":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        bot.send_message(user_id, f"প্রতি রেফারে পাবেন ১০ টাকা।\nআপনার রেফার লিংক:\n{ref_link}")

    elif message.text == "💳 উইথড্র":
        if balance < 1000:
            bot.send_message(user_id, "দুঃখিত মামা, উইথড্র করতে কমপক্ষে ১০০০ টাকা প্রয়োজন।")
        else:
            bot.send_message(user_id, "উইথড্র করতে আপনার বিকাশ/নগদ নাম্বার এবং টাকার পরিমাণ লিখে এডমিনকে মেসেজ দিন।")

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling()
