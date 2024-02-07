import asyncio
import re
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Chat, BadRequest

# Load secret .env file
load_dotenv()

# Telegram bot token
TOKEN = os.getenv('TOKEN')
BOT_USERNAME = '@find_mil_gear_ua_bot'

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
    if (text != '') and (text.isspace()==False) and (len(text)!=1):
        processed = re.sub(r'\s+', ' ', text).strip().lower().replace(' ', '_').replace('-', '_')
        print(f"Searching for {processed}")

        # Run the scraper subprocess to get the search result
        result = await asyncio.create_subprocess_exec(
            "python", "scraper.py", "-v", "-n", processed,
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

    # Retrieve or create a User object for the current chat_id
    user = context.user_data.get(chat_id)
    if not user:
        user = User(chat_id)
        context.user_data[chat_id] = user

    # Check the message type and respond accordingly
    if message_type in (Chat.GROUP, Chat.SUPERGROUP, Chat.CHANNEL):
        if BOT_USERNAME in text:
            print('\nGroup chat bot use')
            print(f"User ({update.message.chat.id}) in {message_type}")
            
            await update.message.reply_text(
                "🐾 <b>Пошук...</b>\n<i>Час очікування: ~1 хв</i>",
                parse_mode='html'
                )
            new_text = text.replace(BOT_USERNAME, '').strip()
            user.searching = True
            await asyncio.gather(handle_response(user, new_text))
        else:
            return
    elif message_type == Chat.PRIVATE:
        print('\nPrivate chat bot use')
        print(f"User ({update.message.chat.id}) in {message_type}")
        
        await update.message.reply_text(
            "🐾 <b>Пошук...</b>\n<i>Час очікування: ~1 хв</i>",
            parse_mode='html'
            )
        user.searching = True
        await asyncio.gather(handle_response(user, text))
    else:
        print("Unsupported message type:", message_type)

    # If the search is completed, send the search result
    if not user.searching:
        await update.message.reply_text(
            user.search_result, 
            disable_web_page_preview=True, 
            parse_mode='html'
            )

# Function to handle errors
async def error(update, context):
    error = context.error
    if isinstance(error, BadRequest) and error.message == "Forbidden: bot was blocked by the user":
        print(f"The user {update.effective_chat.id} has blocked the bot")
    else:
        print(f"{update} caused error {context.error}")

# Main block to run the bot
if __name__ == "__main__":
    print('▢ Starting bot...')
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()

    # Add handlers for the /start command, incoming text messages, and errors
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    print('▣ Polling...')
    app.run_polling(poll_interval=3)  # seconds
