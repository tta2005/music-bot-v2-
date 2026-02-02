import telebot
import os
import yt_dlp
import time

# Render Settings ထဲက BOT_TOKEN ကို လှမ်းယူတာ
API_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "အောင်ပြီ သားကြီး! Bot အခု အလုပ်လုပ်နေပြီ။ သီချင်းနာမည် ပို့ပေးပါ။")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    status_msg = bot.reply_to(message, "🔎 ရှာနေတယ် ခဏစောင့်...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            video_info = info['entries'][0]
            file_path = ydl.prepare_filename(video_info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

            bot.edit_message_text("📤 ပို့နေပြီ...", message.chat.id, status_msg.message_id)
            
            with open(file_path, 'rb') as audio:
                bot.send_audio(message.chat.id, audio, title=video_info['title'])
            
            if os.path.exists(file_path):
                os.remove(file_path)
            
            bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    print("Bot is starting...")
    # Infinity polling သုံးထားရင် error တက်လည်း သူ့ဘာသာ ပြန်ပတ်ပေးတယ်
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
