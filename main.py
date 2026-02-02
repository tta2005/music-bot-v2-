import os
import requests
from pyrogram import Client, filters

# Environment Variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("🚀 Music Bot အသစ် အဆင်သင့်ဖြစ်ပြီ!\nYouTube မသုံးဘဲ တိုက်ရိုက်ရှာပေးမှာမို့လို့ အခုပဲ သီချင်းနာမည် ပို့လိုက်ပါ။")

@app.on_message(filters.text & ~filters.command(["start"]))
async def download_song(client, message):
    song_name = message.text
    sent_message = await message.reply_text(f"🔍 '{song_name}' ကို အခြား Server မှာ ရှာနေတယ်...")

    try:
        # YouTube အစား အခြား Music API တစ်ခုကို သုံးပြီး ရှာခြင်း
        search_url = f"https://saavn.dev/api/search/songs?query={song_name}"
        response = requests.get(search_url).json()

        if response.get('success') and response['data']['results']:
            song_data = response['data']['results'][0]
            download_url = song_data['downloadUrl'][4]['link'] # High quality link
            file_name = f"{song_data['name']}.mp3"

            # သီချင်းကို တိုက်ရိုက် ဒေါင်းခြင်း
            audio_data = requests.get(download_url).content
            with open(file_name, 'wb') as f:
                f.write(audio_data)

            # Telegram ဆီ ပို့ခြင်း
            await message.reply_audio(audio=open(file_name, 'rb'), title=song_data['name'], performer=song_data['artists']['primary'][0]['name'])
            await sent_message.delete()
            os.remove(file_name)
        else:
            await sent_message.edit("❌ သီချင်း ရှာမတွေ့ပါဘူး။")

    except Exception as e:
        await sent_message.edit(f"❌ Error: {str(e)}")

app.run()
