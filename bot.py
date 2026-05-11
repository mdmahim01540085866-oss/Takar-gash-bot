import telebot
import sqlite3
from flask import Flask
from threading import Thread
import os

# --- কনফিগারেশন ---
TOKEN = '8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY'
CHANNEL_ID = '-1003351496871' 
CHANNEL_LINK = 'https://t.me/+fWQHyEKJepA2Njll'

bot = telebot.TeleBot(TOKEN, threaded=True)
app = Flask(__name__) # ঠিক করা হয়েছে

@app.route('/')
def home():
    return "টাকার গাছ বট একদম সচল আছে মামা!"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# --- ডাটাবেস ফাংশন ---
def init_db():
    conn = sqlite3.connect('refer_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, referred_by INTEGER, joined INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def is_joined(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# --- কিবোর্ড মেনু ---
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
    
    args = message.text.split()
    refer_id = args[1] if len(args) > 1 else None

    conn = sqlite3.connect('refer_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id, balance, referred_by, joined) VALUES (?, 0, ?, 0)", (user_id, refer_id))
        conn.commit()
    conn.close()

    if not is_joined(user_id):
        markup = telebot.ypes.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=CHANNEL_LINK))
        markup.add(telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="verify"))
        bot.send_message(user_id, "মামা, পেমেন্ট পেতে আগে চ্যানেলে জয়েন করে ভেরিফাই বাটনে ক্লিক কর!", reply_markup=markup)
    else:
        bot.send_message(user_id, "স্বাগতম মামা! মেনু ব্যবহার করুন।", reply_markup=main_menu())

# --- ভেরিফাই হ্যান্ডলার ---
@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    user_id = call.from_user.id
    if is_joined(user_id):
        conn = sqlite3.connect('refer_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT referred_by, joined FROM users WHERE user_id=?", (user_id,))
        res = cursor.fetchone()
        
        if res and res[1] == 0:
            ref_id = res[0]
            if ref_id and int(ref_id) != user_id:
                cursor.execute("UPDATE users SET balance = balance + 10 WHERE user_id=?", (ref_id,))
                try:
                    bot.send_message(ref_id, "🎉 নতুন রেফার! ১০ টাকা যোগ হয়েছে।")
                except: pass
            
            cursor.execute("UPDATE users SET joined = 1 WHERE user_id=?", (user_id,))
            conn.commit()
        conn.close()
        bot.answer_callback_query(call.id, "ভেরিফাই সফল হয়েছে!")
        bot.send_message(user_id, "সফলভাবে ভেরিফাই হয়েছে!", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "আগে চ্যানেলে জয়েন করুন!", show_alert=True)

# --- বাটন হ্যান্ডলার (নতুন যোগ করা হয়েছে) ---
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.chat.id
    conn = sqlite3.connect('refer_data.db')
    cursor = conn.cursor()

    if message.text == "💰 ব্যালেন্স":
        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        res = cursor.fetchone()
        balance = res[0] if res else 0
        bot.reply_to(message, f"আপনার বর্তমান ব্যালেন্স: {balance} টাকা")

    elif message.text == "👥 রেফার":
        ref_link = f"https://t.me/{(bot.get_me().username)}?start={user_id}"
        bot.reply_to(message, f"আপনার রেফার লিংক:\n{ref_link}\n\nপ্রতি রেফার ১৫ টাকা!")

    elif message.text == "💳 উইথড্র":
        bot.reply_to(message, "উইথড্র অপশন শীঘ্রই আসছে!")

    elif message.text == "📊 স্ট্যাটিস্টিক্স":
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        bot.reply_to(message, f"মোট ইউজার: {total_users}")

    conn.close()

# --- রানার ---
if __name__ == '__main__':
    init_db()
    Thread(target=run_flask).start()
    bot.infinity_polling()if (balance < 1000) {
    alert("আগে 1000 পুরা করো মামা!");
} else {
    // Withdraw process starts
            }
