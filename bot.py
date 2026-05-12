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

def main_m():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 ব্যালেন্স", "🎁 রেফার")
    kb.row("💸 উইথড্র", "📊 স্ট্যাটিস্টিকস"); return kb

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.chat.id
    # ডাটাবেসে মাইলস্টোন ট্র্যাকিং এর জন্য কলাম অ্যাড করা হয়েছে
    db_q('''CREATE TABLE IF NOT EXISTS users 
            (uid INTEGER PRIMARY KEY, bal INTEGER DEFAULT 0, ref INTEGER, 
             jnd INTEGER DEFAULT 0, ref_count INTEGER DEFAULT 0, m_state INTEGER DEFAULT 0)''')
    
    args = m.text.split()
    rid = args[1] if len(args) > 1 else None
    
    if not db_q("SELECT uid FROM users WHERE uid=?", (uid,)):
        db_q("INSERT INTO users (uid, bal, ref, jnd, ref_count, m_state) VALUES (?, 0, ?, 0, 0, 0)", (uid, rid))
    
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
                # রেফারারের কাউন্ট বাড়ানো
                db_q("UPDATE users SET bal = bal + 10, ref_count = ref_count + 1 WHERE uid=?", (rid,))
                
                # মাইলস্টোন বোনাস চেক
                check_milestone(rid)
                
                try: bot.send_message(rid, "🎉 মামা! রেফারে একজন জয়েন করেছে। ১০ টাকা পেয়েছো!")
                except: pass
            
            bot.delete_message(uid, c.message.message_id)
            bot.send_message(uid, "✅ ভেরিফিকেশন সফল! ১০ টাকা বোনাস পেয়েছো মামা।", reply_markup=main_m())
    else:
        bot.answer_callback_query(c.id, "আগে চ্যানেলে জয়েন করো মামা!", show_alert=True)

def check_milestone(rid):
    data = db_q("SELECT ref_count, m_state, bal FROM users WHERE uid=?", (rid,))
    if data:
        count, state, bal = data[0]
        bonus = 0
        new_state = state
        
        if count >= 30 and state < 3:
            bonus, new_state = 400, 3
            msg = "🔥 অভিনন্দন মামা! ৩০টা রেফার পূরণ করায় ৪০০ টাকা এক্সট্রা বোনাস পেয়েছো!"
        elif count >= 20 and state < 2:
            bonus, new_state = 250, 2
            msg = "🚀 অভিনন্দন মামা! ২০টা রেফার পূরণ করায় ২৫০ টাকা এক্সট্রা বোনাস পেয়েছো!"
        elif count >= 10 and state < 1:
            bonus, new_state = 100, 1
            msg = "🌟 অভিনন্দন মামা! ১০টা রেফার পূরণ করায় ১০০ টাকা এক্সট্রা বোনাস পেয়েছো!"
            
        if bonus > 0:
            db_q("UPDATE users SET bal = bal + ?, m_state = ? WHERE uid=?", (bonus, new_state, rid))
            try: bot.send_message(rid, msg)
            except: pass

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    uid = message.chat.id
    if not is_j(uid): return start(message)

    res = db_q("SELECT bal, ref_count FROM users WHERE uid=?", (uid,))
    if not res: return start(message)
    balance, count = res[0]

    if message.text == "💰 ব্যালেন্স":
        bot.send_message(uid, f"আপনার বর্তমান ব্যালেন্স: `{balance} টাকা` \nমোট সফল রেফার: `{count}` জন", parse_mode="Markdown")

    elif message.text == "🎁 রেফার":
        ref_link = f"https://t.me/{(bot.get_me().username)}?start={uid}"
        bot.send_message(uid, f"প্রতি রেফার ১০ টাকা! \n\n🎯 স্পেশাল বোনাস:\n১০ রেফার: ১০০ টাকা\n২০ রেফার: ২৫০ টাকা\n৩০ রেফার: ৪০০ টাকা\n\nলিংক: `{ref_link}`", parse_mode="Markdown")

    elif message.text == "💸 উইথড্র":
        if balance < 1000:
            bot.send_message(uid, f"❌ ১০০০ টাকা হতে আরো {1000-balance} টাকা লাগবে মামা!")
        else:
            bot.send_message(uid, "✅ উইথড্র রিকোয়েস্ট অ্যাডমিনের কাছে পাঠানো হয়েছে।")

    elif message.text == "📊 স্ট্যাটিস্টিকস":
        bot.send_message(uid, "📊 এই ফিচারে কাজ চলছে...")

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))).start()
    bot.infinity_polling()
