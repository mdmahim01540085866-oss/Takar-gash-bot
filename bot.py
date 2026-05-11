import telebot
import sqlite3
from flask import Flask
from threading import Thread
import os

# --- à¦•à¦¨à¦«à¦¿à¦—à¦¾à¦°à§‡à¦¶à¦¨ ---
TOKEN = '8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY'
CHANNEL_ID = '-1003351496871' 
CHANNEL_LINK = 'https://t.me/+fWQHyEKJepA2Njll'
ADMIN_ID = 6871732560 

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask('')

@app.route('/')
def home():
    return "à¦¬à¦Ÿ à¦¸à¦šà¦² à¦†à¦›à§‡ à¦®à¦¾à¦®à¦¾!"

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

# à¦®à¦¾à¦®à¦¾, à¦à¦‡ à¦«à¦¾à¦‚à¦¶à¦¨à¦Ÿà¦¾à¦‡ à¦†à¦¸à¦² à¦šà§‡à¦• à¦•à¦°à§‡
def is_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("ðŸ’° à¦¬à§à¦¯à¦¾à¦²à§‡à¦¨à§à¦¸", "ðŸ‘¥ à¦°à§‡à¦«à¦¾à¦°")
    markup.row("ðŸ’³ à¦‰à¦‡à¦¥à¦¡à§à¦°", "ðŸ“Š à¦¸à§à¦Ÿà§à¦¯à¦¾à¦Ÿà¦¿à¦¸à§à¦Ÿà¦¿à¦•à§à¦¸")
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
        cursor.execute("INSERT INTO users (user_id, balance, referred_by, joined) VALUES (?, 0, ?, 0)", (user_id, ref_id))
        conn.commit()
    conn.close()

    # à¦¯à¦¦à¦¿ à¦œà§Ÿà§‡à¦¨ à¦¨à¦¾ à¦¥à¦¾à¦•à§‡, à¦¤à¦¬à§‡ à¦¸à¦°à¦¾à¦¸à¦°à¦¿ à¦œà§Ÿà§‡à¦¨ à¦¬à¦¾à¦Ÿà¦¨ à¦¦à§‡à¦–à¦¾à¦¬à§‡
    if not is_joined(user_id):
        m = telebot.types.InlineKeyboardMarkup()
        m.add(telebot.types.InlineKeyboardButton("à¦šà§à¦¯à¦¾à¦¨à§‡à¦²à§‡ à¦œà§Ÿà§‡à¦¨ à¦•à¦°à§à¦¨ ðŸ“¢", url=CHANNEL_LINK))
        m.add(telebot.types.InlineKeyboardButton("à¦­à§‡à¦°à¦¿à¦«à¦¾à¦‡ à¦•à¦°à§à¦¨ âœ…", callback_data="verify"))
        bot.send_message(user_id, "à¦®à¦¾à¦®à¦¾, à¦šà§à¦¯à¦¾à¦¨à§‡à¦²à§‡ à¦œà§Ÿà§‡à¦¨ à¦¨à¦¾ à¦•à¦°à¦²à§‡ à¦Ÿà¦¾à¦•à¦¾ à¦‡à¦¨à¦•à¦¾à¦® à¦•à¦°à¦¾ à¦¯à¦¾à¦¬à§‡ à¦¨à¦¾! à¦†à¦—à§‡ à¦œà§Ÿà§‡à¦¨ à¦•à¦°à§‡ à¦­à§‡à¦°à¦¿à¦«à¦¾à¦‡ à¦•à¦°à¥¤", reply_markup=m)
    else:
        bot.send_message(user_id, "à¦¸à§à¦¬à¦¾à¦—à¦¤à¦® à¦®à¦¾à¦®à¦¾! à¦¤à§à¦®à¦¿ à¦…à¦²à¦°à§‡à¦¡à¦¿ à¦œà§Ÿà§‡à¦¨ à¦†à¦›à§‹à¥¤", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    user_id = call.from_user.id
    if is_joined(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT referred_by, joined FROM users WHERE user_id=?", (user_id,))
        res = cursor.fetchone()
        if res and res[1] == 0:
            rid = res[0]
            if rid and int(rid) != user_id:
                cursor.execute("UPDATE users SET balance = balance + 10 WHERE user_id=?", (rid,))
                conn.commit()
                try: bot.send_message(rid, "ðŸŽ‰ à¦®à¦¾à¦®à¦¾! à§§ à¦œà¦¨ à¦¸à¦«à¦²à¦­à¦¾à¦¬à§‡ à¦œà§Ÿà§‡à¦¨ à¦•à¦°à§‡à¦›à§‡à¥¤ à§§à§¦ à¦Ÿà¦¾à¦•à¦¾ à¦¬à§‹à¦¨à¦¾à¦¸ à¦ªà§‡à§Ÿà§‡à¦›à§‹!")
                except: pass
            cursor.execute("UPDATE users SET joined = 1 WHERE user_id=?", (user_id,))
            conn.commit()
        conn.close()
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "à¦­à§‡à¦°à¦¿à¦«à¦¿à¦•à§‡à¦¶à¦¨ à¦¸à¦«à¦² à¦®à¦¾à¦®à¦¾!", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "à¦†à¦—à§‡ à¦œà§Ÿà§‡à¦¨ à¦¤à§‹ à¦•à¦° à¦®à¦¾à¦®à¦¾!", show_alert=True)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.chat.id
    # à¦¯à¦¦à¦¿ à¦•à§‡à¦‰ à¦œà§Ÿà§‡à¦¨ à¦¨à¦¾ à¦•à¦°à§‡ à¦¬à¦¾à¦Ÿà¦¨ à¦šà¦¾à¦ªà§‡, à¦¤à¦¾à¦•à§‡ à¦†à¦¬à¦¾à¦° à¦œà§Ÿà§‡à¦¨ à¦•à¦°à¦¤à§‡ à¦¬à¦²à¦¬à§‡
    if not is_joined(user_id):
        return start(message)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    balance = res[0] if res else 0

    if message.text == "ðŸ’° à¦¬à§à¦¯à¦¾à¦²à§‡à¦¨à§à¦¸":
        bot.send_message(user_id, f"à¦¤à§‹à¦° à¦¬à¦°à§à¦¤à¦®à¦¾à¦¨ à¦¬à§à¦¯à¦¾à¦²à§‡à¦¨à§à¦¸: {balance} à¦Ÿà¦¾à¦•à¦¾à¥¤")
    elif message.text == "ðŸ‘¥ à¦°à§‡à¦«à¦¾à¦°":
        bot_user = bot.get_me().username
        bot.send_message(user_id, f"à¦²à¦¿à¦‚à¦•: https://t.me/{bot_user}?start={user_id}")
    elif message.text == "ðŸ“Š à¦¸à§à¦Ÿà§à¦¯à¦¾à¦Ÿà¦¿à¦¸à§à¦Ÿà¦¿à¦•à§à¦¸":
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        bot.send_message(user_id, f"ðŸ“Š à¦®à§‹à¦Ÿ à¦‡à¦‰à¦œà¦¾à¦°: {total} à¦œà¦¨à¥¤")
    elif message.text == "ðŸ’³ à¦‰à¦‡à¦¥à¦¡à§à¦°":
        if balance < 1000:
            bot.send_message(user_id, "à¦†à¦—à§‡ à§§à§¦à§¦à§¦ à¦ªà§à¦°à¦¾ à¦•à¦°à§‹ à¦®à¦¾à¦®à¦¾! à¦¬à§à¦¯à¦¾à¦²à§‡à¦¨à§à¦¸ à¦¨à¦¾à¦‡à¥¤")
        else:
            bot.send_message(user_id, "à¦®à¦¾à¦®à¦¾, à§§à§¦à§¦à§¦ à¦Ÿà¦¾à¦•à¦¾ à¦¹à§Ÿà§‡ à¦—à§‡à¦›à§‡! à¦¤à§‹à¦®à¦¾à¦° à¦¨à¦¾à¦®à§à¦¬à¦¾à¦° à¦²à¦¿à¦–à§‡ à¦¦à¦¾à¦“à¥¤")
    conn.close()

if __name__ == "__main__":
    init_db()
    Thread(target=run_flask).start()
    bot.infinity_polling()
