import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# --- সেটিংস ---
TOKEN = "8723569797:AAHn_66bEU7fBZwN2G-mUVgJUrIzsT2ZftY" 
YT_LINK = "https://www.youtube.com/@nexusopti"  # তোর ইউটিউব চ্যানেল লিঙ্ক এখানে সেট করে দিয়েছি
MIN_WITHDRAW = 500
REFER_BONUS = 10

# ইউজার ডাটা স্টোর করার ডিকশনারি
users = {}

# স্টার্ট কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    
    # নতুন ইউজার রেজিস্ট্রেশন
    if user_id not in users:
        referrer_id = None
        if context.args:
            try:
                referrer_id = int(context.args[0])
            except: pass
        
        users[user_id] = {'bal': 0, 'ref_by': referrer_id, 'verified': False}

    # ভেরিফিকেশন স্ক্রিন
    if not users[user_id]['verified']:
        keyboard = [
            [InlineKeyboardButton("📺 ইউটিউব চ্যানেল ওপেন করুন", url=YT_LINK)],
            [InlineKeyboardButton("✅ ভেরিফাই করুন", callback_data='verify_click')]
        ]
        await update.message.reply_text(
            f"হ্যালো {first_name}!\n\nবটটি চালু করতে প্রথমে উপরের বাটনে ক্লিক করে আমাদের ইউটিউব চ্যানেলটি ওপেন করুন, তারপর এসে '✅ ভেরিফাই করুন' বাটনে চাপ দিন।",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await show_main_menu(update, context, user_id, first_name)

# মেইন ব্যালেন্স ও রেফার মেনু
async def show_main_menu(update, context, user_id, first_name):
    bot_info = await context.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    msg = (f"স্বাগতম {first_name}!\n\n"
           f"💰 বর্তমান ব্যালেন্স: {users[user_id]['bal']} টাকা\n"
           f"👥 প্রতি রেফার বোনাস: {REFER_BONUS} টাকা\n"
           f"💳 সর্বনিম্ন উইথড্র: {MIN_WITHDRAW} টাকা\n\n"
           f"🔗 আপনার রেফার লিঙ্ক:\n{ref_link}")
    
    keyboard = [
        [InlineKeyboardButton("📊 ব্যালেন্স চেক", callback_data='st')],
        [InlineKeyboardButton("💸 উইথড্র করুন", callback_data='wd')]
    ]
    
    if update.message:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

# বাটন অ্যাকশন হ্যান্ডলার
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    first_name = query.from_user.first_name
    bal = users.get(user_id, {}).get('bal', 0)

    # ইউজার ভেরিফাই বাটনে চাপ দিলে
    if query.data == 'verify_click':
        if not users[user_id]['verified']:
            users[user_id]['verified'] = True
            await query.answer("✅ ভেরিফিকেশন সফল হয়েছে!", show_alert=True)
            await query.message.delete() # ভেরিফাই মেসেজ ডিলিট করবে
            
            # রেফারারকে ১০ টাকা বোনাস দেওয়া
            referrer_id = users[user_id]['ref_by']
            if referrer_id and referrer_id in users and referrer_id != user_id:
                users[referrer_id]['bal'] += REFER_BONUS
                try:
                    await context.bot.send_message(
                        referrer_id, 
                        f"✅ অভিনন্দন! আপনার রেফারে একজন নতুন মেম্বার জয়েন করেছে।\nআপনি {REFER_BONUS} টাকা বোনাস পেয়েছেন।"
                    )
                except: pass
            
            await show_main_menu(update, context, user_id, first_name)
    
    elif query.data == 'st':
        await query.answer()
        await query.message.reply_text(f"আপনার বর্তমান ব্যালেন্স: {bal} টাকা।")
    
    elif query.data == 'wd':
        await query.answer()
        if bal >= MIN_WITHDRAW:
            await query.message.reply_text("অভিনন্দন! আপনার ব্যালেন্স ১০০০ টাকা পূর্ণ হয়েছে। পেমেন্ট নিতে আপনার বিকাশ/নগদ নম্বরটি এডমিনকে মেসেজ করুন।")
        else:
            await query.message.reply_text(f"দুঃখিত! উইথড্রর জন্য আরও {MIN_WITHDRAW - bal} টাকা প্রয়োজন।")

if __name__ == '__main__':
    print("NexusOpti ইউটিউব ক্লিক ভেরিফিকেশন বট সফলভাবে চালু হয়েছে...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()
