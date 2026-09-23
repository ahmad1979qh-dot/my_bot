import sys
import subprocess
import asyncio
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

def auto_install(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

try:
    from telethon import TelegramClient, events, Button
    from telethon.sessions import StringSession
    from telethon.tl.functions.channels import GetParticipantsRequest
    from telethon.tl.types import ChannelParticipantsAdmins
except ImportError:
    auto_install("telethon")
    from telethon import TelegramClient, events, Button
    from telethon.sessions import StringSession
    from telethon.tl.functions.channels import GetParticipantsRequest
    from telethon.tl.types import ChannelParticipantsAdmins

# خادم ويب وهمي لإرضاء متطلبات Render لفتح المنفذ
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# تشغيل الخادم الوهمي في الخلفية
threading.Thread(target=run_web_server, daemon=True).start()

API_ID = 34474141
API_HASH = '5ae079a54f32170ddc5b2ca52ecd2de6'
BOT_TOKEN = '8866078656:AAFrRZsiRXAb1nFzN9DFNIOrxpka1Fe0yU0'
ADMIN_USERNAME = '@italsory'

user_attempts = {}
user_start_stats = {}
MAX_ATTEMPTS = 5
COOLDOWN_HOURS = 8
COOLDOWN_SECONDS = COOLDOWN_HOURS * 3600
user_target_channel = {}
user_mode = {}

USER_SESSION_STRING = "1BVtsOKABu5ftePWrAd7ztvRF8rHJ1mDpqWgiduxIKD-cZofCKZ AMWDwvNSPOVZb28hnVVSfiDkVNOAVGch9VYeeaRSvG1ePUYInsabSfKM1j_MBUm7yX6 unU5uRsqm2n9oUwCZ83DHd1utz8-nbJBTbw1Q4joNs6BKn2_8p099vCIgq1jmoKCz4D C549kSJAnehmgq9_bZnemn1LF3s4mEZYTBKuVZ38kwxs_6pqc-or9FvBFlZFBdefeiY -lrWqOixIrX-yJJCAyXnSR1J05Ax55UuMpSTgsj3i0U0eFKV_vxWGs_dQ6cDHHT6KV_ 2yjlk6GheWZKbjNk1Y07tSHlP0zl2tz-A="

user_client = TelegramClient(StringSession(USER_SESSION_STRING), API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

STRONG_EN_PORN = [
    "cp", "child porn", "csam", "rape", "gangbang", "nude teen", "nsfw", "porno", "xxx", 
    "hardcore", "anal", "cumshot", "creampie", "blowjob", "orgasm", "incest", "bestiality", 
    "bukkake", "squirt", "dildo", "fuck", "pussy", "dick", "cock", "boobs", "asshole", 
    "slut", "whore", "escort", "sex video", "hot tape", "telegram porn", "pornchannel",
    "18+ video", "naked girl", "sex chat", "hentai uncensored"
]

AR_PORN_KEYWORDS = ["سكس", "إباحي", "جنسي", "فيديو ساخن", "بنات سكس", "مقاطع اباحية", "صور عري", "شواذ", "نيك", "18+", "فيديو فاضح", "صورة عارية", "صوره اباحيه", "مقطع جنسي", "اغتصب"]
VIOLENCE_KEYWORDS = ["اغتصاب", "اعتداء جنسي", "قتل متعمد", "ذبح بشري", "عنف دموي", "انتحار جماعي", "تهديد بالقتل", "إرهاب", "داعش"]
ABUSE_KEYWORDS = ["سب وشتم قذر", "شتم سافر", "ألفاظ نابية", "قحب", "عرص", "منيوك", "عاهرة"]
SPAM_DOMAINS = [".xyz", ".top", ".club", ".online", ".site", "t.me/joinchat", "bit.ly", "exe.io", "t.me/+"]
SPAM_PHRASES = ["اشترك الآن لربح", "مسابقة ربح المال", "تمويل قناتك براتب", "زيادة أعضاء مضمونة", "مطلوب ممثلين"]

def analyze_message_content(message):
    text = getattr(message, 'text', '') or getattr(message, 'message', '') or ''
    if hasattr(message, 'media') and message.media:
        if hasattr(message.media, 'caption') and message.media.caption:
            text += " " + message.media.caption
    text_lower = text.lower()
    for word in STRONG_EN_PORN + AR_PORN_KEYWORDS + VIOLENCE_KEYWORDS + ABUSE_KEYWORDS + SPAM_PHRASES:
        if word in text_lower:
            return "🔥 مخالف [محتوى غير آمن أو سبام محظور]"
    for domain in SPAM_DOMAINS:
        if domain in text_lower:
            return "🔗 مخالف [رابط مشبوه]"
    return "سليم"

async def get_all_channel_admins_and_owner(channel_entity):
    admins_list = []
    owner_info = "👑 **المالك الأساسي:** مخفي أو محمي"
    try:
        participants = await user_client(GetParticipantsRequest(
            channel=channel_entity, filter=ChannelParticipantsAdmins(), offset=0, limit=100, hash=0
        ))
        for user in participants.users:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = f"@{user.username}" if user.username else "بدون معرف"
            role = "مشرف عادي"
            is_the_owner = False
            for p in participants.participants:
                if p.user_id == user.id:
                    if hasattr(p, 'is_creator') and p.is_creator:
                        role = "👑 [المالك الأساسي الرسمي]"
                        is_the_owner = True
                    break
            formatted_admin = f"• الاسم: {name}\n  - المعرف: {username}\n  - الآيدي: `{user.id}`\n  - الصفة: {role}"
            if is_the_owner:
                owner_info = f"👑 **المالك الأساسي الرسمي:**\n  - الاسم: {name}\n  - المعرف: {username}\n  - الآيدي: `{user.id}`"
            else:
                admins_list.append(formatted_admin)
        if admins_list:
            return owner_info, admins_list
    except Exception:
        pass
    return owner_info, ["• تعذر جلب قائمة المشرفين بدقة."]

@bot_client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    sender = await event.get_sender()
    user_id = sender.id
    name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
    username = f"@{sender.username}" if sender.username else "بدون معرف"
    
    if user_id not in user_start_stats:
        user_start_stats[user_id] = {'visits': 1}
    else:
        user_start_stats[user_id]['visits'] += 1

    current_visits = user_start_stats[user_id]['visits']
    
    try:
        await user_client.send_message(ADMIN_USERNAME, f"🚨 دخول مستخدم للبوت:\n• الاسم: {name}\n• المعرف: {username}\n• الآيدي: `{user_id}`\n• الزيارات: {current_visits}")
    except Exception:
        pass

    reply_keyboard = [
        [Button.text("📝 كشف", resize=True), Button.text("🛑 مخالفات", resize=True)]
    ]
    welcome_message = (
        "🛡️ **نظام الحماية والفحص المتقدم للقنوات** 🚀\n\n"
        f"👤 **معلوماتك:** `{name}` (`{username}`)\n"
        f"📊 عدد مرات الاستخدام: `{current_visits}`\n\n"
        "اختر الخدمة المطلوبة من الأزرار بالأسفل، ثم أرسل معرف القناة (مثال: `@telegram`):"
    )
    await event.respond(welcome_message, buttons=reply_keyboard)

@bot_client.on(events.NewMessage)
async def handle_incoming_messages(event):
    text = event.text.strip() if event.text else ""
    if not text or text.startswith('/start'):
        return
    user_id = event.sender_id

    if text == "📝 كشف":
        user_mode[user_id] = "admins"
        await event.respond("📝 **تم اختيار وضع [كشف المشرفين والمالك].**\nأرسل معرف القناة الآن:")
        return

    if text == "🛑 مخالفات":
        user_mode[user_id] = "violations"
        await event.respond("🛑 **تم اختيار وضع [فحص المخالفات].**\nأرسل معرف القناة الآن:")
        return

    if text.startswith('@'):
        current_time = time.time()
        if user_id in user_attempts:
            data = user_attempts[user_id]
            if current_time >= data['reset_time']:
                user_attempts[user_id] = {'count': 0, 'reset_time': current_time + COOLDOWN_SECONDS}
            elif data['count'] >= MAX_ATTEMPTS:
                await event.respond("⚠️ عذراً، لقد استنفدت محاولاتك الـ 5. تنتظر 8 ساعات لتتجدد.")
                return
        else:
            user_attempts[user_id] = {'count': 0, 'reset_time': current_time + COOLDOWN_SECONDS}

        user_target_channel[user_id] = text
        chosen_mode = user_mode.get(user_id, "admins")
        user_attempts[user_id]['count'] += 1

        if chosen_mode == "admins":
            await event.respond(f"⏳ جاري تحليل الإدارة للقناة `{text}`...")
            try:
                channel_entity = await user_client.get_entity(text)
                owner_info, admins = await get_all_channel_admins_and_owner(channel_entity)
                report = f"👑 **تقرير الكشف:**\n{owner_info}\n\n" + "\n".join(admins)
                await event.respond(report, link_preview=False)
            except Exception as e:
                await event.respond(f"❌ خطأ: {e}")
        else:
            await event.respond(f"⚡ جاري فحص أحدث المنشورات في `{text}`...")
            try:
                channel_entity = await user_client.get_entity(text)
                violations = 0
                async for message in user_client.iter_messages(channel_entity, limit=100):
                    if "مخالف" in analyze_message_content(message):
                        violations += 1
                await event.respond(f"✅ تم الفحص. عدد المخالفات المرصودة: {violations}")
            except Exception as e:
                await event.respond(f"❌ خطأ: {e}")

async def main():
    print("🔥 جاري بدء تشغيل الحساب الوهمي والبوت...")
    await user_client.start()
    await bot_client.start(bot_token=BOT_TOKEN)
    
    try:
        await bot_client.delete_webhook()
    except Exception:
        pass

    print("🚀 البوت يعمل الآن ويستقبل الرسائل بنجاح!")
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())
    
