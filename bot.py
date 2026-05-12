# -*- coding: utf-8 -*-
import telebot, sqlite3, os
from flask import Flask
from threading import Thread

# --- কনফিগারেশন ---
TOKEN = '8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY'
CH_ID = -1003351496871
CH_LINK = 'https://t.me/+fWQHyEKJepA2Njll'
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

# মেইন মেনু কিবোর্ড (শুধু জয়েন করার পর দেখা যাবে)
def main_m():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 ব্যালেন্স", "🎁 রেফার")
    kb.row("💸 উইথড্র", "📊 স্ট্যাটিস্টিকস"); return kb

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.chat.id
    db_q('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, bal INTEGER DEFAULT 0, ref INTEGER, jnd INTEGER DEFAULT 0)')
    
    args = m.text.split()
    ref = args[1] if len(args) > 1 else None
    
    if not db_q("SELECT uid FROM users WHERE uid=?", (uid,)):
        db_q("INSERT INTO users (uid, bal, ref, jnd) VALUES (?, 0, ?, 0)", (uid, ref))
    
    # ১ম ইন্টারফেস: জয়েন না থাকলে শুধু এই মেসেজটাই দেখাবে
    if not is_j(uid):
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=CH_LINK))
        kb.add(telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="vfy"))
        bot.send_message(uid, "স্বাগতম মামা! ১০ টাকা বোনাস পেতে আগে চ্যানেলে জয়েন করো, তারপর ভেরিফাই বাটনে ক্লিক করো। নাহলে বট খুলবে না।", reply_markup=kb)
    else:
        bot.send_message(uid, "মামা, তোমার একাউন্ট অলরেডি আনলক আছে!", reply_markup=main_m())

@bot.callback_query_handler(func=lambda c: c.data == "vfy")
def vfy(c):
    uid = c.from_user.id
    if is_j(uid):
        res = db_q("SELECT ref, jnd FROM users WHERE uid=?", (uid,))
        if res and res[0][1] == 0:
            rid = res[0][0]
            # ইউজারের নিজের ব্যালেন্সে  ৩০ টাকা অ্যাড
            db_q("UPDATE users SET bal = bal + 10, jnd = 1 WHERE uid=?", (uid,))
            # রেফারারের ব্যালেন্সে ৩০ টাকা অ্যাড
            if rid and int(rid) != uid:
                db_q("UPDATE users SET bal = bal + ৩০ WHERE uid=?", (rid,))
                try: bot.send_message(rid, "🎉 মামা! তোমার রেফার লিংকে একজন সফলভাবে জয়েন করেছে। ১০ টাকা বোনাস পেয়েছো!")
                except: pass
            
            bot.delete_message(uid, c.message.message_id)
            bot.send_message(uid, "✅ ভেরিফিকেশন সফল! ৩৫ টাকা বোনাস পেয়েছো মামা। এখন নিচে থেকে মেনু ব্যবহার করো।", reply_markup=main_m())
        else:
            bot.answer_callback_query(c.id, "মামা, তুমি তো অলরেডি বোনাস নিয়েছো!", show_alert=True)
    else:
        bot.answer_callback_query(c.id, "আগে চ্যানেলে জয়েন তো করো মামা!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.chat.id
    
    # কেউ জয়েন না করে মেসেজ দিলে তাকে ১ম ইন্টারফেসে পাঠাবে
    if not is_j(user_id):
        return start(message)

    res = db_q("SELECT bal FROM users WHERE uid=?", (user_id,))
    if not res: return start(message)
    balance = res[0][0]

    if message.text == "💰 ব্যালেন্স":
        bot.send_message(user_id, f"আপনার বর্তমান ব্যালেন্স: `{balance} টাকা`", parse_mode="Markdown")

    elif message.text == "🎁 রেফার":
        ref_link = f"https://t.me/{(bot.get_me().username)}?start={user_id}"
        bot.send_message(user_id, f"আপনার রেফার লিংক:\n`{ref_link}`\n\nপ্রতি রেফার এ পান ১০ টাকা!", parse_mode="Markdown")

    elif message.text == "💸 উইথড্র":
        if balance < 1000:
            bot.send_message(user_id, "❌ আগে 1000 টাকা পুরা করো মামা!")
        else:
            bot.send_message(user_id, "✅ আপনার উইথড্র রিকোয়েস্টটি প্রসেসিংয়ে আছে। অ্যাডমিন শীঘ্রই যোগাযোগ করবে।")

    elif message.text == "📊 স্ট্যাটিস্টিকস":
        bot.send_message(user_id, "📊 স্ট্যাটিস্টিকস ফিচারটি শীঘ্রই আসছে...")

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))).start()
    bot.infinity_polling()
