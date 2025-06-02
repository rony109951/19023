import json
import random
from datetime import datetime, timedelta

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

TOKEN = "8189292683:AAE53IGPbRVoe5Sc3a5saQGXHzOE-NWxPWY"

DEVELOPER_NAME = "روني البحيره"
DEVELOPER_NUMBER = "01212843252"
BOT_NAME = "جمايكا#1"

POINTS_FILE = "points.json"


def load_points():
    try:
        with open(POINTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_points(data):
    with open(POINTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user_data(user_id):
    points = load_points()
    if str(user_id) not in points:
        points[str(user_id)] = {
            "points": 0,
            "last_daily": None,
            "last_weekly": None,
            "last_spin": None,
        }
        save_points(points)
    return points[str(user_id)]


def update_user_data(user_id, key, value):
    points = load_points()
    user_str = str(user_id)
    if user_str not in points:
        points[user_str] = {
            "points": 0,
            "last_daily": None,
            "last_weekly": None,
            "last_spin": None,
        }
    points[user_str][key] = value
    save_points(points)


def add_points(user_id, amount):
    points = load_points()
    user_str = str(user_id)
    if user_str not in points:
        points[user_str] = {
            "points": 0,
            "last_daily": None,
            "last_weekly": None,
            "last_spin": None,
        }
    points[user_str]["points"] += amount
    save_points(points)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("خدمات التزويد", callback_data= services )],
        [InlineKeyboardButton("تسجيل دخول يومي 🎁", callback_data= daily )],
        [InlineKeyboardButton("عجلة الحظ 🎡", callback_data= spin )],
        [InlineKeyboardButton("تسجيل أسبوعي 📅", callback_data= weekly )],
        [InlineKeyboardButton("شراء نقاط 💰", callback_data= buy_points )],
        [InlineKeyboardButton("تواصل مع المطور 📱", callback_data= contact_dev )],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"👋 أهلاً بيك في بوت {BOT_NAME} 🤖\nالمطور: {DEVELOPER_NAME} 📱\nرقم المطور: {DEVELOPER_NUMBER}\n\nاختر من الأزرار التالية:"
    await update.message.reply_text(text, reply_markup=reply_markup)


async def services_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("تزويد متابعين إنستجرام", callback_data= insta )],
        [InlineKeyboardButton("تزويد مشاهدات تيك توك", callback_data= tiktok )],
        [InlineKeyboardButton("تزويد مشاهدات يوتيوب", callback_data= youtube )],
        [InlineKeyboardButton("تزويد مشاهدات سناب شات", callback_data= snapchat )],
        [InlineKeyboardButton("رجوع 🔙", callback_data= back )],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("اختر الخدمة التي تريدها:", reply_markup=reply_markup)


async def buy_points_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("شراء 1000 نقطة بـ 50 جنيه", callback_data= buy_1000 )],
        [InlineKeyboardButton("شراء 5000 نقطة بـ 200 جنيه", callback_data= buy_5000 )],
        [InlineKeyboardButton("رجوع 🔙", callback_data= back )],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("اختر باقة نقاط للشراء:", reply_markup=reply_markup)


