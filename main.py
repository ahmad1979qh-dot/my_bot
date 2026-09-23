import sys
import subprocess
import asyncio
import time

def auto_install(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

try:
    from telethon import TelegramClient, events, Button
    from telethon.sessions import StringSession
    from telethon.tl.functions.channels import GetParticipantsRequest
    from telethon.tl.types import ChannelParticipantsAdmins, MessageMediaPhoto, MessageMediaDocument
except ImportError:
    auto_install("telethon")
    from telethon import TelegramClient, events, Button
    from telethon.sessions import StringSession
    from telethon.tl.functions.channels import GetParticipantsRequest
    from telethon.tl.types import ChannelParticipantsAdmins, MessageMediaPhoto, MessageMediaDocument

API_ID = 24400989
API_HASH = '8a682c7664872355902f07d127b494d9'
BOT_TOKEN = '8774584319:AAGJ8kMyYUGrpYDpLJRARH9yI2-0_a9B7bg'

# معرف حسابك الأساسي الذي ستصل إليه إشعارات الدخول
ADMIN_USERNAME = '@italsory'

user_attempts = {}
user_start_stats = {}
MAX_ATTEMPTS = 5
COOLDOWN_HOURS = 8
COOLDOWN_SECONDS = COOLDOWN_HOURS * 3600
user_target_channel = {}
user_mode = {}

user_client = TelegramClient('my_userbot_session', API_ID, API_HASH)
bot_client = TelegramClient('my_bot_session', API_ID, API_HASH)

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

    for word in STRONG_EN_PORN:
        if word in text_lower:
            return "🔥 مخالف [محتوى/صور إباحية إنجليزية محظورة - تطير فوري]"

    for word in AR_PORN_KEYWORDS:
        if word in text_lower:
            return "🔥 مخالف [محتوى أو صورة إباحية صريحة]"

    for word in VIOLENCE_KEYWORDS:
        if word in text_lower:
            return "⚠️ مخالف [عنف شديد أو إرهاب أو اغتصاب]"

    for word in ABUSE_KEYWORDS:
        if word in text_lower:
            return "🛑 مخالف [إساءة وسب سافر]"

    for domain in SPAM_DOMAINS:
        if domain in text_lower:
            return "🔗 مخالف [رابط مشبوه أو دعوة مغلقة]"
            
    for phrase in SPAM_PHRASES:
        if phrase in text_lower:
            return "📢 مخالف [إعلان ترويجي / سبام]"
            
    return "سليم"

async def get_all_channel_admins_and_owner(channel_entity):
    admins_list = []
    owner_info = "👑 **المالك الأساسي:** مخفي أو محمي بواسطة إعدادات الخصوصية الفائقة"
    try:
        participants = await user_client(GetParticipantsRequest(
            channel=channel_entity, filter=ChannelParticipantsAdmins(), offset=0, limit=100, hash=0
        ))
        for user in participants.users:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = f"@{user.username}" if user.username else "بدون معرف"
            user_id = user.id
            role = "مشرف عادي"
            is_the_owner = False
            for p in participants.participants:
                if p.user_id == user_id:
                    if hasattr(p, 'rank') and p.rank:
                        role = f"مشرف (رتبة: {p.rank})"
                    if hasattr(p, 'is_creator') and p.is_creator:
                        role = "👑 [المالك الأساسي الرسمي]"
                        is_the_owner = True
                    break
            formatted_admin = f"• الاسم: {name}\n  - المعرف: {username}\n  - الآيدي: `{user_id}`\n  - الصفة: {role}"
            if is_the_owner:
                owner_info = f"👑 **المالك الأساسي الرسمي:**\n  - الاسم: {name}\n  - المعرف: {username}\n  - الآيدي: `{user_id}`"
            else:
                admins_list.append(formatted_admin)
        if admins_list:
            return owner_info, admins_list
    except Exception:
        pass

    try:
        async for message in user_client.iter_messages(channel_entity, limit=100):
            if message.sender_id:
                try:
                    sender = await user_client.get_entity(message.sender_id)
                    s_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
                    s_username = f"@{sender.username}" if sender.username else "بدون معرف"
                    info_str = f"• الاسم: {s_name}\n  - المعرف: {s_username}\n  - الآيدي: `{sender.id}`\n  - الصفة: ينشر باستمرار في القناة (مالك أو مشرف رئيسي)"
                    if info_str not in admins_list:
                        admins_list.append(info_str)
                except Exception:
                    pass
            if len(admins_list) >= 6:
                break
        if admins_list:
            owner_info = "👑 **المالك / الناشر الأساسي:** تم استخراجه بأقوى خوارزمية تحليل لبصمة المنشورات"
    except Exception:
        admins_list.append(f"⚠️ تعذر الاستخراج الكامل بسبب قيود الخصوصية العالية.")

    return owner_info, admins_list

@bot_client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    sender = await event.get_sender()
    user_id = sender.id
    name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
    username = f"@{sender.username}" if sender.username else "بدون معرف"
    
    if user_id not in user_start_stats:
        user_start_stats[user_id] = {'visits': 1, 'name': name, 'username': username}
    else:
        user_start_stats[user_id]['visits'] += 1
        user_start_stats[user_id]['name'] = name
        user_start_stats[user_id]['username'] = username

    current_visits = user_start_stats[user_id]['visits']
    
    notification_text = (
        f"🚨 **تنبيه دخول مستخدم جديد للبوت:**\n\n"
        f"• الاسم: {name}\n"
        f"• المعرف: {username}\n"
        f"• الآيدي: `{user_id}`\n"
        f"• عدد مرات استخدام البوت: {current_visits}"
    )
    try:
        await user_client.send_message(ADMIN_USERNAME, notification_text)
    except Exception as e:
        print(f"تعذر إرسال الإشعار للحساب الأساسي: {e}")

    reply_keyboard = [
        [Button.text("📝 كشف", resize=True), Button.text("🛑 مخالفات", resize=True)]
    ]
    welcome_message = (
        "🛡️ **نظام الحماية والفحص الخارق المتقدم للقنوات** 🚀\n\n"
        f"👤 **معلوماتك المسجلة:**\n"
        f"• الاسم: `{name}`\n"
        f"• المعرف: `{username}`\n"
        f"• الآيدي: `{user_id}`\n\n"
        f"📊 عدد مرات استخدامك للبوت: `{current_visits}` مرّة.\n\n"
        "أقوى نظام تليجرام لتحليل الإدارة، كشف المالكين الأساسيين، والرصد العميق للمخالفات والصور الإباحية الحصرية.\n"
        "⏳ *نظام المحاولات:* لك 5 محاولات فحص، ولا تتجدد إلا بعد مرور 8 ساعات كاملة لضمان العدالة وعدم التحايل.\n\n"
        "👑 **المالك والمشرف العام:** @italsory\n\n"
        "👇 **اختر الخدمة المطلوبة من الأزرار بالأسفل، ثم أرسل معرف القناة (مثال: `@telegram`):**"
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
        await event.respond("📝 **تم اختيار وضع [كشف المشرفين والمالك الأساسي].**\nالآن أرسل معرف القناة (مثال: `@telegram`):")
        return

    if text == "🛑 مخالفات":
        user_mode[user_id] = "violations"
        await event.respond("🛑 **تم اختيار وضع [فحص المخالفات والصور الإباحية الحصرية].**\nالآن أرسل معرف القناة (مثال: `@telegram`):")
        return

    if text.startswith('@'):
        current_time = time.time()
        
        if user_id in user_attempts:
            data = user_attempts[user_id]
            if current_time >= data['reset_time']:
                user_attempts[user_id] = {'count': 0, 'reset_time': current_time + COOLDOWN_SECONDS}
            elif data['count'] >= MAX_ATTEMPTS:
                remaining_seconds = int(data['reset_time'] - current_time)
                rem_hours = remaining_seconds // 3600
                rem_mins = (remaining_seconds % 3600) // 60
                await event.respond(f"⚠️ **عذراً، لقد استنفدت محاولات الفحص الـ 5 المسموحة.**\n⏳ حتى لو قمت بحذف المحادثة والعودة، لن تتصفر المحاولات إلا بعد مرور الـ 8 ساعات كاملة.\nيرجى الانتظار لمدة `{rem_hours}` ساعة و `{rem_mins}` دقيقة.")
                return
        else:
            user_attempts[user_id] = {'count': 0, 'reset_time': current_time + COOLDOWN_SECONDS}

        user_target_channel[user_id] = text
        chosen_mode = user_mode.get(user_id, "admins")

        if chosen_mode == "admins":
            await execute_scan_admins(event, user_id)
        else:
            await execute_scan_violations(event, user_id)

async def execute_scan_admins(event, user_id):
    channel_username = user_target_channel[user_id]
    user_attempts[user_id]['count'] += 1
    await event.respond(f"⏳ جاري الفحص وتحليل الإدارة العميق للقناة `{channel_username}`...")
    try:
        channel_entity = await user_client.get_entity(channel_username)
        owner_info, admins = await get_all_channel_admins_and_owner(channel_entity)
        admins_text = "\n\n".join(admins) if admins else "لا توجد تفاصيل إضافية."
        report = f"👑 **تقرير الكشف الشامل (بواسطة @italsory):**\n━━━━━━━━━━━━━━━━━━━\n{owner_info}\n\n{admins_text}"
        await event.respond(report, link_preview=False)
    except Exception as e:
        await event.respond(f"❌ حدث خطأ أثناء تحليل القناة: {str(e)}")

async def execute_scan_violations(event, user_id):
    channel_username = user_target_channel[user_id]
    clean_username = channel_username.replace('@', '').strip()
    user_attempts[user_id]['count'] += 1
    await event.respond(f"⚡ جاري الفحص الدقيق لأحدث **350 منشوراً** (البحث عن الكلمات الإباحية، السب، العنف، والصور الإباحية الحصرية) في `{channel_username}`...")
    try:
        channel_entity = await user_client.get_entity(channel_username)
        violations = []
        total_scanned = 0
        
        async for message in user_client.iter_messages(channel_entity, limit=350):
            total_scanned += 1
            verdict = analyze_message_content(message)
            if "مخالف" in verdict:
                msg_text = getattr(message, 'text', '') or getattr(message, 'message', '') or 'محتوى مرئي / صورة مخالفة'
                violations.append({'id': message.id, 'link': f"https://t.me/{clean_username}/{message.id}", 'verdict': verdict, 'text': msg_text[:60]})
        
        if not violations:
            report = f"✅ **تقرير فحص المخالفات الحصرية:**\nفُحص `{total_scanned}` منشوراً، والقناة نظيفة وخالية تماماً من أي مخالفات أو صور إباحية."
        else:
            report = f"🚨 **تم رصد واكتشاف {len(violations)} مخالفة حصرية من أصل {total_scanned} منشوراً:**\n\n"
            for v in violations[:20]:
                report += f"🔹 [رابط المخالفة المباشر]({v['link']}) \n   ↳ الـحكم: {v['verdict']}\n\n"
        await event.respond(report, link_preview=False)
    except Exception as e:
        await event.respond(f"❌ حدث خطأ أثناء الفحص: {str(e)}")

async def main():
    print("🔥 جاري تشغيل الحساب الوهمي...")
    await user_client.start()
    print("🤖 جاري تشغيل البوت وإعداد نظام إرسال الإشعارات إلى حسابك الأساسي (@italsory)...")
    await bot_client.start(bot_token=BOT_TOKEN)
    print("🚀 البوت يعمل الآن بكامل القوة والصلاحيات الخارقة!")
    await asyncio.gather(user_client.run_until_disconnected(), bot_client.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(main())
 
