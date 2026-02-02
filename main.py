import telebot
import os
import yt_dlp

# Koyeb က Environment Variable ကို ယူမယ်
API_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Koyeb ပေါ်မှာ Bot အသက်ဝင်နေပြီ သားကြီး! သီချင်းနာမည် ပို့ပေးပါ။")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    status_msg = bot.reply_to(message, "🔎 ရှာနေတယ်...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            video_info = info['entries'][0]
            title = video_info['title']
            url = video_info['webpage_url']
            
            bot.edit_message_text(f"🎵 {title}\n🔗 {url}\n\nအခု ဒေါင်းလုဒ်စနေပြီ၊ ခဏစောင့်...", message.chat.id, status_msg.message_id)
            
            # ဒေါင်းတဲ့အပိုင်း
            ydl_opts['download'] = True
            ydl_opts['outtmpl'] = 'downloads/%(title)s.%(ext)s'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
            
            if not os.path.exists('downloads'): os.makedirs('downloads')
            ydl.download([url])
            
            file_path = f"downloads/{title}.mp3" # ရိုးရိုးရှင်းရှင်းပဲ နာမည်ပေးလိုက်မယ်
            
            with open(file_path, 'rb') as audio:
                bot.send_audio(message.chat.id, audio, title=title)
            
            os.remove(file_path)
            bot.delete_message(message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
