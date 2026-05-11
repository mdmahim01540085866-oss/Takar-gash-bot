import telebot
import sqlite3
from flask import Flask
from threading import Thread
import os

# --- কনফিগারেশন ---
TOKEN = '8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY'
CHANNEL_ID = '-1003351496871' 
CHANNEL_LINK = 'https://t.me/+fWQHyEKJepA2Njll'

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask('')

@app.route('/')
def home():
    return "টাকার গাছ বট একদম সচল!"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# --- ডাটাবেস ফাংশন ---
def get_db():
    conn = sqlite3.connect('refer_data.db', check_same_thread=False)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # joined কলামটা নিশ্চিত করা হচ্ছে
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, referred_by INTEGER, joined INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# --- মেম্বারশিপ চেক ---
def is_joined(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# --- মেনু ---
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 ব্যালেন্স", "👥 রেফার")
    markup.row("💳 উইথড্র", "📊 স্ট্যাটিস্টিক্স")
    return markup

# --- স্টার্ট কমান্ড ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    init_db()
    
    text = message.text.split()
    refer_id = text[1] if len(text) > 1 else None

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        # একদম নতুন ইউজার হলে ডাটাবেসে ঢোকানো হচ্ছে
        cursor.execute("INSERT INTO users (user_id, balance, referred_by, joined) VALUES (?, 0, ?, 0)", (user_id, refer_id))
        conn.commit()
    conn.close()

    if not is_joined(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=CHANNEL_LINK))
        markup.add(telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="verify"))
        bot.send_message(user_id, "মামা, চ্যানেলে জয়েন করে ভেরিফাই না করলে রেফার বোনাস অ্যাড হবে না!", reply_markup=markup)
    else:
        bot.send_message(user_id, "স্বাগতম মামা! মেনু ব্যবহার করুন।", reply_markup=main_menu())

# --- ভেরিফাই বাটন (আসল জাদুর জায়গা) ---
@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    user_id = call.from_user.id
    if is_joined(user_id):
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT referred_by, joined FROM users WHERE user_id=?", (user_id,))
        res = cursor.fetchone()
        
        if res and res[1] == 0:  # যদি ইউজার আগে কখনো ভেরিফাই না করে থাকে
            ref_id = res[0]
            if ref_id and int(ref_id) != user_id:
                # রেফারারকে ১০ টাকা দেওয়া হচ্ছে
                cursor.execute("UPDATE users SET balance = balance + 10 WHERE user_id=?", (ref_id,))
                conn.commit()
                try:
                    bot.send_message(ref_id, "মামা! আপনার রেফার লিংকে একজন নতুন মেম্বার জয়েন করেছে। ১০ টাকা বোনাস পেলেন! 🎉")
                except: pass
            
            # এই ইউজারের কাজ শেষ, joined = 1 করে দিলাম
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
    
    if message.text == "💰 ব্যালেন্স":
        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        res = cursor.fetchone()
        balance = res[0] if res else 0
        bot.send_message(user_id, f"আপনার বর্তমান ব্যালেন্স: {balance} টাকা।")
    
    elif message.text == "👥 রেফার":
        bot_user = bot.get_me().username
        bot.send_message(user_id, f"প্রতি রেফারে ১০ টাকা!\nলিংক:\nhttps://t.me/{bot_user}?start={user_id}")
    
    conn.close()

if __name__ == "__main__":
    init_db()
    Thread(target=run_flask).start()
    print("বট সচল হচ্ছে...")
    bot.infinity_polling()
