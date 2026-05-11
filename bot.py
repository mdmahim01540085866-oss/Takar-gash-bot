infinity_polling()*- c:(user_id, "স্বাগতম মামা! ১০ টাকা বোনাস পেতে আগে চ্যানেলে জয়েন করো, তারপর ভেরিফাই করো।", reply_markup=m)
    else:
        bot.send_message(user_id, "স্বাগতম মামা! মেনু ব্যবহার করো।", reply_markup=main_menu())

@# -*- coding: utf-8 -*-
import telebot, sqlite3, os
from flask import Flask
from threading import Thread

TOKEN = '8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY'
CH_ID, ADMIN = '-1003351496871', 6871732560
CH_LINK = 'https://t.me/+fWQHyEKJepA2Njll'

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask('')
@app.route('/')
def home(): return "Bot Running"

# ডাটাবেস কানেকশন মজবুত করা হয়েছে
def db_query(sql, params=()):
    try:
        conn = sqlite3.connect('refer_data.db', check_same_thread=False, timeout=20)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        res = cursor.fetchall()
        conn.close()
        return res
    except Exception as e:
        print(f"DB Error: {e}")
        return None

def init_db():
    db_query('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, bal INTEGER DEFAULT 0, ref INTEGER, jnd INTEGER DEFAULT 0)')

def is_j(uid):
    try: return bot.get_chat_member(CH_ID, uid).status in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.chat.id
    init_db()
    args = m.text.split()
    rid = args[1] if len(args) > 1 else None
    
    if not db_query("SELECT uid FROM users WHERE uid=?", (uid,)):
        db_query("INSERT INTO users (uid, bal, ref, jnd) VALUES (?, 0, ?, 0)", (uid, rid))
    
    if not is_j(uid):
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=CH_LINK))
        kb.add(telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="vfy"))
        bot.send_message(uid, "মামা, চ্যানেলে জয়েন করে ভেরিফাই করলেই তুমি ১০ টাকা আর তোমার বন্ধু ১০ টাকা পাবে!", reply_markup=kb)
    else: bot.send_message(uid, "স্বাগতম মামা! মেনু ব্যবহার করো।", reply_markup=main_m())

@bot.callback_query_handler(func=lambda c: c.data == "vfy")
def vfy(c):
    uid = c.from_user.id
    if is_j(uid):
        res = db_query("SELECT ref, jnd FROM users WHERE uid=?", (uid,))
        if res and res[0][1] == 0:
            rid = res[0][0]
            # নতুন ইউজার ও রেফারার দুই পক্ষকেই ১০ টাকা দেওয়া
            db_query("UPDATE users SET bal = bal + 10, jnd = 1 WHERE uid=?", (uid,))
            if rid and int(rid) != uid:
                db_query("UPDATE users SET bal = bal + 10 WHERE uid=?", (rid,))
                try: bot.send_message(rid, "🎉 মামা! তোমার রেফারে একজন জয়েন করেছে। ১০ টাকা বোনাস পেয়েছো!")
                except: pass
            
            bot.delete_message(uid, c.message.message_id)
            bot.send_message(uid, "১০ টাকা বোনাস পেয়েছো মামা!", reply_markup=main_m())
        else: bot.answer_callback_query(c.id, "মামা, তুমি অলরেডি বোনাস নিয়েছো!", show_alert=True)
    else: bot.answer_callback_query(c.id, "আগে চ্যানেলে জয়েন তো করো মামা!", show_alert=True)

def main_m():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 ব্যালেন্স", "👥 রেফার")
    markup.row("💳 উইথড্র", "📊 স্ট্যাটিস্টিক্স")
    return markup

@bot.message_handler(func=lambda m: True)
def hdl(m):
    uid = m.chat.id
    if not is_j(uid): return start(m)
    
    if m.text == "💰 ব্যালেন্স":
        res = db_query("SELECT bal FROM users WHERE uid=?", (uid,))
        bal = res[0][0] if res else 0
        bot.send_message(uid, f"আপনার বর্তমান ব্যালেন্স: {bal} টাকা।")
    elif m.text == "👥 রেফার":
        bot.send_message(uid, f"প্রতি রেফারে ১০ টাকা!\nলিংক: https://t.me/{bot.get_me().username}?start={uid}")
    elif m.text == "📊 স্ট্যাটিস্টিক্স": 
        res = db_query("SELECT COUNT(*) FROM users")
        bot.send_message(uid, f"📊 বটের মোট মেম্বার: {res[0][0]} জন।")
    elif m.text == "💳 উইথড্র":
        res = db_query("SELECT bal FROM users WHERE uid=?", (uid,))
        bal = res[0][0] if res else 0
        if bal < 1000: bot.send_message(uid, f"আগে ১০০০ টাকা পুরা করো মামা! ব্যালেন্স: {bal} টাকা।")
        else: bot.send_message(uid, "মামা, ১০০০ টাকা হয়ে গেছে! তোমার বিকাশ নাম্বার দাও।")

if __name__ == "__main__":
    init_db()
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))).start()
    bot.infinity_polling()
