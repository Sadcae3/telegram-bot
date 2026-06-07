import os
import json
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
PAYMENT_LINK = "https://sadratajik.com/?add-to-cart=8288"
DATA_FILE = "users.json"

# ─── متن‌های ربات ───────────────────────────────────────────

WELCOME = """👋 سلام و خوش اومدی

من دستیار صدرا تاجیک هستم.

اینجا قراره یه تجربه متفاوت داشته باشی.

🎯 برنامه «عملیات هیدرا» — یه مینی‌دوره صوتی رایگان در ۴ فاز — همین الان شروع میشه.

هر روز یه فاز. هر فاز پیش‌نیاز بعدیه.

آماده‌ای؟"""

PHASES = {
    0: {
        "title": "⚡️ فاز صفر — پایه‌گذاری",
        "text": """فاز صفر عملیات هیدرا:

این فاز درباره یه حقیقت تلخه.

۹۰٪ آدم‌ها فکر می‌کنن مشکلشون کمبود اطلاعاته.
مشکل واقعی؟ کمبود تمرکز استراتژیک.

📎 فایل صوتی این فاز رو گوش بده.
فردا فاز اول منتظرته.""",
        "audio": None  # بعداً file_id صوتی اضافه میشه
    },
    1: {
        "title": "🔥 فاز اول — شناسایی دشمن",
        "text": """فاز اول عملیات هیدرا:

دشمن تمرکز تو کیه؟

نه موبایل. نه نوتیفیکیشن.
خودته.

دقیق‌تر: سیستم تصمیم‌گیری غلطته.

📎 فایل صوتی این فاز رو گوش بده.
فردا فاز دوم.""",
        "audio": None
    },
    2: {
        "title": "💡 فاز دوم — طراحی سیستم",
        "text": """فاز دوم عملیات هیدرا:

سیستم یعنی چی؟

یعنی وقتی انگیزه نداری، باز هم پیش میری.
یعنی وقتی خسته‌ای، ساختار برات تصمیم میگیره.

📎 فایل صوتی این فاز رو گوش بده.
فردا فاز سوم — و یه چیز مهم.""",
        "audio": None
    },
    3: {
        "title": "🎯 فاز سوم — اجرا",
        "text": """فاز سوم عملیات هیدرا — آخرین فاز:

اجرا بدون استراتژی = شلوغ‌بازی.
استراتژی بدون اجرا = خیال‌پردازی.

این فاز این دو رو به هم وصل می‌کنه.

📎 فایل صوتی این فاز رو گوش بده.""",
        "audio": None
    }
}

SALES_MESSAGE = """🏆 عملیات هیدرا تموم شد.

حالا می‌دونی مشکل کجاست.
حالا می‌دونی سیستم چیه.

اما یه چیزی هست که هیدرا بهت نداد:

**استراتژیست تمرکز** — نسخه کامل.

۵ ساعت صوتی + فریم‌ورک‌های اجرایی که تو هیچ دوره فارسی دیگه‌ای پیدا نمیکنی.

این یه دوره برای همه نیست.
برای آدم‌هاییه که وقتشون باارزشه و می‌خوان نتیجه بگیرن.

قیمت: ۲،۰۰۰،۰۰۰ تومان

👇 اگه آماده‌ای:"""

# ─── مدیریت داده کاربران ──────────────────────────────────

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

def get_user(user_id):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "joined": datetime.now().isoformat(),
            "phase": 0,
            "last_phase_date": datetime.now().isoformat()
        }
        save_users(users)
    return users[uid]

def update_user(user_id, data):
    users = load_users()
    uid = str(user_id)
    users[uid].update(data)
    save_users(users)

# ─── هندلرها ──────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    get_user(user_id)  # ثبت کاربر

    keyboard = [[InlineKeyboardButton("بزن بریم ⚡️", callback_data="phase_0")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(WELCOME, reply_markup=reply_markup)

async def send_phase(update: Update, context: ContextTypes.DEFAULT_TYPE, phase_num: int, user_id: int):
    phase = PHASES[phase_num]

    if phase["audio"]:
        await context.bot.send_audio(
            chat_id=user_id,
            audio=phase["audio"],
            caption=f"{phase['title']}\n\n{phase['text']}"
        )
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"{phase['title']}\n\n{phase['text']}"
        )

    update_user(user_id, {
        "phase": phase_num + 1,
        "last_phase_date": datetime.now().isoformat()
    })

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "phase_0":
        await send_phase(update, context, 0, user_id)

    elif query.data == "buy":
        keyboard = [[InlineKeyboardButton("🛒 خرید استراتژیست تمرکز", url=PAYMENT_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(SALES_MESSAGE, reply_markup=reply_markup, parse_mode="Markdown")

async def send_daily_phases(context: ContextTypes.DEFAULT_TYPE):
    """هر روز فاز بعدی رو برای کاربران ارسال می‌کنه"""
    users = load_users()
    now = datetime.now()

    for uid, data in users.items():
        try:
            phase = data.get("phase", 0)
            last_date = datetime.fromisoformat(data.get("last_phase_date", now.isoformat()))
            days_passed = (now - last_date).days

            if days_passed >= 1:
                if phase <= 3:
                    await send_phase(None, context, phase, int(uid))
                elif phase == 4:
                    # ارسال پیام فروش
                    keyboard = [[InlineKeyboardButton("🛒 خرید استراتژیست تمرکز", url=PAYMENT_LINK)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await context.bot.send_message(
                        chat_id=int(uid),
                        text=SALES_MESSAGE,
                        reply_markup=reply_markup,
                        parse_mode="Markdown"
                    )
                    update_user(int(uid), {"phase": 5})

        except Exception as e:
            logger.error(f"Error sending to {uid}: {e}")

# ─── اجرا ─────────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # job queue برای ارسال روزانه — هر روز ساعت ۹ صبح
    app.job_queue.run_daily(
        send_daily_phases,
        time=datetime.strptime("09:00", "%H:%M").time()
    )

    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
