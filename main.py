import sys
import subprocess
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

def auto_install(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    except Exception:
        pass

try:
    from telethon import TelegramClient, events, Button
    from telethon.sessions import StringSession
except ImportError:
    auto_install("telethon")
    from telethon import TelegramClient, events, Button
    from telethon.sessions import StringSession

# --- خادم الويب الأساسي لإرضاء Render ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running 24/7!")
    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# تشغيل الويب في الخلفية
threading.Thread(target=run_web_server, daemon=True).start()

# --- بيانات التوثيق ---
API_ID = 34474141
API_HASH = '5ae079a54f32170ddc5b2ca52ecd2de6'
BOT_TOKEN = '8866078656:AAFrRZsiRXAb1nFzN9DFNIOrxpka1Fe0yU0'
ADMIN_USERNAME = '@italsory'

USER_SESSION_STRING = (
    "1BVtsOKABu5ftePWrAd7ztvRF8rHJ1mDpqWgiduxIKD-cZofCKZ"
    "AMWDwvNSPOVZb28hnVVSfiDkVNOAVGch9VYeeaRSvG1ePUYInsabSfKM1j_MBUm7yX6"
    "unU5uRsqm2n9oUwCZ83DHd1utz8-nbJBTbw1Q4joNs6BKn2_8p099vCIgq1jmoKCz4D"
    "C549kSJAnehmgq9_bZnemn1LF3s4mEZYTBKuVZ38kwxs_6pqc-or9FvBFlZFBdefeiY"
    "-lrWqOixIrX-yJJCAyXnSR1J05Ax55UuMpSTgsj3i0U0eFKV_vxWGs_dQ6cDHHT6KV_"
    "2yjlk6GheWZKbjNk1Y07tSHlP0zl2tz-A="
)

user_client = TelegramClient(StringSession(USER_SESSION_STRING), API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

user_start_stats = {}

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

async def main():
    print("🔥 جاري بدء الاتصال...", flush=True)
    await user_client.start()
    print("✅ الحساب الوهمي يعمل بنجاح!", flush=True)
    
    await bot_client.start(bot_token=BOT_TOKEN)
    print("✅ البوت يعمل بنجاح!", flush=True)
    
    try:
        await bot_client.delete_webhook()
    except Exception:
        pass

    print("🚀 البوت جاهز تماماً ويستقبل الرسائل!", flush=True)
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())
    
