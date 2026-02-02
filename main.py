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
    await message.reply_text("🚀 Pro Caching System စတင်နေပြီ သားကြီး!\nသီချင်းနာမည် ပို့ပေးပါ။")

@app.on_message(filters.text & ~filters.command(["start"]))
async def music_engine(client, message: Message):
    query = message.text.lower()
    status = await message.reply_text(f"🔎 '{query}' ကို ရှာနေတယ်...")
    
    # ၁။ Database မှာ အရင်စစ်မယ်
    cached_song = await songs_collection.find_one({"query": query})
    if cached_song:
        await status.edit("⚡ Database ထဲမှာ ရှိပြီးသားမို့လို့ ချက်ချင်း ပို့ပေးနေပြီ...")
        try:
            await client.send_audio(message.chat.id, cached_song['file_id'], caption=f"✅ Cached: {cached_song['title']}")
            await status.delete()
            return
        except:
            pass # File ID ပျက်နေရင် အောက်ကအတိုင်း အသစ်ပြန်ဒေါင်းမယ်

    # ၂။ SoundCloud ကနေ ဒေါင်းမယ်
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'nocheckcertificate': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"scsearch1:{query}", download=False)
            video = search_results['entries'][0]
            title, url = video['title'], video['url']
            
            await status.edit(f"📥 {title}\nကို ဒေါင်းလုဒ်ဆွဲနေတယ်...")
            
            path = f"downloads/{title}.mp3"
            ydl_opts['outtmpl'] = path.replace('.mp3', '.%(ext)s')
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
            
            if not os.path.exists('downloads'): os.makedirs('downloads')
            ydl.download([url])
            
            # ၃။ ပို့ပြီးရင် Database ထဲ file_id သိမ်းမယ်
            sent_audio = await client.send_audio(message.chat.id, path, title=title)
            await songs_collection.insert_one({
                "query": query,
                "file_id": sent_audio.audio.file_id,
                "title": title
            })
            
            await status.delete()
            if os.path.exists(path): os.remove(path)
            
    except Exception as e:
        await status.edit(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    app.run()
