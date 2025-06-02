import json
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

POINTS_FILE = "points.json"

# خدمات السوشيال وأسعارها بالنقاط
SOCIAL_SERVICES = {
    "متابعين": 1000,
    "لايكات": 500,
    "مشاهدات": 300,
    "تعليقات": 800,
}

WELCOME_IMAGE = "welcome.jpg"  # صورة ترحيب

# تحميل نقاط المستخدمين من الملف
def load_points():
    try:
        with open(POINTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# حفظ النقاط في الملف
def save_points(data):
    with open(POINTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# إضافة نقاط لمستخدم
def add_points(user_id, amount):
    points = load_points()
    user_id = str(user_id)
    if user_id not in points:
        points[user_id] = {"points": 0, "last_daily": None, "last_weekly": None}
    points[user_id]["points"] += amount
    save_points(points)

# الحصول على نقاط المستخدم
def get_user_points(user_id):
    points = load_points()
    user_id = str(user_id)
    if user_id in points:
        return points[user_id]["points"]
    return 0

# تحديث توقيت الهدايا اليومية والأسبوعية
def update_user_time(user_id, key):
    points = load_points()
    user_id = str(user_id)
    if user_id not in points:
        points[user_id] = {"points": 0, "last_daily": None, "last_weekly": None}
    points[user_id][key] = datetime.utcnow().isoformat()
    save_points(points)

# التحقق من صلاحية الهدايا اليومية والأسبوعية
def can_claim(user_id, key, interval_hours):
    points = load_points()
    user_id = str(user_id)
    if user_id not in points or points[user_id][key] is None:
        return True
    last_time = datetime.fromisoformat(points[user_id][key])
    return datetime.utcnow() - last_time > timedelta(hours=interval_hours)

# أمر /start - ترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"أهلاً بك {user.first_name} في بوت جمايكا#1 🌟\n"
        f"مرحباً بك في بوت خدمات السوشيال ميديا مع نظام النقاط.\n\n"
        f"لديك الآن {get_user_points(user.id)} نقطة.\n"
        "استخدم /help لمعرفة الأوامر."
    )
    await update.message.reply_photo(
        photo=open(WELCOME_IMAGE, "rb"),
        caption=welcome_text,
    )

# أمر /help - قائمة الأوامر
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "قائمة الأوامر:\n"
        "/start - بداية التشغيل\n"
        "/help - قائمة الأوامر\n"
        "/points - عرض نقاطك الحالية\n"
        "/daily - استلام هدية يومية (200 نقطة)\n"
        "/weekly - استلام هدية أسبوعية (1000 نقطة)\n"
        "/spin - عجلة الحظ (من 50 إلى 500 نقطة)\n"
        "/services - عرض خدمات التزويد\n"
        "/buy <الخدمة> - شراء خدمة (مثال: /buy متابعين)\n"
    )
    await update.message.reply_text(help_text)

# أمر /points - عرض نقاط المستخدم
async def points_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    pts = get_user_points(user.id)
    await update.message.reply_text(f"لديك {pts} نقطة 🎉")

# أمر /daily - هدية يومية
async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if can_claim(user.id, "last_daily", 24):
        add_points(user.id, 200)
        update_user_time(user.id, "last_daily")
        await update.message.reply_text("🎁 استلمت هديتك اليومية 200 نقطة! استمتع.")
    else:
        await update.message.reply_text("⏰ لقد استلمت هديتك اليوم بالفعل. جرب غداً!")

# أمر /weekly - هدية أسبوعية
async def weekly_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if can_claim(user.id, "last_weekly", 168):  # 168 ساعة = 7 أيام
        add_points(user.id, 1000)
        update_user_time(user.id, "last_weekly")
        await update.message.reply_text("🎁 استلمت هديتك الأسبوعية 1000 نقطة! أحسنت.")
    else:
        await update.message.reply_text("⏰ لقد استلمت هديتك الأسبوعية بالفعل. انتظر الأسبوع القادم!")

# أمر /spin - عجلة الحظ
async def spin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    points_won = random.randint(50, 500)
    add_points(user.id, points_won)
    await update.message.reply_text(f"🎡 عجلة الحظ أوقفت عند: {points_won} نقطة! مبروك!")

# أمر /services - عرض خدمات التزويد
async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "💼 خدمات التزويد المتاحة:\n"
    for service, price in SOCIAL_SERVICES.items():
        text += f"• {service} - {price} نقطة\n"
    text += "\nلشراء خدمة، اكتب: /buy اسم_الخدمة"
    await update.message.reply_text(text)

# أمر /buy - شراء خدمة
async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    if not args:
        await update.message.reply_text("❗️ من فضلك اكتب اسم الخدمة بعد الأمر.\nمثال: /buy متابعين")
        return

    service_name = args[0]
    if service_name not in SOCIAL_SERVICES:
        await update.message.reply_text("❌ الخدمة غير موجودة. استخدم /services لمعرفة الخدمات المتاحة.")
        return

    price = SOCIAL_SERVICES[service_name]
    user_points = get_user_points(user.id)
    if user_points < price:
        await update.message.reply_text(f"❌ نقاطك غير كافية. تحتاج {price} نقطة، ولديك {user_points} نقطة فقط.")
        return

    # خصم النقاط وإتمام العملية (هنا يمكنك إضافة تنفيذ الخدمة الحقيقية)
    points = load_points()
    points[str(user.id)]["points"] -= price
    save_points(points)

    await update.message.reply_text(
        f"✅ تم شراء خدمة {service_name} مقابل {price} نقطة.\n"
        "سيتم تنفيذ طلبك قريباً. شكراً لاستخدامك بوت جمايكا#1! ❤️"
    )

async def main():
    TOKEN = "8189292683:AAE53IGPbRVoe5Sc3a5saQGXHzOE-NWxPWY"  # استبدل بالتوكن الحقيقي

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("points", points_command))
    app.add_handler(CommandHandler("daily", daily_command))
    app.add_handler(CommandHandler("weekly", weekly_command))
    app.add_handler(CommandHandler("spin", spin_command))
    app.add_handler(CommandHandler("services", services_command))
    app.add_handler(CommandHandler("buy", buy_command))

    print("🤖 بوت جمايكا#1 شغال دلوقتي...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
