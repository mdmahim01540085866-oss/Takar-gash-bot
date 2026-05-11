import telebot
import sqlite3
from flask import Flask
from threading import Thread
import os

# আপনার বটের তথ্য
TOKEN = '8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY'
CHANNEL_ID = '-1003351496871' 
CHANNEL_LINK = 'https://t.me/+fWQHyEKJepA2Njll'

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "বট সচল আছে!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

def init_db():
    conn = sqlite3.connect('refer_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER, referred_by INTEGER, is_verified INTEGER)''')
    conn.commit()
    conn.close()

def check_join(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    init_db()
    
    if not check_join(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=CHANNEL_LINK))
        markup.add(telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="verify"))
        bot.send_message(user_id, "সম্মানিত ইউজার মামা, আমাদের বটের সেবা পেতে প্রথমে নিচের চ্যানেলে জয়েন করুন এবং ভেরিফাই বাটনে ক্লিক করুন।", reply_markup=markup)
    else:
        bot.send_message(user_id, "অভিনন্দন মামা! আপনি এখন সফলভাবে বটটি ব্যবহার করতে পারবেন।")

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify_user(call):
    if check_join(call.from_user.id):
        bot.answer_callback_query(call.id, "আপনার ভেরিফিকেশন সফল হয়েছে!")
        bot.edit_message_text("ধন্যবাদ মামা! আপনার ভেরিফিকেশন সম্পন্ন হয়েছে।", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "মামা, আপনি এখনো চ্যানেলে জয়েন করেননি!", show_alert=True)

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling()
