# -*- coding: utf-8 -*-
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

def db_q(sql, p=()):
    with sqlite3.connect('refer_data.db', timeout=20) as conn:
        cur = conn.cursor()
        cur.execute(sql, p)
        conn.commit()
        return cur.fetchall()

def init():
    db_q('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, bal INTEGER DEFAULT 0, ref INTEGER, jnd INTEGER DEFAULT 0)')

def is_j(uid):
    try: return bot.get_chat_member(CH_ID, uid).status in ['member', 'administrator', 'creator']
    except: return False

def main_m():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 ব্যালেন্স", "👥 রেফার")
    kb.row("💳 উইথড্র", "📊 স্ট্যাটিস্টিক্স")
    return kb

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.chat.id
    init()
    ref = m.text.split()[1] if len(m.text.split()) > 1 else None
    if not db_q("SELECT uid FROM users WHERE uid=?", (uid,)):
        db_q("INSERT INTO users (uid, bal, ref, jnd) VALUES (?, 0, ?, 0)", (uid, ref))
    
    if not is_j(uid):
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("জয়েন করুন 📢", url=CH_LINK))
        kb.add(telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="vfy"))
        bot.send_message(uid, "মামা, আগে জয়েন কর তারপর ভেরিফাই বাটনে চাপ দে!", reply_markup=kb)
    else: bot.send_message(uid, "স্বাগতম মামা!", reply_markup=main_m())

@bot.callback_query_handler(func=lambda c: c.data == "vfy")
def vfy(c):
    uid = c.from_user.id
    if is_j(uid):
        res = db_q("SELECT ref, jnd FROM users WHERE uid=?", (uid,))
        if res and res[0][1] == 0:
            rid = res[0][0]
            db_q("UPDATE users SET bal = bal + 10, jnd = 1 WHERE uid=?", (uid,))
            if rid:
                db_q("UPDATE users SET bal = bal + 10 WHERE uid=?", (rid,))
                try: bot.send_message(rid, "🎉 রেফার বোনাস ১০ টাকা পেয়েছো!")
                except: pass
            bot.delete_message(uid, c.message.message_id)
            bot.send_message(uid, "ভেরিফাই সফল! ১০ টাকা বোনাস পেয়েছো।", reply_markup=main_m())
    else: bot.answer_callback_query(c.id, "আগে জয়েন তো কর!", show_alert=True)

@bot.message_handler(func=lambda m: True)
def hdl(m):
    uid = m.chat.id
    if not is_j(uid): return start(m)
    res = db_q("SELECT bal FROM users WHERE uid=?", (uid,))
    bal = res[0][0] if res else 0
    if m.text == "💰 ব্যালেন্স": bot.send_message(uid, f"ব্যালেন্স: {bal} টাকা")
    elif m.text == "👥 রেফার": bot.send_message(uid, f"লিংক: https://t.me/{bot.get_me().username}?start={uid}")
    elif m.text == "📊 স্ট্যাটিস্টিক্স": 
        cnt = db_q("SELECT COUNT(*) FROM users")[0][0]
        bot.send_message(uid, f"মোট মেম্বার: {cnt}")

if __name__ == "__main__":
    init()
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))).start()
    bot.infinity_polling()
