import subprocess
import re

from telegram.ext import Application, CommandHandler, MessageHandler, filters


# Telegram bot token
TOKEN = "6199764187:AAEtT1Ubg7gGHqhvhWySO0LggoGVktLfPdg"
BOT_USERNAME = "@find_mil_gear_ua_bot"

# Commands
async def start(update, context):
    await update.message.reply_text(
        "<b>Надішли назву товару для пошуку</b>\nНаприклад: <i>сумка скидання</i>",
        parse_mode='html'
        )

# Responses
def handle_response(text):
    
    if text != '':
        # Replace multiple consecutive whitespaces with a single one and then apply some other transformations
        processed = re.sub(r'\s+', ' ', text).strip().lower().replace(' ','_')
        print(f"Searсhing for {processed}")
        
        # Store the result
        result = subprocess.run(
            ["python", "scraper.py", "-v", "-n", processed],
            capture_output=True,
            text=True,
            encoding="utf-8"
            )
        # Return terminal output
        return result.stdout
    
    
async def handle_message(update, context):
    message_type = update.message.chat.type
    text = update.message.text
    
    print(f"User ({update.message.chat.id}) in {message_type}: '{text}'")

    # Bot within a group will respond only when mentioned, i.e. @find_mil_gear_ua_bot сумка скидання
    if message_type == 'group' or 'supergroup':
        print('In-group bot use')
        if BOT_USERNAME in text:
            await update.message.reply_text("🚀 Пошук...")
            new_text = text.replace(BOT_USERNAME, '').strip()
            response = handle_response(new_text)
        else:
            return
    else:
        await update.message.reply_text("🚀 Пошук...")
        # Leave only this and delete the rest of loop to respond to every message
        # even when not mentioned with @
        response = handle_response(text)
        
    print('Bot:', response)
    
    await update.message.reply_text(response, disable_web_page_preview=True, parse_mode='html')
    
    
async def error(update, context):
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Errors 
    app.add_error_handler(error)
    
    # Check for updates
    print('Polling...')
    app.run_polling(poll_interval=3)  # seconds