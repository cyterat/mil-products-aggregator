import asyncio
import string
import csv
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

import regex
from telegram import Chat
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.error import BadRequest


# Load secret .env file
load_dotenv()

# Telegram bot token
TOKEN = os.getenv('TOKEN')
BOT_USERNAME = '@find_mil_gear_ua_bot'

# Create logs path
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
# Create a translation table to replace whitespace (for console command compatibility)
table = str.maketrans(' ', '_', string.ascii_uppercase)

# Store data output path
data_dir = os.path.join('data','data.csv')

def append_to_csv(data_dir, chat_id):
    """
    Appends a new row with 'chat_id' and current timestamp to a CSV file.

    Parameters:
        - data_dir (str): The path to the CSV file.
        - chat_id: The chat ID value to be appended to the CSV file.

    If the CSV file does not exist, it will be created with a header row containing 'chat_id' and 'timestamp'.
    If the file already exists, a new row will be appended with the provided 'chat_id' and the current date and time.

    Example:
        append_to_csv('path/to/your/file.csv', '123456')
    """
    # Check if the file exists to determine whether to write the header
    file_exists = os.path.isfile(data_dir)
    
    # Get current date and time
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(data_dir, mode='a', newline='') as f:
        writer = csv.writer(f)

        # Write header if the file is newly created
        if not file_exists:
            writer.writerow(['chat_id', 'timestamp'])

        # Write the chat_id and timestamp
        writer.writerow([chat_id, current_datetime])


# Define a User class to store user-specific data
class User:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.searching = False
        self.search_result = ""


# Command to handle the /start command
async def start(update, context):
    await update.message.reply_text(
        "<b>Надішли назву товару для пошуку</b>\nНаприклад: <i>мультитул leatherman</i>",
        parse_mode='html'
    )


# Function to handle the response after searching for a product
async def handle_response(user, text):

    if (text != '') and (text.isspace() == False) and (len(text) != 1):
        processed = pattern.sub(' ', text.lower()).strip().translate(table)
        logging.debug(f"Searching for {processed}")

        # Run the scraper subprocess to get the search result
        result = await asyncio.create_subprocess_exec(
            "python", os.path.join("event_processors","scraper.py"), "-v", "-n", processed,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await result.communicate()
        user.search_result = stdout.decode('utf-8')
        user.searching = False


# Function to handle incoming messages
async def handle_message(update, context):
    message_type = update.message.chat.type
    text = update.message.text
    chat_id = update.message.chat_id
    
    # Record chat_id for general bot use statistics purposes
    append_to_csv(data_dir,chat_id)

    # Retrieve or create a User object for the current chat_id
    user = context.user_data.get(chat_id)
    if not user:
        user = User(chat_id)
        context.user_data[chat_id] = user

    # Check the message type and respond accordingly
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
        logging.error("Unsupported message type:", message_type)

    # If the search is completed, send the search result
    if not user.searching:
        await update.message.reply_text(
            user.search_result, 
            disable_web_page_preview=True, 
            parse_mode='html'
            )


# Function to handle errors
async def error(update, context):
    # Store error message
    error = context.error
    
    if isinstance(error, BadRequest) and error.message == "Forbidden: bot was blocked by the user":
        logging.warning(f"The user {update.effective_chat.id} has blocked the bot")
    elif "Message text is empty" in error.message:
        logging.debug(f"{update} message was empty")
        await update.message.reply_text(
            "⚠ <b>Повідомлення повинне містити назву товару для пошуку</b>",
            parse_mode='html'
            )
    else:
        logging.critical(f"{update} caused an error: {context.error}")


# Main block to run the bot
if __name__ == "__main__":  
    print('▢ Starting bot...')
    # Create the bot
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()

    # Add handlers for the /start command, incoming text messages, and errors
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    print('▣ Polling...')
    # Check for new user messages
    app.run_polling(poll_interval=3)  # seconds
