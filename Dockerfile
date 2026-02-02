FROM python:3.10-slim

# FFmpeg နှင့် လိုအပ်သည်များ သွင်းခြင်း
RUN apt-get update && apt-get install -y ffmpeg git && apt-get clean

WORKDIR /app
COPY . .

# Dependencies များ သွင်းခြင်း
RUN pip install --no-cache-dir -r requirements.txt

# Bot ကို နှိုးခြင်း
CMD ["python", "main.py"]
