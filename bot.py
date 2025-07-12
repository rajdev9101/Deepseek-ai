# --------------------------------------------------------
# 🤖 Telegram Bot + DeepSeek Integration
# Created by: Rajdev (@raj_dev_01)
# --------------------------------------------------------

import os
import random
import requests
from telegram import Update, ChatAction, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# API Keys
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# Emoji options
emojis = ['🤖', '✨', '💡', '🤔', '😎', '🔥']

# Language options
LANGUAGES = {
    "English": "Hello! You can now chat with me in English.",
    "हिन्दी": "नमस्ते! अब आप मुझसे हिंदी में बात कर सकते हैं।",
    "বাংলা": "হ্যালো! আপনি এখন বাংলায় আমার সঙ্গে কথা বলতে পারেন।"
}

user_languages = {}

# Start command
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_languages[chat_id] = "English"
    context.bot.send_message(chat_id=chat_id, text=f"👋 Hello! I'm a ChatGPT-style bot.\nMade by @raj_dev_01")

# Help command
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("🛠 Send me any message, and I’ll reply using DeepSeek API.\nUse /language to change language.")

# About command
def about_command(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 I'm an AI-powered bot powered by DeepSeek.\nCreated by @raj_dev_01.")

# Creator command
def creator_command(update: Update, context: CallbackContext):
    update.message.reply_text("👨‍💻 Bot Creator: Rajdev (@raj_dev_01)")

# Language change command
def language_command(update: Update, context: CallbackContext):
    keyboard = [[KeyboardButton(lang)] for lang in LANGUAGES]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("🌐 Choose your language:", reply_markup=reply_markup)

# Handle language selection
def handle_language(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    lang = update.message.text
    if lang in LANGUAGES:
        user_languages[chat_id] = lang
        update.message.reply_text(LANGUAGES[lang])
        return
    handle_message(update, context)

# Main message handler
def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_msg = update.message.text

    emoji = random.choice(emojis)
    context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    update.message.reply_text(emoji)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": user_msg}]
    }

    try:
        response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data)
        result = response.json()
        reply_text = result['choices'][0]['message']['content'].strip()
    except Exception as e:
        reply_text = "⚠️ Sorry, I couldn't get a reply. Please try again later."

    context.bot.send_message(chat_id=chat_id, text=f"{reply_text}\n\n🔖 _Powered by @raj_dev_01_", parse_mode="Markdown")

# Welcome new users (optional)
def welcome(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"👋 Welcome {member.first_name}! Ask me anything.",
            parse_mode="Markdown"
        )

# Start polling
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("about", about_command))
    dp.add_handler(CommandHandler("creator", creator_command))
    dp.add_handler(CommandHandler("language", language_command))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_language))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

