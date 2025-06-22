from app.bot.application import BotApplication
from app.utils.logger import logger

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
