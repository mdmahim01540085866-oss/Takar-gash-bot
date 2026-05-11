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
