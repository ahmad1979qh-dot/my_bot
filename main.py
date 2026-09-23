import sys
import subprocess
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

def auto_install(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

try:
    from telethon import TelegramClient, events
    from telethon.sessions import StringSession
except ImportError:
    auto_install("telethon")
    from telethon import TelegramClient, events
    from telethon.sessions import StringSession

# خادم ويب وهمي لإبقاء منفذ Render مفتوحاً ومنع إيقاف السيرفر
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# بدء خادم الويب في خلفية الكود
threading.Thread(target=run_web_server, daemon=True).start()

API_ID = 24400989
API_HASH = '8a682c7664872355902f07d127b494d9'
BOT_TOKEN = '8774584319:AAGJ8kMyYUGrpYDpLJRARH9yI2-0_a9B7bg'

ADMIN_USERNAME = '@italsory'

USER_SESSION_STRING = "1BVtsOL8Bu2YAt-dU42Fe8mIbPoH2jEZJQdXs7nMRxIhYJVk0PpiKYH4-acUI-DMeKuBGAQ5taqmcWF7HvA1TuqCPzn8LNp6mNqakfC-rZ9jjFyjuEHtM_ZVr1HYJ14vxGIlmm9V4ZtZM30yOWWROsxr4gihwoTD9I4_ehctIbBb-n2cQu61gZT66rIiGEqVks5VhFTpzD0hrIgmTlBWDwhJXiSL8NN2EPGwZe5IHa_099VHQuQNSj8wv1LJnlQH_wRdnYIidcu9IkfSunEKJeVTdjNLBr8wVpOpkfP2C9Fh6KoXRUx2yHHxK72SIorz2vnkfxMqc5Aw1TDvhy8PTsKYTME2wMe0="

user_client = TelegramClient(StringSession(USER_SESSION_STRING), API_ID, API_HASH)

async def main():
    await user_client.start()
    print("🔥 جاري تشغيل الحساب الوهمي...")
    print("🤖 جاري تشغيل البوت وإعداد نظام الإشعارات إلى حسابك الأساسي (@italsory)...")
    print("🚀 البوت يعمل الآن بكامل القوة والصلاحيات الخارقة!")
    
    @user_client.on(events.NewMessage(incoming=True))
    async def handler(event):
        pass

    await user_client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
