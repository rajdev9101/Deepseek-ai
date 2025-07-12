# --------------------------------------------------------
# 🤖 Telegram Bot + OpenAI Integration
# Created by: Rajdev (@raj_dev_01)
# --------------------------------------------------------

import os
import random
import openai
from telegram import Update, ChatAction, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# API Keys (from Koyeb environment)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Emoji options
emojis = ['🤖', '✨', '💡', '🤔', '😎', '🔥']

# Supported languages
LANGUAGES = {
    "English": "✅ Language set to English. You can chat with me freely.",
    "हिन्दी": "✅ भाषा हिंदी सेट कर दी गई है। अब आप मुझसे हिंदी में बात कर सकते हैं।",
    "বাংলা": "✅ ভাষা বাংলা সেট করা হয়েছে। এখন আপনি বাংলায় কথা বলতে পারেন।"
}

# Store user language preferences
user_languages = {}

# /start command
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_languages[chat_id] = "English"
    context.bot.send_message(chat_id=chat_id, text="👋 Hello! I'm your AI bot powered by OpenAI.\nMade by @raj_dev_01")

# /help command
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("🛠 Just send me any message, and I will reply using OpenAI.\nUse /language to change language.")

# /about command
def about_command(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 I am an AI chatbot using OpenAI's GPT model.\nBuilt and maintained by @raj_dev_01.")

# /creator command
def creator_command(update: Update, context: CallbackContext):
    update.message.reply_text("👨‍💻 Bot Creator: Rajdev (@raj_dev_01)")

# /language command
def language_command(update: Update, context: CallbackContext):
    keyboard = [[KeyboardButton(lang)] for lang in LANGUAGES]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("🌐 Choose your language:", reply_markup=reply_markup)

# Handle language change
def handle_language(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    lang = update.message.text
    if lang in LANGUAGES:
        user_languages[chat_id] = lang
        update.message.reply_text(LANGUAGES[lang])
        return
    handle_message(update, context)

# Main message handler using OpenAI Chat
def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_msg = update.message.text
    emoji = random.choice(emojis)
    context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    update.message.reply_text(emoji)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_msg}
            ]
        )
        reply_text = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        reply_text = "⚠️ Sorry, I couldn't get a reply. Please try again later."

    context.bot.send_message(
        chat_id=chat_id,
        text=f"{reply_text}\n\n🔖 [Powered by @raj_dev_01](https://t.me/raj_dev_01)",
        parse_mode="Markdown"
    )

# Greet new users
def welcome(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"👋 Welcome {member.first_name}! I'm an AI bot. Ask me anything!",
            parse_mode="Markdown"
        )

# Main function
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
    
