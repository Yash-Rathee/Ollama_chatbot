import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import threading
from flask import Flask

load_dotenv()

TOKEN = os.getenv("TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def ask_llm(prompt):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "meta-llama/llama-3.1-8b-instruct",
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
        }
    )

    return response.json()["choices"][0]["message"]["content"]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.chat.send_action("typing")
    reply = ask_llm(user_text)
    await update.message.reply_text(reply[:4000])

# --- Telegram bot ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

def run_bot():
    app.run_polling()

# --- Flask app ---
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Hades is running 🔥"

# --- Main ---
if __name__ == "__main__":
    print("Starting bot + Flask...")

    t = threading.Thread(target=run_bot)
    t.start()

    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)
