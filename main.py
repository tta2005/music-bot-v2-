import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import yt_dlp

# Koyeb Environment Variables ကနေ အချက်အလက်တွေ ယူမယ်
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Pyrogram Client ကို Bot Token နဲ့ Run မယ်
app = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("🔥 Pro Bot စနစ် အသက်ဝင်နေပြီ သားကြီး!\nသီချင်းနာမည် ပို့ပေးပါ။ SoundCloud ကနေ ရှာပေးမယ်။")

@app.on_message(filters.text & ~filters.command(["start"]))
async def search_and_send(client, message: Message):
    query = message.text
    status = await message.reply_text(f"🔎 '{query}' ကို ရှာနေတယ်...")
    
    # SoundCloud မှာ ရှာဖို့နဲ့ Network Error တွေ ကျော်ဖို့ Settings
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # scsearch ဆိုတာ SoundCloud မှာ ရှာခိုင်းတာပါ
            search_results = ydl.extract_info(f"scsearch1:{query}", download=False)
            
            if not search_results or 'entries' not in search_results or not search_results['entries']:
                await status.edit("❌ SoundCloud မှာ ရှာမတွေ့ဘူး သားကြီး။")
                return

            video = search_results['entries'][0]
            title = video['title']
            url = video['url']
            
            await status.edit(f"🎵 {title}\n\nအခု ဒေါင်းနေပြီ၊ ခဏစောင့်...")
            
            # ဒေါင်းလုဒ်ဖိုင် သိမ်းမယ့် လမ်းကြောင်း
            if not os.path.exists('downloads'): 
                os.makedirs('downloads')
                
            path = f"downloads/{title}.mp3"
            ydl_opts['outtmpl'] = path.replace('.mp3', '.%(ext)s')
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
            
            # အမှန်တကယ် ဒေါင်းလုဒ်လုပ်မယ်
            ydl.download([url])
            
            # Telegram ဆီ ပို့မယ်
            await client.send_audio(
                chat_id=message.chat.id,
                audio=path,
                title=title,
                caption=f"🎧 {title}\n✅ Downloaded successfully!"
            )
            
            # ပို့ပြီးရင် အမှိုက်ရှင်းမယ်
            await status.delete()
            if os.path.exists(path): 
                os.remove(path)

    except Exception as e:
        await status.edit(f"❌ Error: {str(e)}")

# Bot ကို စတင်မယ်
if __name__ == "__main__":
    app.run()
