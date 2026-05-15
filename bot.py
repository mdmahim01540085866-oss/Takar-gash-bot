#-*- coding: utf-8 -*-
import telebot
import sqlite3
import time
import os
from flask import Flask
from threading import Thread

# --- কনফিগারেশন ---
TOKEN = '8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY'
CH_ID = -1003842595357
CH_LINK = 'https://t.me/Bezznxt'
ADMIN = 6871732560

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

def get_db():
    conn = sqlite3.connect('refer_data.db', timeout=20)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                    (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, 
                     referred_by INTEGER, joined_status INTEGER DEFAULT 0,
                     total_ref INTEGER DEFAULT 0, task_state INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def is_joined(user_id):
    try:
        member = bot.get_chat_member(CH_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

def main_menu():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("💰 ব্যালেন্স", "🎁 রেফার")
    keyboard.row("📝 টাস্ক", "💸 উইথড্র")
    keyboard.row("📊 স্ট্যাটিস্টিকস")
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    init_db()
    
    command_args = message.text.split()
    referrer = command_args[1] if len(command_args) > 1 else None
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute("INSERT INTO users (user_id, balance, referred_by, joined_status, total_ref, task_state) VALUES (?, 0, ?, 0, 0, 0)", 
                       (user_id, referrer))
        conn.commit()
    conn.close()
    
    if not is_joined(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        join_btn = telebot.types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=CH_LINK)
        verify_btn = telebot.types.InlineKeyboardButton("ভেরিফাই করুন ✅", callback_data="verify_join")
        markup.add(join_btn)
        markup.add(verify_btn)
        bot.send_message(user_id, "স্বাগতম মামা! ১০ টাকা বোনাস পেতে আগে আমাদের চ্যানেলে জয়েন করো, তারপর ভেরিফাই বাটনে ক্লিক করো।", reply_markup=markup)
    else:
        bot.send_message(user_id, "মামা, তোমার একাউন্ট অলরেডি ভেরিফাইড আছে!", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_callback(call):
    user_id = call.from_user.id
    if is_joined(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT referred_by, joined_status FROM users WHERE user_id=?", (user_id,))
        res = cursor.fetchone()
        
        if res and res[1] == 0:
            referrer_id = res[0]
            # ইউজারের ১০ টাকা বোনাস
            cursor.execute("UPDATE users SET balance = balance + 10, joined_status = 1 WHERE user_id=?", (user_id,))
            
            # রেফারারের ১০ টাকা বোনাস ও কাউন্ট আপডেট
            if referrer_id and int(referrer_id) != user_id:
                cursor.execute("UPDATE users SET balance = balance + 10, total_ref = total_ref + 1 WHERE user_id=?", (referrer_id,))
                try:
                    bot.send_message(referrer_id, "🎉 মামা! তোমার রেফার লিংকে একজন সফলভাবে জয়েন করেছে। ১০ টাকা বোনাস পেয়েছো!")
                except:
                    pass
            
            conn.commit()
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, "✅ ভেরিফিকেশন সফল! ১০ টাকা বোনাস তোমার ব্যালেন্সে যোগ হয়েছে মামা।", reply_markup=main_menu())
        else:
            bot.answer_callback_query(call.id, "মামা, তুমি তো অলরেডি বোনাস নিয়েছো!", show_alert=True)
        conn.close()
    else:
        bot.answer_callback_query(call.id, "মামা, আগে তো চ্যানেলে জয়েন করতে হবে!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.chat.id
    if not is_joined(user_id):
        return start(message)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, total_ref, task_state FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    conn.close()

    if not data:
        return start(message)

    balance, total_ref, task_state = data

    if message.text == "💰 ব্যালেন্স":
        bot.send_message(user_id, f"আপনার বর্তমান ব্যালেন্স: `{balance} টাকা` \nমোট রেফার: `{total_ref}` জন", parse_mode="Markdown")

    elif message.text == "🎁 রেফার":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        bot.send_message(user_id, f"প্রতি রেফার এ পান ১০ টাকা!\nআপনার রেফার লিংক:\n`{ref_link}`", parse_mode="Markdown")

    elif message.text == "📝 টাস্ক":
        task_msg = f"🎯 **রেফার মাইলস্টোন টাস্ক**\n\n"
        task_msg += f"১. ১০ রেফার: ১২০ টাকা বোনাস {'✅' if task_state >= 1 else '❌'}\n"
        task_msg += f"২. ২০ রেফার: ২৫০ টাকা বোনাস {'✅' if task_state >= 2 else '❌'}\n"
        task_msg += f"৩. ৪০ রেফার: ৫০০ টাকা বোনাস {'✅' if task_state >= 3 else '❌'}\n\n"
        task_msg += f"মোট রেফার: `{total_ref}` জন।"
        
        kb = telebot.types.InlineKeyboardMarkup()
        if total_ref >= 10 and task_state == 0:
            kb.add(telebot.types.InlineKeyboardButton("১০ রেফার বোনাস (১২০ টাকা) ক্লেইম করুন 🎁", callback_data="get_1"))
        if total_ref >= 20 and task_state == 1:
            kb.add(telebot.types.InlineKeyboardButton("২০ রেফার বোনাস (২৫০ টাকা) ক্লেইম করুন 🎁", callback_data="get_2"))
        if total_ref >= 40 and task_state == 2:
            kb.add(telebot.types.InlineKeyboardButton("৪০ রেফার বোনাস (৫০০ টাকা) ক্লেইম করুন 🎁", callback_data="get_3"))
        
        bot.send_message(user_id, task_msg, reply_markup=kb, parse_mode="Markdown")

    elif message.text == "💸 উইথড্র":
        if balance < 1000:
            bot.send_message(user_id, f"❌ আগে ১০০০ টাকা পুরা করো মামা! আপনার আছে {balance} টাকা।")
        else:
            bot.send_message(user_id, "✅ আপনার উইথড্র রিকোয়েস্টটি প্রসেসিংয়ে আছে। অ্যাডমিন শীঘ্রই যোগাযোগ করবে।")

    elif message.text == "📊 স্ট্যাটিস্টিকস":
        bot.send_message(user_id, "📊 এই ফিচারে কাজ চলছে...")

@bot.callback_query_handler(func=lambda call: call.data.startswith('get_'))
def get_bonus(call):
    user_id = call.from_user.id
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT total_ref, task_state FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    
    ref_cnt, state = res
    bonus = 0
    new_state = state
    
    if call.data == "get_1" and ref_cnt >= 10 and state == 0:
        bonus, new_state = 120, 1
    elif call.data == "get_2" and ref_cnt >= 20 and state == 1:
        bonus, new_state = 250, 2
    elif call.data == "get_3" and ref_cnt >= 40 and state == 2:
        bonus, new_state = 500, 3
        
    if bonus > 0:
        cursor.execute("UPDATE users SET balance = balance + ?, task_state = ? WHERE user_id=?", (bonus, new_state, user_id))
        conn.commit()
        bot.answer_callback_query(call.id, f"অভিনন্দন! {bonus} টাকা বোনাস পেয়েছো মামা।", show_alert=True)
        bot.edit_message_text(f"✅ আপনি সফলভাবে {bonus} টাকা মাইলস্টোন বোনাস নিয়েছেন!", user_id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "মামা, তুমি এই বোনাস নেওয়ার যোগ্য নও!", show_alert=True)
    conn.close()

if __name__ == "__main__":
    init_db()
    Thread(target=run).start()
    bot.infinity_polling()
