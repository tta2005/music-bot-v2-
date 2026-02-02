import os
import yt_dlp
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient

# Environment Variables တွေဆီကနေ Data ယူခြင်း
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")

# Bot နဲ့ Database ကို ချိတ်ဆက်ခြင်း
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client.music_bot_db

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("🚀 Pro Caching System အဆင်သင့်ဖြစ်ပြီ!\nသီချင်းနာမည် ပို့ပေးပါ။")

@app.on_message(filters.text & ~filters.command(["start"]))
async def download_song(client, message):
    song_name = message.text
    sent_message = await message.reply_text(f"🔎 '{song_name}' ကို ရှာနေတယ်...")

    try:
        # YouTube ကနေ သီချင်းရှာပြီး အချက်အလက်ယူခြင်း
        ydl_opts = {
            'format': 'bestaudio/best',
            'keepvideo': False,
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # အခုနကတက်တဲ့ String indices error မတက်အောင် entries ကနေ ဆွဲထုတ်ထားတယ်
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            if 'entries' in info:
                video = info['entries'][0]
            else:
                video = info
            
            file_name = ydl.prepare_filename(video).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            title = video.get('title', 'Unknown Title')

        # Telegram ဆီ သီချင်းပို့ခြင်း
        await message.reply_audio(audio=open(file_name, 'rb'), title=title)
        await sent_message.delete()

        # Local မှာ သိမ်းထားတဲ့ ဖိုင်ကို ပြန်ဖျက်ခြင်း
        if os.path.exists(file_name):
            os.remove(file_name)

    except Exception as e:
        await sent_message.edit(f"❌ Error: {str(e)}")

app.run()
