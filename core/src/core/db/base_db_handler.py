"""
Base database handler providing common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager

from ..base_util.logger import get_logger
from ..base_util.exception_handler import BaseTestException

logger = get_logger(__name__)


class DatabaseError(BaseTestException):
    """Exception raised for database operation errors."""
    pass


class BaseDBHandler(ABC):
    """Abstract base class for database handlers."""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.config = connection_config
        self.connection = None
        self._connected = False
    
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if database connection is active."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a database query."""
        pass
    
    def reconnect(self) -> None:
        """Reconnect to the database."""
        logger.info("Reconnecting to database...")
        self.disconnect()
        self.connect()
    
    @contextmanager
    def connection_context(self):
        """Context manager for database connections."""
        was_connected = self.is_connected()
        
        if not was_connected:
            self.connect()
        
        try:
            yield self
        finally:
            if not was_connected:
                self.disconnect()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        if exc_type:
            logger.error(f"Database operation failed: {exc_val}")
        return False