import telebot
import os
import yt_dlp
import time

# Koyeb Environment Variable ကနေ Token ကိုယူမယ်
API_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Koyeb ပေါ်မှာ Bot အသက်ဝင်နေပြီ သားကြီး! သီချင်းနာမည် ပို့ပေးပါ။")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    status_msg = bot.reply_to(message, f"🔎 '{query}' ကို ရှာနေတယ်...")
    
    # YouTube Block တာကျော်ဖို့ Bypass Settings များ
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'cookiefile': 'cookies.txt', # မင်းထည့်ထားတဲ့ Cookies ကို သုံးမယ်
        'nocheckcertificate': True,
        'geo_bypass': True,
        'source_address': '0.0.0.0', # IPv6 ပြဿနာကျော်ဖို့
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ဗီဒီယိုအချက်အလက်ကို အရင်ရှာမယ်
            search_result = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if not search_result['entries']:
                bot.edit_message_text("❌ ရှာမတွေ့ဘူး သားကြီး။", message.chat.id, status_msg.message_id)
                return

            video_info = search_result['entries'][0]
            title = video_info['title']
            url = video_info['webpage_url']
            
            bot.edit_message_text(f"🎵 {title}\n🔗 {url}\n\nအခု ဒေါင်းလုဒ်စနေပြီ၊ ခဏစောင့်...", message.chat.id, status_msg.message_id)
            
            # ဒေါင်းလုဒ်လုပ်မယ့် Configuration
            ydl_opts['outtmpl'] = f'downloads/{int(time.time())}_%(title)s.%(ext)s'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            
            if not os.path.exists('downloads'): os.makedirs('downloads')
            
            # ဒေါင်းလုဒ်အမှန်တကယ်လုပ်မယ်
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
            # Telegram ဆီ ပို့မယ်
            with open(file_path, 'rb') as audio:
                bot.send_audio(message.chat.id, audio, title=title)
            
            # ပို့ပြီးရင် ဖိုင်ပြန်ဖျက်မယ်
            os.remove(file_path)
            bot.delete_message(message.chat.id, status_msg.message_id)
            
    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm" in error_msg:
             bot.edit_message_text("❌ YouTube က Block ထားတုန်းပဲ သားကြီး။ Cookies အသစ်ပြန်ထည့်ကြည့်ပါ။", message.chat.id, status_msg.message_id)
        else:
             bot.edit_message_text(f"❌ Error: {error_msg}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
