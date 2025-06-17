import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from app.bot.handler import BotHandler
from app.db.database import Database
from app.utils.config import config
from app.utils.logger import logger

class BotApplication:
    """Main bot application class."""
    
    def __init__(self):
        """Initialize bot application."""
        # Initialize database
        self.db = Database(config.get('db_url'))
        self.db.create_tables()
        
        # Initialize bot handler
        self.handler = BotHandler(self.db)
        
        # Initialize application
        self.application = Application.builder().token(config.get('bot_token')).build()
        
        # Add handlers
        self.application.add_handler(self.handler.conversation_handler)
        self.application.add_handler(CallbackQueryHandler(self.handler.handle_callback))
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)
    
    async def error_handler(self, update, context):
        """Handle errors."""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже."
            )
    
    def run(self):
        """Run the bot."""
        logger.info("Starting bot...")
        self.application.run_polling()
    
    def stop(self):
        """Stop the bot."""
        logger.info("Stopping bot...")
        self.application.stop()

def main():
    """Main entry point."""
    # Create and run application
    app = BotApplication()
    try:
        app.run()
    except KeyboardInterrupt:
        app.stop()
    except Exception as e:
        logger.error(f"Error running application: {str(e)}")
        app.stop()

if __name__ == '__main__':
    main() 