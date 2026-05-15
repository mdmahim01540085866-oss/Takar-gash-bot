# -*- coding: utf-8 -*-
import telebot, sqlite3, os
from flask import Flask
from threading import Thread

# --- কনফিগারেশন (তোর নতুন চ্যানেল ডিটেইলস) ---
TOKEN = '8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY'
CH_ID = -1003842595357
CH_LINK = 'https://t.me/Bezznxt'
ADMIN = 6871732560

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask('')
@app.route('/')
def home(): return "Bot Running"

def db_q(sql, p=()):
    with sqlite3.connect('refer_data.db', timeout=20) as conn:
        cur = conn.cursor()
        cur.execute(sql, p); conn.commit()
        return cur.fetchall()

def is_j(uid):
    try: return bot.get_chat_member(CH_ID, uid).status in ['member', 'administrator', 'creator']
    except: return False

def main_m():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 ব্যালেন্স", "🎁 রেফার")
    kb.row("📝 টাস্ক", "💸 উইথড্র")
    kb.row("📊 স্ট্যাটিস্টিকস"); return kb

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.chat.id
    db_q('''CREATE TABLE IF NOT EXISTS users 
            (uid INTEGER PRIMARY KEY, bal INTEGER DEFAULT 0, ref INTEGER, 
             jnd INTEGER DEFAULT 0, r_cnt INTEGER DEFAULT 0, m_state INTEGER DEFAULT 0)''')
    
    args = m.text.split()
    rid = args[1] if len(args) > 1 else None
    
    if not db_q("SELECT uid FROM users WHERE uid=?", (uid,)):
        db_q("INSERT INTO users (uid, bal, ref, jnd, r_cnt, m_state) VALUES (?, 0, ?, 0, 0, 0)", (uid, rid))
    
    if not is_j(uid):
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=CH_LINK))
        kb.add(telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="vfy"))
        bot.send_message(uid, "স্বাগতম মামা! ১০ টাকা বোনাস পেতে আগে চ্যানেলে জয়েন করো, তারপর ভেরিফাই করো।", reply_markup=kb)
    else:
        bot.send_message(uid, "মামা, তোমার একাউন্ট আনলক আছে!", reply_markup=main_m())

@bot.callback_query_handler(func=lambda c: c.data == "vfy")
def vfy(c):
    uid = c.from_user.id
    if is_j(uid):
        res = db_q("SELECT ref, jnd FROM users WHERE uid=?", (uid,))
        if res and res[0][1] == 0:
            rid = res[0][0]
            db_q("UPDATE users SET bal = bal + 10, jnd = 1 WHERE uid=?", (uid,))
            if rid and int(rid) != uid:
                db_q("UPDATE users SET bal = bal + 10, r_cnt = r_cnt + 1 WHERE uid=?", (rid,))
                try: bot.send_message(rid, "🎉 মামা! তোমার রেফারে একজন জয়েন করেছে। ১০ টাকা বোনাস পেয়েছো!")
                except: pass
            bot.delete_message(uid, c.message.message_id)
            bot.send_message(uid, "✅ ভেরিফিকেশন সফল! ১০ টাকা বোনাস পেয়েছো।", reply_markup=main_m())
    else:
        bot.answer_callback_query(c.id, "আগে চ্যানেলে জয়েন করো মামা!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    uid = message.chat.id
    if not is_j(uid): return start(message)

    res = db_q("SELECT bal, r_cnt, m_state FROM users WHERE uid=?", (uid,))
    if not res: return start(message)
    bal, r_cnt, m_state = res[0]

    if message.text == "💰 ব্যালেন্স":
        bot.send_message(uid, f"আপনার বর্তমান ব্যালেন্স: `{bal} টাকা` \nমোট রেফার: `{r_cnt}` জন", parse_mode="Markdown")

    elif message.text == "🎁 রেফার":
        ref_link = f"https://t.me/{(bot.get_me().username)}?start={uid}"
        bot.send_message(uid, f"প্রতি রেফার ১০ টাকা! \nলিংক: `{ref_link}`", parse_mode="Markdown")

    elif message.text == "📝 টাস্ক":
        msg = f"🎯 **রেফার মাইলস্টোন টাস্ক**\n\n"
        msg += f"১. ১০ রেফার: ১২০ টাকা বোনাস {'✅' if m_state >= 1 else '❌'}\n"
        msg += f"২. ২০ রেফার: ২৫০ টাকা বোনাস {'✅' if m_state >= 2 else '❌'}\n"
        msg += f"৩. ৪০ রেফার: ৫০০ টাকা বোনাস {'✅' if m_state >= 3 else '❌'}\n\n"
        msg += f"আপনার মোট রেফার: `{r_cnt}` জন।\n"
        
        kb = telebot.types.InlineKeyboardMarkup()
        if r_cnt >= 10 and m_state == 0:
            kb.add(telebot.types.InlineKeyboardButton("১০ রেফার বোনাস নিন 🎁", callback_data="claim_1"))
        if r_cnt >= 20 and m_state == 1:
            kb.add(telebot.types.InlineKeyboardButton("২০ রেফার বোনাস নিন 🎁", callback_data="claim_2"))
        if r_cnt >= 40 and m_state == 2:
            kb.add(telebot.types.InlineKeyboardButton("৪০ রেফার বোনাস নিন 🎁", callback_data="claim_3"))
        
        bot.send_message(uid, msg, reply_markup=kb, parse_mode="Markdown")

    elif message.text == "💸 উইথড্র":
        if bal < 1000: bot.send_message(uid, "❌ আগে 1000 টাকা পুরা করো মামা!")
        else: bot.send_message(uid, "✅ আপনার উইথড্র রিকোয়েস্টটি প্রসেসিংয়ে আছে।")

    elif message.text == "📊 স্ট্যাটিস্টিকস":
        bot.send_message(uid, "📊 শীঘ্রই আসছে...")

@bot.callback_query_handler(func=lambda c: c.data.startswith('claim_'))
def claim_bonus(c):
    uid = c.from_user.id
    res
