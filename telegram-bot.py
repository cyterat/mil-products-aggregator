import asyncio
import string
import os
import logging
from dotenv import load_dotenv

import regex
from telegram import Chat
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.error import BadRequest

from lib import generate_formatted_output


# Load secret .env file
load_dotenv()

# Set telegram bot token and name
TOKEN = os.getenv('TELEGRAM_TOKEN')
BOT_USERNAME = '@find_mil_gear_ua_bot'


# Ensure the logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

log_file_path = os.path.join('logs', 'telegram-bot.log')

# Set up logging
logging.basicConfig(
    filename=log_file_path,
    level=logging.WARNING,
    encoding='utf-8',
    filemode='a',
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Compile the regular expression pattern
pattern = regex.compile(r'\P{Alnum}+')


# Define a User class to store user-specific data
class User:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.searching = False
        self.search_result = ""


# Handle the /start command
async def start(update, context):
    await update.message.reply_text(
        "<b>Надішли назву товару для пошуку</b>\nНаприклад: <i>мультитул leatherman</i>",
        parse_mode='html'
    )


# Handle user request
async def handle_response(user, text):
    logging.debug(f"Raw input: text {text}")
    processed = pattern.sub(' ', text.lower()).strip()
    logging.debug(f"Processed input: {processed}")

    # Check if processed text is empty or whitespace only
    if not processed or processed.isspace() or len(processed) < 2:
        logging.error("Invalid input received.")
        user.search_result = "⚠ <b>Повідомлення повинне містити назву товару для пошуку</b>"
        user.searching = False
        return

    try:
        # Call the asynchronous scraper function directly
        formatted_message = await generate_formatted_output(processed)
        user.search_result = formatted_message
    except Exception as e:
        logging.critical(f"Error during scraping process: {e}")
        user.search_result = "⚠ <b>Сталася помилка під час пошуку. Спробуйте ще раз пізніше.</b>"

    user.searching = False
    
    
# Handle reply message
async def handle_message(update, context):
    message_type = update.message.chat.type
    text = update.message.text
    chat_id = update.message.chat_id

    user = context.user_data.get(chat_id)
    if not user:
        user = User(chat_id)
        context.user_data[chat_id] = user

    try:
        if message_type in (Chat.GROUP, Chat.SUPERGROUP, Chat.CHANNEL):
            if BOT_USERNAME in text:
                logging.debug('\nGroup chat bot use')
                logging.debug(f"\nUser ({update.message.chat.id}) in {message_type}")
                
                await update.message.reply_text(
                    "🐾 <b>Пошук...</b>\n<i>Процес може тривати ~1 хв</i>",
                    parse_mode='html'
                )
                new_text = text.replace(BOT_USERNAME, '').strip()
                user.searching = True
                await asyncio.gather(handle_response(user, new_text))
            else:
                return
        elif message_type == Chat.PRIVATE:
            logging.debug('\nPrivate chat bot use')
            logging.debug(f"\nUser ({update.message.chat.id}) in {message_type}")
            
            await update.message.reply_text(
                "🐾 <b>Пошук...</b>\n<i>Процес може тривати ~1 хв</i>",
                parse_mode='html'
            )
            user.searching = True
            await asyncio.gather(handle_response(user, text))
        else:
            logging.error(f"Unsupported message type: {message_type}")

        # Always send the search result, even if the input was invalid
        if not user.searching:
            logging.debug(f"Search completed for user ({update.message.chat.id})")
            logging.debug(f"Search result: {user.search_result}")
            await update.message.reply_text(
                user.search_result, 
                disable_web_page_preview=True, 
                parse_mode='html'
            )
    except Exception as e:
        logging.critical(f"An error occurred in handle_message: {e}")
        await update.message.reply_text(
            "⚠ <b>Сталася помилка під час обробки вашого запиту.</b>",
            parse_mode='html'
        )


# Handle errors
async def error(update, context):
    error = context.error
    logging.critical(f"An error occurred: {error}")

    if isinstance(error, BadRequest) and "Forbidden: bot was blocked by the user" in error.message:
        logging.warning(f"The user {update.effective_chat.id} has blocked the bot")
    elif "Message text is empty" in error.message:
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text(
                "⚠ <b>Повідомлення повинне містити назву товару для пошуку</b>",
                parse_mode='html'
            )
    else:
        logging.critical(f"An error occurred: {error}")
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text(
                "⚠ <b>Сталася помилка під час обробки вашого запиту.</b>",
                parse_mode='html'
            )



if __name__ == "__main__":
    print('▢ Starting bot...')
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    print('▣ Polling...')
    app.run_polling(poll_interval=3)