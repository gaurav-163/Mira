"""
Centralized Logging Configuration
Provides consistent logging across the application
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


class LoggerConfig:
    """Centralized logger configuration"""
    
    LOG_DIR = Path(__file__).parent.parent.parent / "logs"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    @classmethod
    def setup_logger(
        cls,
        name: str,
        level: int = logging.INFO,
        log_to_file: bool = True,
        log_to_console: bool = True
    ) -> logging.Logger:
        """
        Setup a logger with file and console handlers
        
        Args:
            name: Logger name (usually __name__)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file
            log_to_console: Whether to log to console
            
        Returns:
            Configured logger instance
        """
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatters
        formatter = logging.Formatter(cls.LOG_FORMAT, cls.DATE_FORMAT)
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if log_to_file:
            cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
            
            # Main application log
            app_log_file = cls.LOG_DIR / "app.log"
            file_handler = RotatingFileHandler(
                app_log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            # Error log (only ERROR and above)
            error_log_file = cls.LOG_DIR / "error.log"
            error_handler = RotatingFileHandler(
                error_log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            logger.addHandler(error_handler)
        
        return logger


def get_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger instance
    
    Args:
        name: Logger name (defaults to caller's module name)
        level: Logging level
        
    Returns:
        Configured logger
    """
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals['__name__']
    
    return LoggerConfig.setup_logger(name, level)


# Pre-configured loggers for common use cases
def get_api_logger() -> logging.Logger:
    """Get logger for API/routes"""
    return get_logger("api")


def get_service_logger() -> logging.Logger:
    """Get logger for services"""
    return get_logger("service")


def get_core_logger() -> logging.Logger:
    """Get logger for core modules"""
    return get_logger("core")
