import json
import random
import datetime
import logging
import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# تفعيل اللوق
logging.basicConfig(
    format= %(asctime)s - %(name)s - %(levelname)s - %(message)s , level=logging.INFO
)
logger = logging.getLogger(__name__)

# بيانات البوت والمطور
TOKEN = "8189292683:AAE53IGPbRVoe5Sc3a5saQGXHzOE-NWxPWY"
BOT_NAME = "جمايكا"
DEVELOPER_NAME = "روني البحيره"
DEVELOPER_NUMBER = "01212843252"

# API خدمات التزويد
API_BASE = "https://panel.01212843252.repl.co/api/v1"

POINTS_FILE = "points.json"

# قراءة نقاط المستخدمين من ملف JSON
def load_points():
    try:
        with open(POINTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# حفظ نقاط المستخدمين إلى ملف JSON
def save_points(data):
    with open(POINTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تحديث نقاط مستخدم محدد
def update_user_points(user_id: str, points_change: int):
    points_data = load_points()
    points = points_data.get(user_id, 0)
    points += points_change
    if points < 0:
        points = 0
    points_data[user_id] = points
    save_points(points_data)
    return points

# التحقق من آخر تسجيل يومي للمستخدم لمنع الغش
def can_claim_daily(user_id: str):
    points_data = load_points()
    user_info = points_data.get(user_id+"_daily", None)
    if user_info:
        last_claim_str = user_info.get("last_claim", None)
        if last_claim_str:
            last_claim = datetime.datetime.strptime(last_claim_str, "%Y-%m-%d")
            now = datetime.datetime.now()
            if (now - last_claim).days < 1:
                return False
    return True

# تحديث آخر تسجيل يومي
def update_daily_claim(user_id: str):
    points_data = load_points()
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    user_info = points_data.get(user_id+"_daily", {})
    user_info["last_claim"] = now
    points_data[user_id+"_daily"] = user_info
    save_points(points_data)

# بدء المحادثة - قائمة رئيسية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎁 خدمات التزويد", callback_data= services )],
        [InlineKeyboardButton("⭐ نقاطي", callback_data= points )],
        [InlineKeyboardButton("📞 تواصل مع المطور", callback_data= contact )],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"أهلاً بك في بوت {BOT_NAME} 🤖\nكيف يمكنني مساعدتك اليوم؟",
        reply_markup=reply_markup
    )

# قائمة خدمات التزويد
async def services_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("👥 زيادة متابعين انستقرام", callback_data= add_followers )],
        [InlineKeyboardButton("❤️ زيادة لايكات انستقرام", callback_data= add_likes )],
        [InlineKeyboardButton("👀 زيادة مشاهدات تيك توك", callback_data= add_views )],
        [InlineKeyboardButton("⬅️ رجوع", callback_data= home )],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "اختر الخدمة التي تريدها:",
        reply_markup=reply_markup
    )

# صفحة نقاط المستخدم
async def points_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    points_data = load_points()
    points = points_data.get(user_id, 0)
    text = f"⭐ رصيدك الحالي من النقاط: {points} نقطة."
    keyboard = [
        [InlineKeyboardButton("🎡 عجلة الحظ (50-500 نقطة)", callback_data= spin_wheel )],
        [InlineKeyboardButton("🎁 تسجيل يومي (+200 نقطة)", callback_data= daily )],
        [InlineKeyboardButton("⬅️ رجوع", callback_data= home )],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

# تواصل مع المطور
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"📞 تواصل مع المطور: {DEVELOPER_NAME}\nرقم الواتساب: {DEVELOPER_NUMBER}"
    keyboard = [
        [InlineKeyboardButton("⬅️ رجوع", callback_data= home )],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

# عجلة الحظ
async def spin_wheel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    points_data = load_points()
    points = points_data.get(user_id, 0)

    cost = 50
    if points < cost:
        await query.edit_message_text(
            f"❌ تحتاج {cost} نقطة لتدوير عجلة الحظ، ورصيدك الحالي {points} نقطة.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data= points )]])
        )
        return

    # خصم النقاط
    update_user_points(user_id, -cost)

    # نقاط الفوز من 50 إلى 500
    win_points = random.randint(50, 500)
    update_user_points(user_id, win_points)

    text = f"🎡 دورت عجلة الحظ ودخلت {win_points} نقطة! رصيدك الآن {points - cost + win_points} نقطة."
    keyboard = [
        [InlineKeyboardButton("⬅️ رجوع", callback_data= points )],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data= home )],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

# تسجيل يومي
async def daily_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if not can_claim_daily(user_id):
        await query.edit_message_text(
            "⏳ لقد حصلت على نقاطك اليومية مسبقاً، تعال غداً للحصول على المزيد.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data= points )]])
        )
        return

    update_user_points(user_id, 200)
    update_daily_claim(user_id)
    points_data = load_points()
    points = points_data.get(user_id, 0)

    await query.edit_message_text(
        f"🎁 تهانينا! حصلت على 200 نقطة تسجيل يومي.\nرصيدك الآن: {points} نقطة.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data= points )]])
    )

# صفحة شراء الخدمات بالنقاط
async def buy_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    points_data = load_points()
    points = points_data.get(user_id, 0)

    keyboard = [
        [InlineKeyboardButton("👥 زيادة متابعين انستقرام (500 نقطة)", callback_data= buy_followers )],
        [InlineKeyboardButton("❤️ زيادة لايكات انستقرام (300 نقطة)", callback_data= buy_likes )],
        [InlineKeyboardButton("👀 زيادة مشاهدات تيك توك (400 نقطة)", callback_data= buy_views )],
        [InlineKeyboardButton("⬅️ رجوع", callback_data= home )],
    ]
    text = f"🛒 اختر الخدمة التي تريد شراءها بالنقاط.\nرصيدك الحالي: {points} نقطة."
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

# تنفيذ شراء خدمة بالنقاط
async def buy_service_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    points_data = load_points()
    points = points_data.get(user_id, 0)

    data = query.data
    cost_map = {
         buy_followers : 500,
         buy_likes : 300,
         buy_views : 400,
    }
    service_map = {
         buy_followers :  instagram_followers ,
         buy_likes :  instagram_likes ,
         buy_views :  tiktok_views ,
    }

    cost = cost_map.get(data, 0)
    service = service_map.get(data)

    if points < cost:
        await query.edit_message_text(
            f"❌ رصيدك غير كافي لشراء هذه الخدمة (تكلفة {cost} نقطة).\nرصيدك الحالي: {points} نقطة.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data= buy_services )]])
        )
        return

    # خصم النقاط
    update_user_points(user_id, -cost)

    # طلب التزويد عبر API (مثال)
    try:
        async with httpx.AsyncClient() as client:
            # هنا مثال طلب POST -- عدل حسب API الخاص بك
            payload = {"service": service, "user": user_id}
            r = await client.post(f"{API_BASE}/add", json=payload
