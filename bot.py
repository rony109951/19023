import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
import random
from datetime import datetime, timedelta

# إعدادات اللوج
logging.basicConfig(level=logging.INFO)

# قاعدة بيانات مؤقتة في الذاكرة
users_data = {}

# اسم المطور والبوت
BOT_NAME = "جمايكا#1"
DEVELOPER_NAME = "روني البحيره"
DEVELOPER_PHONE = "01212843252"

# دالة لتهيئة بيانات المستخدم
def get_user_data(user_id):
    if user_id not in users_data:
        users_data[user_id] = {
            "points": 0,
            "last_daily": None,
            "last_weekly": None
        }
    return users_data[user_id]

# رسالة الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎁 هديتي اليومية", callback_data="daily")],
        [InlineKeyboardButton("🎡 عجلة الحظ", callback_data="wheel")],
        [InlineKeyboardButton("📅 تسجيل أسبوعي", callback_data="weekly")],
        [InlineKeyboardButton("🛒 الخدمات بالنقاط", callback_data="services")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"أهلاً بيك في بوت {BOT_NAME} 🤖\n"
        f"المطور: {DEVELOPER_NAME} 📱\n"
        f"رقم المطور: {DEVELOPER_PHONE}\n\n"
        "اختر من الأزرار التالية:",
        reply_markup=reply_markup
    )

# هدية يومية
async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user_data(user_id)

    now = datetime.now()
    if user["last_daily"] and now - user["last_daily"] < timedelta(days=1):
        await query.answer("😅 خدت هديتك اليومية النهاردة، تعالى بكرة!")
        return

    user["last_daily"] = now
    user["points"] += 200
    await query.answer("🎁 تم إضافة 200 نقطة لحسابك!")
    await query.edit_message_text("✅ استلمت هديتك اليومية! 🎉")

# تسجيل أسبوعي
async def weekly_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user_data(user_id)

    now = datetime.now()
    if user["last_weekly"] and now - user["last_weekly"] < timedelta(days=7):
        await query.answer("😅 انت مسجل الاسبوع ده بالفعل.")
        return

    user["last_weekly"] = now
    user["points"] += 1000
    await query.answer("🎊 تم إضافة 1000 نقطة لحسابك!")
    await query.edit_message_text("✅ تم تسجيلك الأسبوعي بنجاح! 🔥")

# عجلة الحظ
async def spin_wheel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user_data(user_id)

    reward = random.choice([50, 100, 150, 200, 300, 500])
    user["points"] += reward
    await query.answer(f"🎡 فزت بـ {reward} نقطة!")
    await query.edit_message_text(f"✅ عجلة الحظ دارت! وكسبت {reward} نقطة 🤑")

# عرض الخدمات
async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("💎 خدمة VIP - 1000 نقطة", callback_data="buy_vip")],
        [InlineKeyboardButton("📸 تصميم لوجو - 500 نقطة", callback_data="buy_logo")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="home")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🛒 *قائمة الخدمات بالنقاط:*\n"
        "اختر الخدمة اللي محتاجها، وسيتم التحقق منك ✨",
        parse_mode="Markdown",
        reply_markup=markup
    )

# الرجوع للصفحة الرئيسية
async def back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🎁 هديتي اليومية", callback_data="daily")],
        [InlineKeyboardButton("🎡 عجلة الحظ", callback_data="wheel")],
        [InlineKeyboardButton("📅 تسجيل أسبوعي", callback_data="weekly")],
        [InlineKeyboardButton("🛒 الخدمات بالنقاط", callback_data="services")]
    ]
    await query.edit_message_text(
        f"✅ رجعت للصفحة الرئيسية لـ {BOT_NAME} 🤖",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# طلب خدمة VIP
async def buy_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user_data(user_id)

    if user["points"] < 1000:
        await query.answer("❌ نقاطك مش كفاية!")
        return

    user["points"] -= 1000
    await query.edit_message_text("✅ تم طلب خدمة VIP بنجاح، جاري التحقق من الطلب ✅")

# طلب لوجو
async def buy_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user_data(user_id)

    if user["points"] < 500:
        await query.answer("❌ نقاطك غير كافية!")
        return

    user["points"] -= 500
    await query.edit_message_text("✅ تم طلب تصميم اللوجو بنجاح، سيتم التواصل معك 🎨")

# توزيع الردود بناءً على الكول باك
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    handlers = {
        "daily": daily_reward,
        "weekly": weekly_reward,
        "wheel": spin_wheel,
        "services": show_services,
        "home": back_home,
        "buy_vip": buy_vip,
        "buy_logo": buy_logo,
    }
    if data in handlers:
        await handlers[data](update, context)

# تشغيل البوت
if __name__ == "__main__":
    import os
    TOKEN = "8189292683:AAE53IGPbRVoe5Sc3a5saQGXHzOE-NWxPWY"  # ← غيّر دي بالتوكن بتاعك

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    print(f"🤖 بوت {BOT_NAME} شغال دلوقتي...")
    app.run_polling()
