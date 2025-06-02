import json
import random
import os
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

BOT_NAME = "جمايكا"
DEVELOPER_NAME = "روني البحيره"
DEVELOPER_PHONE = "01212843252"
POINTS_FILE = "points.json"

# تحميل النقاط أو إنشاء ملف جديد
if os.path.exists(POINTS_FILE):
    with open(POINTS_FILE, "r", encoding="utf-8") as f:
        points_data = json.load(f)
else:
    points_data = {}

def save_points():
    with open(POINTS_FILE, "w", encoding="utf-8") as f:
        json.dump(points_data, f, ensure_ascii=False, indent=2)

def get_user_points(user_id):
    user = points_data.get(str(user_id), {})
    return user.get("points", 0)

def add_user_points(user_id, amount):
    user = points_data.setdefault(str(user_id), {})
    user["points"] = user.get("points", 0) + amount
    save_points()

def set_user_last_daily(user_id, date_str):
    user = points_data.setdefault(str(user_id), {})
    user["last_daily"] = date_str
    save_points()

def get_user_last_daily(user_id):
    user = points_data.get(str(user_id), {})
    return user.get("last_daily", "")

def set_user_last_weekly(user_id, date_str):
    user = points_data.setdefault(str(user_id), {})
    user["last_weekly"] = date_str
    save_points()

def get_user_last_weekly(user_id):
    user = points_data.get(str(user_id), {})
    return user.get("last_weekly", "")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user_points(user.id, 0)  # تأكد وجود المستخدم في البيانات
    text = (
        f"مرحبًا بك في بوت {BOT_NAME} 🌟\n\n"
        f"أنا هنا لأساعدك على تزويد متابعينك وخدمات السوشيال ميديا المختلفة.\n"
        f"يمكنك جمع نقاط يومية، تسجيل أسبوعي، ولعب عجلة الحظ للفوز بالنقاط.\n\n"
        f"استخدم /menu لعرض القائمة الرئيسية."
    )
    await update.message.reply_text(text)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    pts = get_user_points(user.id)
    keyboard = [
        [InlineKeyboardButton(f"🪙 نقاطي: {pts}", callback_data="points_info")],
        [InlineKeyboardButton("🎁 نقاط يومية", callback_data="daily_points")],
        [InlineKeyboardButton("📅 تسجيل أسبوعي", callback_data="weekly_points")],
        [InlineKeyboardButton("🎡 عجلة الحظ", callback_data="wheel")],
        [InlineKeyboardButton("📦 خدمات التزويد", callback_data="services")],
        [InlineKeyboardButton("📞 تواصل مع المطور", callback_data="contact_dev")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"مرحبًا {user.first_name}! اختر من القائمة:", reply_markup=reply_markup)

async def points_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    pts = get_user_points(user.id)
    await query.edit_message_text(f"🎉 لديك {pts} نقطة في حسابك.")

async def daily_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    today_str = datetime.now().strftime("%Y-%m-%d")
    last_daily = get_user_last_daily(user.id)

    if last_daily == today_str:
        await query.edit_message_text("⚠️ لقد استلمت نقاطك اليومية بالفعل اليوم. حاول غدًا.")
        return

    add_user_points(user.id, 200)
    set_user_last_daily(user.id, today_str)
    await query.edit_message_text("✅ تم إضافة 200 نقطة إلى حسابك اليوم. استمتع!")

async def weekly_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    today = datetime.now()
    last_weekly_str = get_user_last_weekly(user.id)
    if last_weekly_str:
        last_weekly = datetime.strptime(last_weekly_str, "%Y-%m-%d")
        if (today - last_weekly).days < 7:
            await query.edit_message_text("⚠️ يمكنك الحصول على تسجيل الأسبوعي مرة واحدة في كل 7 أيام فقط.")
            return

    add_user_points(user.id, 1000)
    set_user_last_weekly(user.id, today.strftime("%Y-%m-%d"))
    await query.edit_message_text("✅ تم إضافة 1000 نقطة كتسجيل أسبوعي. مبروك!")

async def wheel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    points_won = random.randint(50, 500)
    add_user_points(query.from_user.id, points_won)
    await query.edit_message_text(f"🎡 لقد ربحت {points_won} نقطة من عجلة الحظ! مبروك 🎉")

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("متابعين انستقرام - 500 نقطة", callback_data="service_followers")],
        [InlineKeyboardButton("لايكات انستقرام - 300 نقطة", callback_data="service_likes")],
        [InlineKeyboardButton("مشاهدات تيك توك - 400 نقطة", callback_data="service_views")],
        [InlineKeyboardButton("رجوع 🔙", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("اختر الخدمة التي تريد شراءها:", reply_markup=reply_markup)

async def buy_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    pts = get_user_points(user.id)

    service_costs = {
        "service_followers": 500,
        "service_likes": 300,
        "service_views": 400,
    }
    service_names = {
        "service_followers": "متابعين انستقرام",
        "service_likes": "لايكات انستقرام",
        "service_views": "مشاهدات تيك توك",
    }

    service_key = query.data
    cost = service_costs.get(service_key, 0)
    service_name = service_names.get(service_key, "الخدمة")

    if pts < cost:
        await query.edit_message_text(f"⚠️ نقاطك الحالية ({pts}) غير كافية لشراء {service_name} التي تكلف {cost} نقطة.")
        return

    # خصم النقاط
    points_data[str(user.id)]["points"] -= cost
    save_points()

    # رسالة نجاح وابلاغ المطور
    await query.edit_message_text(f"✅ تم شراء خدمة {service_name} بنجاح! تم خصم {cost} نقطة من حسابك.")

    # ابلاغ المطور
    context.bot.send_message(
        chat_id=user.id,  # ممكن تستبدلها برقم المطور اذا عندك
        text=(
            f"📢 طلب جديد لخدمة {service_name}\n"
            f"من المستخدم: {user.first_name} (ID: {user.id})\n"
            f"النقاط المستخدمة: {cost}\n"
            f"للتواصل: @{user.username if user.username else  لا يوجد }"
        ),
    )

async def contact_dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        f"📞 للتواصل مع المطور {DEVELOPER_NAME}:\n"
        f"رقم الهاتف: {DEVELOPER_PHONE}\n\n"
        f"يمكنك مراسلته مباشرة عبر التليجرام أو الواتساب."
    )
    keyboard = [[InlineKeyboardButton("رجوع 🔙", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "menu":
        await menu(update, context)
    elif data == "points_info":
        await points_info(update, context)
    elif data == "daily_points":
        await daily_points(update, context)
    elif data == "weekly_points":
        await weekly_points(update, context)
    elif data == "wheel":
        await wheel(update, context)
    elif data.startswith("service_"):
        await buy_service(update, context)
    elif data == "services":
        await services(update, context)
    elif data == "contact_dev":
        await contact_dev(update, context)
    else:
        await query.answer("خطأ في الاختيار", show_alert=True)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ أمر غير معروف. استخدم /menu لعرض القائمة الرئيسية.")

def main():
    import logging
    logging.basicConfig(
        format= %(asctime)s - %(name)s - %(levelname)s - %(message)s , level=logging.INFO
    )

    TOKEN = "
8189292683:AAE53IGPbRVoe5Sc3a5saQGXHzOE-NWxPWY"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print(f"🤖 بوت {BOT_NAME} شغال دلوقتي...")

    app.run_polling()

if __name__ == "__main__":
    main()
