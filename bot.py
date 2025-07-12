# ---------------------------------------------------
# 🤖 Telegram Chat Bot using DeepSeek API
# Created by Rajdev (@raj_dev_01)
# ✅ Includes Force Subscribe & Multilingual Support
# ---------------------------------------------------

import os
import random
import requests
from telegram import Update, ChatAction, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.error import BadRequest

# 🔐 API keys from environment
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 🔗 Force subscription channel (must be PUBLIC)
FORCE_CHANNEL = "https://t.me/+eMw2ExVt0P04ZGVl"  # Replace with your public channel username

# 🌐 DeepSeek API configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
emojis = ['🤖', '✨', '💡', '🤔', '😎', '🔥']

# 🌍 Store selected language per user
user_languages = {}

# ✅ Check if user is subscribed to the required channel
def is_user_subscribed(user_id, context):
    try:
        member = context.bot.get_chat_member(chat_id=FORCE_CHANNEL, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except BadRequest:
        return False

# ✅ /start command
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_user_subscribed(user_id, context):
        update.message.reply_text(
            f"🔒 Please join the required channel first:\n{FORCE_CHANNEL}\nThen come back and use the bot."
        )
        return

    update.message.reply_text("👋 Hello! I'm a smart chatbot powered by DeepSeek AI.\nMade by @raj_dev_01")

# ✅ /language command – to let users choose their preferred language
def language_command(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("🇮🇳 Hindi"), KeyboardButton("🇬🇧 English"), KeyboardButton("🇧🇩 Bangla")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("🌐 Please choose your preferred language:", reply_markup=reply_markup)

# ✅ /refresh command – allows user to retry after joining the channel
def refresh(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if is_user_subscribed(user_id, context):
        update.message.reply_text("✅ Thank you! You're now verified. You can use the bot.")
    else:
        update.message.reply_text(f"❌ You're still not subscribed to:\n{FORCE_CHANNEL}")

# ✅ /help command
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🛠 *Help Menu*\n"
        "• Send me any message\n"
        "• I will reply using DeepSeek AI\n"
        "• To change language: use /language\n\n"
        "🔗 Created by @raj_dev_01",
        parse_mode="Markdown"
    )

# ✅ /creator command
def creator_command(update: Update, context: CallbackContext):
    update.message.reply_text("🙋‍♂️ I was created by *Rajdev* (@raj_dev_01)", parse_mode="Markdown")

# ✅ /about command
def about_command(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 I am an AI-powered chatbot using DeepSeek API. Multilingual and smart!")

# ✅ Main message handler
def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_msg = update.message.text.strip()

    if not is_user_subscribed(user_id, context):
        update.message.reply_text(f"🔒 Please join the required channel first:\n{FORCE_CHANNEL}")
        return

    if user_msg in ["🇮🇳 Hindi", "🇬🇧 English", "🇧🇩 Bangla"]:
        if user_msg == "🇮🇳 Hindi":
            user_languages[user_id] = "Hindi"
        elif user_msg == "🇧🇩 Bangla":
            user_languages[user_id] = "Bengali"
        else:
            user_languages[user_id] = "English"
        update.message.reply_text(f"✅ Language set to: {user_msg}")
        return

    emoji = random.choice(emojis)
    update.message.reply_text(emoji)
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    selected_language = user_languages.get(user_id, "English")
    prompt = f"Reply to this message in {selected_language}:\n{user_msg}"

    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }

        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        reply_text = data['choices'][0]['message']['content'].strip()
    except Exception as e:
        reply_text = f"❌ Error: {str(e)}"

    update.message.reply_text(f"{reply_text}\n\n🔖 _Powered by @raj_dev_01_", parse_mode="Markdown")

# ✅ Welcome message for new group members
def welcome(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"👋 Welcome {member.first_name}!\nPlease join {FORCE_CHANNEL} to use this bot.",
            parse_mode="Markdown"
        )

# ✅ Main function
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("creator", creator_command))
    dp.add_handler(CommandHandler("about", about_command))
    dp.add_handler(CommandHandler("language", language_command))
    dp.add_handler(CommandHandler("refresh", refresh))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
