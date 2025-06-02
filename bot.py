import logging
import json
import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, JobQueue

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_NAME = "جمايكا#1"
DEVELOPER = "روني البحيره"
DEV_USERNAME = "@VlP_l1"
DEV_PHONE = "01212843252"
WELCOME_PHOTO_URL = "https://i.imgur.com/your_image.jpg"  # غير الرابط لصورة ترحيب حقيقية

DATA_FILE = "points_data.json"

# خدمات مع النقاط والإيموجي
services = {
    "متابعين انستجرام 👥": 150,
    "لايكات انستجرام ❤️": 100,
    "تعليقات انستجرام 💬": 120,
    "مشاهدات انستجرام 👁️": 80,
    "لايكات ريلز انستجرام 🎬": 110,
    "مشاهدات ريلز انستجرام 📽️": 90,
    "تفاعل استوري انستجرام 📊": 95,
    "متابعين تيك توك 🎵": 160,
    "لايكات تيك توك 🔥": 110,
    "مشاهدات تيك توك 📺": 90,
    "أعضاء تيليجرام 📢": 200,
    "مشاهدات تيليجرام 👀": 85,
    "تعليقات فيسبوك 🗯️": 100,
    "لايكات فيسبوك 👍": 95,
    "شرا نقاط تواصل مع المطور 💎": 1000
}

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# نستخدم ملف JSON لتخزين نقاط المستخدمين وتواريخ الهدايا
points_data = load_data()

def get_user(user_id):
    if str(user_id) not in points_data:
        points_data[str(user_id)] = {
            "points": 0,
            "last_daily": None,
            "last_weekly": None
        }
        save_data(points_data)
    return points_data[str(user_id)]

def add_points(user_id, amount):
    user = get_user(user_id)
    user["points"] += amount
    save_data(points_data)

def can_get_daily(user_id):
    user = get_user(user_id)
    if user["last_daily"] is None:
        return True
    last = datetime.datetime.fromisoformat(user["last_daily"])
    now = datetime.datetime.now()
    return (now - last).days >= 1

def can_get_weekly(user_id):
    user = get_user(user_id)
    if user["last_weekly"] is None:
        return True
    last = datetime.datetime.fromisoformat(user["last_weekly"])
    now = datetime.datetime.now()
    return (now - last).days >= 7

def set_daily(user_id):
    user = get_user(user_id)
    user["last_daily"] = datetime.datetime.now().isoformat()
    save_data(points_data)

def set_weekly(user_id):
    user = get_user(user_id)
    user["last_weekly"] = datetime.datetime.now().isoformat()
    save_data(points_data)

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    # إعطاء نقاط هدية يومية تلقائياً إذا ممكن
    if can_get_daily(user_id):
        add_points(user_id, 200)
        set_daily(user_id)
    
    user = get_user(user_id)
    points = user["points"]

    welcome_text = f"""
🎉 أهلاً بك في بوت {BOT_NAME}!

👤 المطور: {DEVELOPER}
📱 تواصل مع المطور:
- تيليجرام: {DEV_USERNAME}
- واتساب (إذا محظور): {DEV_PHONE}

📢 نقاطك الحالية: {points} نقطة.

استخدم الأزرار للاطلاع على الخدمات وطلبها.

"""
    keyboard = []
    for service_name in services.keys():
        keyboard.append([InlineKeyboardButton(service_name, callback_data=f"order_{service_name}")])
    keyboard.append([InlineKeyboardButton("عجلة الحظ 🎡", callback_data="wheel")])
    keyboard.append([InlineKeyboardButton("تسجيل أسبوعي 📅", callback_data="weekly")])
    keyboard.append([InlineKeyboardButton("رجوع ⬅️", callback_data="back")])
    keyboard.append([InlineKeyboardButton("الصفحة الرئيسية 🏠", callback_data="home")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # إرسال صورة ترحيب مع النص
    update.message.reply_photo(photo=WELCOME_PHOTO_URL, caption=welcome_text, reply_markup=reply_markup)

def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    query.answer()
    
    if data == "back":
        # فقط نعيد قائمة الخدمات
        keyboard = []
        for service_name in services.keys():
            keyboard.append([InlineKeyboardButton(service_name, callback_data=f"order_{service_name}")])
        keyboard.append([InlineKeyboardButton("عجلة الحظ 🎡", callback_data="wheel")])
        keyboard.append([InlineKeyboardButton("تسجيل أسبوعي 📅", callback_data="weekly")])
        keyboard.append([InlineKeyboardButton("رجوع ⬅️", callback_data="back")])
        keyboard.append([InlineKeyboardButton("الصفحة الرئيسية 🏠", callback_data="home")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_caption(caption="اختر الخدمة التي تريدها:", reply_markup=reply_markup)
        return

    if data == "home":
        query.edit_message_text(text="الرجاء استخدم /start للعودة للصفحة الرئيسية.")
        return

    if data == "wheel":
        # عجلة الحظ - تعطي نقاط عشوائية بين 50 و 500
        points_won = random.randint(50, 500)
        add_points(user_id, points_won)
        query.edit_message_text(f"🎡 لقد ربحت {points_won} نقطة من عجلة الحظ!\nرصيدك الآن: {get_user(user_id)['points']} نقطة.")
        return

    if data == "weekly":
        # التسجيل الأسبوعي
        if can_get_weekly(user_id):
            add_points(user_id, 1000)
            set_weekly(user_id)
            query.edit_message_text(f"📅 تم تسجيلك لهذا الأسبوع بنجاح! حصلت على 1000 نقطة.\nرصيدك الآن: {get_user(user_id)['points']} نقطة.")
        else:
            query.edit_message_text("⚠️ لقد قمت بالتسجيل هذا الأسبوع مسبقاً. يمكنك المحاولة الأسبوع القادم.")
        return

    if data.startswith("order_"):
        service_name = data[len("order_"):]
        points_needed = services.get(service_name, None)
        
        if points_needed is None:
            query.edit_message_text("❌ الخدمة غير موجودة!")
            return
        
        user_pts = get_user(user_id)["points"]
        if user_pts >= points_needed:
            points_data[str(user_id)]["points"] -= points_needed
            save_data(points_data)
            query.edit_message_text(
                f"✅ تم طلب خدمة *{service_name}* بنجاح!\n"
                f"🔻 تم خصم {points_needed} نقطة من رصيدك.\n"
                f"💰 رصيدك الحالي: {points_data[str(user_id)]['points']} نقطة.\n\n"
                f"⏳ سيتم تنفيذ طلبك قريبًا.\n\n"
                f"📞 للتواصل مع المطور: {DEV_USERNAME}\n"
                f"📱 واتساب (إذا محظور): {DEV_PHONE}",
                parse_mode='Markdown'
            )
        else:
            query.edit_message_text(
                f"❌ رصيدك غير كافي لطلب *{service_name}*.\n"
                f"🔹 نقاطك الحالية: {user_pts} نقطة.\n"
                f"📢 يمكنك شحن نقاط أو التواصل مع المطور: {DEV_USERNAME}",
                parse_mode='Markdown'
            )
        return

def main():
    TOKEN = "8189292683:AAE53IGPbRVoe5Sc3a5saQGXHzOE-NWxPWY"
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()