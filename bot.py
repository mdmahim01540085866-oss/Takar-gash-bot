
# -*- coding: utf-8 -*-
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
    return "Takar Gash Bot is Running!"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def get_db():
    # ডাটাবেস কানেকশন এবং টাইমআউট সেট করা হয়েছে যাতে ডাটা ঠিকমতো সেভ হয়
    conn = sqlite3.connect('refer_data.db', check_same_thread=False, timeout=10)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, referred_by INTEGER, joined INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def is_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
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
        # নতুন ইউজার হলে রেফারার আইডি সেভ হবে
        cursor.execute("INSERT INTO users (user_id, balance, referred_by, joined) VALUES (?, 0, ?, 0)", (user_id, ref_id))
        conn.commit()
    conn.close()

    if not is_joined(user_id):
        m = telebot.types.InlineKeyboardMarkup()
        m.add(telebot.types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=CHANNEL_LINK))
        m.add(telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="verify"))
        bot.send_message(user_id, "স্বাগতম মামা! ১০ টাকা বোনাস পেতে আগে চ্যানেলে জয়েন করো, তারপর ভেরিফাই করো।", reply_markup=m)
    else:
        bot.send_message(user_id, "স্বাগতম মামা! মেনু ব্যবহার করো।", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    user_id = call.from_user.id
    if is_joined(user_id):
        conn = get_db()
        cursor = conn.cu