async def contact_dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = f"📱 تواصل مع المطور:\n\n{DEVELOPER_NAME}\nرقم الهاتف: {DEVELOPER_NUMBER}"
    keyboard = [[InlineKeyboardButton("رجوع 🔙", callback_data= back )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def daily_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    now = datetime.now()

    if user_data["last_daily"]:
        last_daily = datetime.fromisoformat(user_data["last_daily"])
        if now - last_daily < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - last_daily)
            hrs, rem = divmod(remaining.seconds, 3600)
            mins, _ = divmod(rem, 60)
            await query.edit_message_text(
                f"⏳ انت استلمت هديتك اليوميه قبل كده\nتعال بعد {hrs} ساعة و {mins} دقيقة."
            )
            return

    add_points(user_id, 200)
    update_user_data(user_id, "last_daily", now.isoformat())
    points = get_user_data(user_id)["points"]
    await query.edit_message_text(f"🎁 تم اضافة 200 نقطة لهدايا اليوم! رصيدك الآن: {points} نقطة.")


async def weekly_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    now = datetime.now()

    if user_data["last_weekly"]:
        last_weekly = datetime.fromisoformat(user_data["last_weekly"])
        if now - last_weekly < timedelta(days=7):
            remaining = timedelta(days=7) - (now - last_weekly)
            days = remaining.days
            hrs, rem = divmod(remaining.seconds, 3600)
            mins, _ = divmod(rem, 60)
            await query.edit_message_text(
                f"⏳ انت استلمت هديتك الاسبوعيه قبل كده\nتعال بعد {days} يوم و {hrs} ساعة و {mins} دقيقة."
            )
            return

    add_points(user_id, 1000)
    update_user_data(user_id, "last_weekly", now.isoformat())
    points = get_user_data(user_id)["points"]
    await query.edit_message_text(f"🎁 تم اضافة 1000 نقطة لهدايا الأسبوع! رصيدك الآن: {points} نقطة.")


async def spin_wheel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    now = datetime.now()

    if user_data["last_spin"]:
        last_spin = datetime.fromisoformat(user_data["last_spin"])
        if now - last_spin < timedelta(hours=1):
            remaining = timedelta(hours=1) - (now - last_spin)
            mins, secs = divmod(remaining.seconds, 60)
            await query.edit_message_text(
                f"⏳ عجلة الحظ متاحة مرة واحدة كل ساعة\nتعال بعد {mins} دقيقة و {secs} ثانية."
            )
            return

    points_won = random.randint(50, 500)
    add_points(user_id, points_won)
    update_user_data(user_id, "last_spin", now.isoformat())
    points = get_user_data(user_id)["points"]
    await query.edit_message_text(
        f"🎡 فزت بـ {points_won} نقطة في عجلة الحظ! رصيدك الآن: {points} نقطة."
    )


async def handle_services_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "insta":
        await query.edit_message_text("✅ طلبك لـ تزويد متابعين إنستجرام تم استلامه.\nسوف يتم التواصل معك قريباً.")
    elif data == "tiktok":
        await query.edit_message_text("✅ طلبك لـ تزويد مشاهدات تيك توك تم استلامه.\nسوف يتم التواصل معك قريباً.")
    elif data == "youtube":
        await query.edit_message_text("✅ طلبك لـ تزويد مشاهدات يوتيوب تم استلامه.\nسوف يتم التواصل معك قريباً.")
    elif data == "snapchat":
        await query.edit_message_text("✅ طلبك لـ تزويد مشاهدات سناب شات تم استلامه.\nسوف يتم التواصل معك قريباً.")
    else:
        await query.edit_message_text("خطأ في اختيار الخدمة!")


async def buy_points_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "buy_1000":
        await query.edit_message_text("💵 طلب شراء 1000 نقطة بقيمة 50 جنيه تم استلامه.\nسيتم التواصل معك قريباً.")
    elif data == "buy_5000":
        await query.edit_message_text("💵 طلب شراء 5000 نقطة بقيمة 200 جنيه تم استلامه.\nسيتم التواصل معك قريباً.")
    else:
        await query.edit_message_text("خطأ في اختيار الباقة!")


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ الأمر غير معروف. استخدم /start للعودة للقائمة الرئيسية.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # أزرار القائمة الرئيسية
    app.add_handler(CallbackQueryHandler(services_menu, pattern="^services$"))
    app.add_handler(CallbackQueryHandler(daily_gift, pattern="^daily$"))
    app.add_handler(CallbackQueryHandler(weekly_gift, pattern="^weekly$"))
    app.add_handler(CallbackQueryHandler(spin_wheel, pattern="^spin$"))
    app.add_handler(CallbackQueryHandler(buy_points_menu, pattern="^buy_points$"))
    app.add_handler(CallbackQueryHandler(contact_dev, pattern="^contact_dev$"))

    # خدمات التزويد
    app.add_handler(CallbackQueryHandler(handle_services_selection, pattern="^(insta|tiktok|youtube|snapchat)$"))

    # شراء نقاط
    app.add_handler(CallbackQueryHandler(buy_points_handler, pattern="^(buy_1000|buy_5000)$"))

    # زر رجوع
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="^back$"))

    # أمر غير معروف
    app.add_handler(CommandHandler(None, unknown_command))

    print(f"🤖 بوت {BOT_NAME} شغال دلوقتي...")
    app.run_polling()


if __name__ == "__main__":
    main()
