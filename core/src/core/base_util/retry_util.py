"""
Retry utilities for handling transient failures in tests.
"""

import time
import functools
from typing import Callable, Type, Tuple, Optional, Any
from dataclasses import dataclass

from .logger import get_logger
from .exception_handler import BaseTestException

logger = get_logger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    delay: float = 1.0
    backoff_factor: float = 2.0
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
    max_delay: float = 30.0


def retry(config: Optional[RetryConfig] = None):
    """
    Decorator to retry function calls on failure.
    
    Args:
        config: RetryConfig instance with retry parameters
        
    Returns:
        Decorated function
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = config.delay
            
            for attempt in range(config.max_attempts):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"{func.__name__} succeeded on attempt {attempt + 1}")
                    return result
                    
                except config.exceptions as e:
                    last_exception = e
                    if attempt < config.max_attempts - 1:
                        logger.warning(
                            f"{func.__name__} failed on attempt {attempt + 1}: {str(e)}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay = min(delay * config.backoff_factor, config.max_delay)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {config.max_attempts} attempts"
                        )
            
            # If we get here, all attempts failed
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


def retry_on_failure(func: Callable, 
                    config: Optional[RetryConfig] = None,
                    *args, **kwargs) -> Any:
    """
    Function-based retry mechanism.
    
    Args:
        func: Function to retry
        config: RetryConfig instance
        *args, **kwargs: Arguments to pass to func
        
    Returns:
        Result of successful function call
    """
    if config is None:
        config = RetryConfig()
    
    decorated_func = retry(config)(func)
    return decorated_func(*args, **kwargs)