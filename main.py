import telebot
import os
import yt_dlp
import time

# Koyeb Environment Variable ကနေ Token ကိုယူမယ်
API_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "SoundCloud Mode အလုပ်လုပ်နေပြီ သားကြီး! သီချင်းနာမည် ပို့ပေးပါ။ (Cookies မလိုတော့ဘူးနော်)")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    status_msg = bot.reply_to(message, f"🔎 SoundCloud မှာ '{query}' ကို ရှာနေတယ်...")
    
    # SoundCloud အတွက် Settings (YouTube Block တာကို ကျော်ဖို့ အကောင်းဆုံးနည်းလမ်း)
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # scsearch ဆိုတာ SoundCloud မှာ ရှာခိုင်းတာပါ
            search_result = ydl.extract_info(f"scsearch1:{query}", download=False)
            
            if not search_result['entries']:
                bot.edit_message_text("❌ SoundCloud မှာ ရှာမတွေ့ဘူး သားကြီး။", message.chat.id, status_msg.message_id)
                return

            video_info = search_result['entries'][0]
            title = video_info['title']
            url = video_info['url']
            
            bot.edit_message_text(f"🎵 {title}\n🔗 Found on SoundCloud\n\nအခု ဒေါင်းလုဒ်စနေပြီ၊ ခဏစောင့်...", message.chat.id, status_msg.message_id)
            
            # ဒေါင်းလုဒ်ဖိုင် သိမ်းမယ့်နေရာ
            file_name = f"downloads/{int(time.time())}.mp3"
            ydl_opts['outtmpl'] = file_name.replace('.mp3', '.%(ext)s')
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            
            if not os.path.exists('downloads'): os.makedirs('downloads')
            
            # အမှန်တကယ် ဒေါင်းလုဒ်လုပ်မယ်
            ydl.download([url])
            
            # Telegram ဆီ ပို့မယ်
            with open(file_name, 'rb') as audio:
                bot.send_audio(message.chat.id, audio, title=title)
            
            # ဖိုင်ပြန်ဖျက်မယ်
            if os.path.exists(file_name): os.remove(file_name)
            bot.delete_message(message.chat.id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
