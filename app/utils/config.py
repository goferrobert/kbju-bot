import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

class Config:
    """Application configuration manager."""
    
    def __init__(self, env_file: str = '.env'):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file
        """
        # Load environment variables
        load_dotenv(env_file)
        
        # Bot settings
        self.bot_token = os.getenv('BOT_TOKEN')
        self.bot_username = os.getenv('BOT_USERNAME')
        
        # Database settings
        self.db_url = os.getenv('DATABASE_URL')
        
        # Logging settings
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_dir = os.getenv('LOG_DIR', 'logs')
        
        # Notification settings
        self.notification_interval = int(os.getenv('NOTIFICATION_INTERVAL', '60'))  # minutes
        
        # Validation settings
        self.min_age = int(os.getenv('MIN_AGE', '12'))
        self.max_age = int(os.getenv('MAX_AGE', '100'))
        self.min_height = float(os.getenv('MIN_HEIGHT', '100'))
        self.max_height = float(os.getenv('MAX_HEIGHT', '250'))
        self.min_weight = float(os.getenv('MIN_WEIGHT', '30'))
        self.max_weight = float(os.getenv('MAX_WEIGHT', '300'))
        
        # Activity settings
        self.min_steps = int(os.getenv('MIN_STEPS', '0'))
        self.max_steps = int(os.getenv('MAX_STEPS', '100000'))
        self.steps_goal = int(os.getenv('STEPS_GOAL', '10000'))
        
        # Training settings
        self.min_training_frequency = int(os.getenv('MIN_TRAINING_FREQUENCY', '0'))
        self.max_training_frequency = int(os.getenv('MAX_TRAINING_FREQUENCY', '7'))
        self.min_training_duration = int(os.getenv('MIN_TRAINING_DURATION', '15'))  # minutes
        self.max_training_duration = int(os.getenv('MAX_TRAINING_DURATION', '180'))  # minutes
        
        # Message settings
        self.message_timeout = int(os.getenv('MESSAGE_TIMEOUT', '300'))  # seconds
        self.max_message_length = int(os.getenv('MAX_MESSAGE_LENGTH', '4096'))
        
        # Cache settings
        self.cache_ttl = int(os.getenv('CACHE_TTL', '3600'))  # seconds
        self.cache_max_size = int(os.getenv('CACHE_MAX_SIZE', '1000'))
        
        # Security settings
        self.allowed_users = os.getenv('ALLOWED_USERS', '').split(',')
        self.admin_users = os.getenv('ADMIN_USERS', '').split(',')
        
        # Feature flags
        self.enable_notifications = os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'
        self.enable_statistics = os.getenv('ENABLE_STATISTICS', 'true').lower() == 'true'
        self.enable_goals = os.getenv('ENABLE_GOALS', 'true').lower() == 'true'
        self.enable_preferences = os.getenv('ENABLE_PREFERENCES', 'true').lower() == 'true'
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        setattr(self, key, value)
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        required_settings = [
            'bot_token',
            'bot_username',
            'db_url'
        ]
        
        for setting in required_settings:
            if not getattr(self, setting):
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary with configuration values
        """
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }

# Create default configuration instance
config = Config() 