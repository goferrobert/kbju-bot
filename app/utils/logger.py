import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
from logging.handlers import RotatingFileHandler

class Logger:
    """Application logger with file and console handlers."""
    
    def __init__(self, name: str, log_dir: str = 'logs'):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # File handler for all logs
        all_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, 'all.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        all_handler.setLevel(logging.DEBUG)
        all_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        all_handler.setFormatter(all_formatter)
        
        # File handler for errors
        error_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, 'error.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
            'File: %(pathname)s:%(lineno)d\n'
            'Function: %(funcName)s\n'
            'Message: %(message)s\n'
            'Exception: %(exc_info)s'
        )
        error_handler.setFormatter(error_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(all_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """
        Log debug message.
        
        Args:
            message: Log message
            **kwargs: Additional context
        """
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """
        Log info message.
        
        Args:
            message: Log message
            **kwargs: Additional context
        """
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """
        Log warning message.
        
        Args:
            message: Log message
            **kwargs: Additional context
        """
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, exc_info: Optional[Exception] = None, **kwargs):
        """
        Log error message.
        
        Args:
            message: Log message
            exc_info: Exception info
            **kwargs: Additional context
        """
        self._log(logging.ERROR, message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, exc_info: Optional[Exception] = None, **kwargs):
        """
        Log critical message.
        
        Args:
            message: Log message
            exc_info: Exception info
            **kwargs: Additional context
        """
        self._log(logging.CRITICAL, message, exc_info=exc_info, **kwargs)
    
    def _log(self, level: int, message: str, exc_info: Optional[Exception] = None, **kwargs):
        """
        Log message with context.
        
        Args:
            level: Log level
            message: Log message
            exc_info: Exception info
            **kwargs: Additional context
        """
        # Add timestamp
        context = {
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        # Format message with context
        if context:
            message = f"{message} | Context: {context}"
        
        # Log message
        if exc_info:
            self.logger.log(level, message, exc_info=exc_info)
        else:
            self.logger.log(level, message)

# Create default logger instance
logger = Logger('fitness_bot') 