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

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "বট একদম সচল আছে মামা!"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# --- ডাটাবেস ---
def init_db():
    conn = sqlite3.connect('refer_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER, referred_by INTEGER, joined INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# --- মেম্বারশিপ চেক ---
def check_join(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
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
    
    # রেফার আইডি চেক
    text = message.text.split()
    refer_id = text[1] if len(text) > 1 else None

    conn = sqlite3.connect('refer_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        # নতুন ইউজার হলে ডাটাবেসে সেভ করো
        cursor.execute("INSERT INTO users (user_id, balance, referred_by) VALUES (?, ?, ?)", (user_id, 0, refer_id))
        conn.commit()
    conn.close()

    # জয়েন চেক
    if not check_join(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=CHANNEL_LINK))
        markup.add(telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="verify"))
        bot.send_message(user_id, "মামা, আগে আমাদের চ্যানেলে জয়েন করতে হবে। নাহলে ব্যালেন্স পাবেন না!", reply_markup=markup)
    else:
        bot.send_message(user_id, "স্বাগতম মামা! আপনি অলরেডি জয়েন আছেন।", reply_markup=main_menu())

# --- ভেরিফাই বাটন ---
@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    user_id = call.from_user.id
    if check_join(user_id):
        conn = sqlite3.connect('refer_data.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # চেক করো আগে বোনাস পেয়েছে কি না
        cursor.execute("SELECT referred_by, joined FROM users WHERE user_id=?", (user_id,))
        res = cursor.fetchone()
        
        if res and res[1] == 0: # যদি আগে জয়েন না হয়ে থাকে (joined=0)
            ref_id = res[0]
            if ref_id and int(ref_id) != user_id:
                cursor.execute("UPDATE users SET balance = balance + 10 WHERE user_id=?", (ref_id,))
                try:
                    bot.send_message(ref_id, f"মামা! আপনার রেফার লিংকে একজন জয়েন করেছে। ১০ টাকা বোনাস পেলেন।")
                except: pass
            
            # জয়েন স্ট্যাটাস ১ করে দাও যাতে বারবার টাকা না পায়
            cursor.execute("UPDATE users SET joined = 1 WHERE user_id=?", (user_id,))
            conn.commit()
        
        conn.close()
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "ভেরিফিকেশন সফল! এখন কাজ শুরু করুন।", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "আরে মামা, আগে জয়েন তো করেন! তারপর ভেরিফাই ক্লিক করেন।", show_alert=True)

# --- টেক্সট হ্যান্ডলার ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.chat.id
    if not check_join(user_id):
        return start(message)

    conn = sqlite3.connect('refer_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    balance = res[0] if res else 0
    conn.close()

    if message.text == "💰 ব্যালেন্স":
        bot.send_message(user_id, f"আপনার ব্যালেন্স: {balance} টাকা")
    elif message.text == "👥 রেফার":
        bot_user = bot.get_me().username
        bot.send_message(user_id, f"আপনার রেফার লিংক:\nhttps://t.me/{bot_user}?start={user_id}")
    elif message.text == "💳 উইথড্র":
        bot.send_message(user_id, "উইথড্র করতে ১০০০ টাকা লাগবে মামা। আপনার আছে মাত্র " + str(balance) + " টাকা।")

if __name__ == "__main__":
    init_db()
    Thread(target=run_flask).start()
    print("বট একদম রেডি মামা!")
    bot.infinity_polling()
