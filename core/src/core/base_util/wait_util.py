"""
Waiting utilities for test synchronization.
"""

import time
from typing import Callable, Any, Optional
from dataclasses import dataclass

from .logger import get_logger
from .exception_handler import TestTimeoutError

logger = get_logger(__name__)


@dataclass
class WaitConfig:
    """Configuration for wait operations."""
    timeout: float = 30.0
    poll_interval: float = 0.5
    ignore_exceptions: bool = True
    error_message: Optional[str] = None


def wait_until(condition: Callable[[], Any], 
               config: Optional[WaitConfig] = None,
               description: str = "condition") -> Any:
    """
    Wait until a condition becomes true/truthy.
    
    Args:
        condition: Function that returns the condition to wait for
        config: WaitConfig instance
        description: Description of what we're waiting for (for logging)
        
    Returns:
        The truthy result returned by condition
        
    Raises:
        TestTimeoutError: If timeout is exceeded
    """
    if config is None:
        config = WaitConfig()
    
    start_time = time.time()
    last_exception = None
    
    logger.info(f"Waiting for {description} (timeout: {config.timeout}s)")
    
    while time.time() - start_time < config.timeout:
        try:
            result = condition()
            if result:
                elapsed = time.time() - start_time
                logger.info(f"{description} achieved after {elapsed:.2f}s")
                return result
        except Exception as e:
            last_exception = e
            if not config.ignore_exceptions:
                raise
            logger.debug(f"Exception while waiting for {description}: {str(e)}")
        
        time.sleep(config.poll_interval)
    
    # Timeout exceeded
    elapsed = time.time() - start_time
    error_msg = config.error_message or f"Timeout waiting for {description} after {elapsed:.2f}s"
    
    if last_exception and not config.ignore_exceptions:
        error_msg += f". Last exception: {str(last_exception)}"
    
    logger.error(error_msg)
    raise TestTimeoutError(error_msg, {"timeout": config.timeout, "elapsed": elapsed})


def wait_for_seconds(seconds: float, description: str = "delay"):
    """Simple sleep with logging."""
    logger.info(f"Waiting for {seconds}s ({description})")
    time.sleep(seconds)


def wait_until_not(condition: Callable[[], Any],
                   config: Optional[WaitConfig] = None,
                   description: str = "condition to be false") -> None:
    """
    Wait until a condition becomes false/falsy.
    
    Args:
        condition: Function that returns the condition to wait to be false
        config: WaitConfig instance
        description: Description of what we're waiting for
    """
    def inverted_condition():
        return not condition()
    
    wait_until(inverted_condition, config, f"NOT {description}")
    return True