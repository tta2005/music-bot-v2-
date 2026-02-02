import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient
import yt_dlp

# Koyeb Variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")

# Setup Clients
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client.music_bot_db
songs_collection = db.songs

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("🚀 Pro Caching System အဆင်သင့်ဖြစ်ပြီ!\nသီချင်းနာမည် ပို့ပေးပါ။")

@app.on_message(filters.text & ~filters.command(["start"]))
async def music_engine(client, message: Message):
    query = message.text.lower().strip()
    status = await message.reply_text(f"🔎 '{query}' ကို ရှာနေတယ်...")
    
    # ၁။ Database မှာ အရင်စစ်မယ်
    try:
        cached_song = await songs_collection.find_one({"query": query})
        if cached_song:
            await status.edit("⚡ Database ထဲကနေ ချက်ချင်း ပို့ပေးနေပြီ...")
            await client.send_audio(message.chat.id, cached_song['file_id'], caption=f"✅ {cached_song['title']}")
            await status.delete()
            return
    except Exception as e:
        print(f"DB Error: {e}")

    # ၂။ SoundCloud ကနေ ရှာပြီး ဒေါင်းမယ်
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'scsearch',
        'quiet': True,
        'nocheckcertificate': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"scsearch1:{query}", download=False)
            if not info or 'entries' not in info or not info['entries']:
                await status.edit("❌ မတွေ့ပါဘူး၊ တခြားနာမည်နဲ့ ထပ်ရှာကြည့်ပါ။")
                return
                
            video = info['entries'][0]
            title = video.get('title', 'Music')
            url = video.get('url')
            
            await status.edit(f"📥 {title}\nကို ဒေါင်းလုဒ်ဆွဲနေတယ်...")
            
            path = f"downloads/{title}.mp3"
            if not os.path.exists('downloads'): os.makedirs('downloads')
            
            ydl_opts['outtmpl'] = f"downloads/%(title)s.%(ext)s"
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl_down:
                ydl_down.download([url])
            
            # ဒေါင်းထားတဲ့ဖိုင် အမှန်တကယ်ရှိမရှိ စစ်မယ်
            downloaded_files = os.listdir('downloads')
            if not downloaded_files:
                await status.edit("❌ ဒေါင်းလုဒ်ဆွဲတာ အဆင်မပြေပါဘူး။")
                return
            
            final_path = f"downloads/{downloaded_files[0]}"
            
            # ၃။ Telegram ဆီ ပို့ပြီး Database ထဲ သိမ်းမယ်
            sent_audio = await client.send_audio(message.chat.id, final_path, title=title)
            await songs_collection.insert_one({
                "query": query,
                "file_id": sent_audio.audio.file_id,
                "title": title
            })
            
            await status.delete()
            os.remove(final_path)
            
    except Exception as e:
        await status.edit(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    app.run()
