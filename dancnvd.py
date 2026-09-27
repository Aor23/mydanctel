import os
import telebot
from openai import OpenAI
from flask import Flask
import threading

# လုံခြုံရေးအတွက် Token များကို Environment မှတဆင့် လှမ်းခေါ်ခြင်း
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# သင့် Group ID နှင့် Topic ID
ALLOWED_GROUP_ID = -1004424706597
ALLOWED_TOPIC_ID = 2

# Render တွင် Bot အိပ်မသွားစေရန် Web Server အသေးစားဖန်တီးခြင်း
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running smoothly!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def auto_reply(message):
    # သတ်မှတ်ထားသော Group နှင့် Topic မဟုတ်ပါက စာမပြန်ဘဲ အဆုံးသတ်မည်[cite: 2]
    if message.chat.id != ALLOWED_GROUP_ID or message.message_thread_id != ALLOWED_TOPIC_ID:
        return
    
    # Bot ဘက်မှ စာရိုက်နေကြောင်း ပြသရန်[cite: 2]
    bot.send_chat_action(message.chat.id, 'typing', message_thread_id=message.message_thread_id)
    
    try:
        response = client.chat.completions.create(
            model="nvidia/nemotron-3-ultra-550b-a55b:free",
            messages=[
                {"role": "system", "content": "You are a helpful and friendly assistant."},
                {"role": "user", "content": message.text}
            ]
        )
        reply_text = response.choices[0].message.content
        
    except Exception as e:
        reply_text = "ဆာဗာချိတ်ဆက်မှု အနည်းငယ် နှေးနေပါတယ်။ ခဏနေမှ ထပ်မေးကြည့်ပါဗျာ။"
        
    # သက်ဆိုင်ရာ Topic ထဲသို့သာ အလိုအလျောက် ပြန်လည်ပေးပို့မည်[cite: 2]
    bot.reply_to(message, reply_text)

if __name__ == "__main__":
    print("Starting web server...")
    # Web server ကို နောက်ကွယ် (Thread) ကနေ Run မည်
    threading.Thread(target=run_web).start()
    
    print("Bot is running in specific topic...")
    # Timeout ပြဿနာကို ကာကွယ်ရန် အချိန်တိုးထားခြင်း
    bot.infinity_polling(timeout=60)
