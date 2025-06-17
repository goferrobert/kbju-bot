# Fitness Progress Tracking Bot

Telegram bot for tracking fitness progress, body measurements, and training activities.

## Features

- User registration with detailed profile
- Body measurements tracking (weight, waist, neck, hip)
- Body fat percentage calculation
- Daily steps tracking
- Training activity logging
- Goal setting and progress tracking
- Customizable notifications
- Statistics and progress reports

## Requirements

- Python 3.8+
- PostgreSQL database
- Telegram Bot Token

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fitness-bot
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with configuration:
```env
BOT_TOKEN=your_telegram_bot_token
DB_URL=postgresql://user:password@localhost:5432/fitness_bot
LOG_LEVEL=INFO
```

5. Initialize database:
```bash
python -m app.db.init
```

## Usage

1. Start the bot:
```bash
python -m app.bot.application
```

2. Open Telegram and start a chat with your bot
3. Follow the registration process to set up your profile
4. Use the menu buttons to access different features

## Commands

- `/start` - Start the bot or show main menu
- `/stats` - Show your statistics
- `/goals` - Manage your goals
- `/settings` - Configure bot settings
- `/notifications` - Manage notifications
- `/help` - Show help information
- `/cancel` - Cancel current operation

## Development

### Project Structure

```
fitness-bot/
├── app/
│   ├── bot/
│   │   ├── application.py
│   │   └── handler.py
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── init.py
│   └── utils/
│       ├── calculations.py
│       ├── config.py
│       ├── logger.py
│       ├── messages.py
│       ├── validation.py
│       └── cache.py
├── logs/
├── .env
├── requirements.txt
└── README.md
```

### Adding New Features

1. Create necessary database models in `app/db/models.py`
2. Add validation functions in `app/utils/validation.py`
3. Add calculation functions in `app/utils/calculations.py`
4. Add message templates in `app/utils/messages.py`
5. Add handlers in `app/bot/handler.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 