"""
Logging utilities for the test platform.
Provides standardized logging configuration and utilities.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class Logger:
    """Centralized logging configuration and management."""
    
    _loggers = {}
    _configured = False
    
    @classmethod
    def configure_logging(cls, 
                         level: str = "INFO",
                         log_dir: Optional[str] = None,
                         log_file: Optional[str] = None,
                         format_string: Optional[str] = None) -> None:
        """Configure global logging settings."""
        if cls._configured:
            return
            
        # Default format
        if format_string is None:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # Create formatter
        formatter = logging.Formatter(format_string)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler if specified
        if log_dir or log_file:
            if log_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = f"test_platform_{timestamp}.log"
            
            if log_dir is None:
                log_dir = "logs"
            
            # Ensure log directory exists
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            file_path = os.path.join(log_dir, log_file)
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance with the given name."""
        if not cls._configured:
            cls.configure_logging()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]


def get_logger(name: str = __name__) -> logging.Logger:
    """Convenience function to get a logger instance."""
    return Logger.get_logger(name)