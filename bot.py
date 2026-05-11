import telebot
import sqlite3
from flask import Flask
from threading import Thread
import os

# তোর টোকেন এবং আইডি
TOKEN = '8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY'
CHANNEL_ID = '-1003351496871' 
CHANNEL_LINK = 'https://t.me/+fWQHyEKJepA2Njll'

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "তোর বট এখন অনলাইনে সচল আছে!"

def run():
    # রেন্ডার সার্ভারের জন্য পোর্ট সেটিংস
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ডাটাবেস ফাংশনসমূহ ---
def init_db():
    conn = sqlite3.connect('refer_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER, referred_by INTEGER, is_verified INTEGER)''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('refer_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res

def add_user(user_id, refer_id=None):
    if not get_user(user_id):
        conn = sqlite3.connect('refer_data.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (user_id, 0, refer_id, 0))
        conn.commit()
        conn.close()

# --- কমান্ড হ্যান্ডলার ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id)
    bot.reply_to(message, "তোর বট এখন সফলভাবে চালু হয়েছে!")

if __name__ == "__main__":
    init_db()
    keep_alive()
    print("বট স্টার্ট হচ্ছে...")
    bot.infinity_polling()
