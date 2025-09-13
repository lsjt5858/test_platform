"""
Base message queue handler providing common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass

from ..base_util.logger import get_logger
from ..base_util.exception_handler import BaseTestException

logger = get_logger(__name__)


class MessageQueueError(BaseTestException):
    """Exception raised for message queue operation errors."""
    pass


@dataclass
class Message:
    """Represents a message in the queue."""
    topic: str
    key: Optional[str] = None
    value: Any = None
    headers: Optional[Dict[str, Any]] = None
    partition: Optional[int] = None
    offset: Optional[int] = None
    timestamp: Optional[int] = None


class BaseMQHandler(ABC):
    """Abstract base class for message queue handlers."""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.config = connection_config
        self.connection = None
        self._connected = False
        self.message_handlers: Dict[str, List[Callable]] = {}
    
    @abstractmethod
    def connect(self) -> None:
        """Establish message queue connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close message queue connection."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if message queue connection is active."""
        pass
    
    @abstractmethod
    def send_message(self, message: Message) -> bool:
        """Send message to queue."""
        pass
    
    @abstractmethod
    def receive_messages(self, topic: str, timeout: Optional[float] = None) -> List[Message]:
        """Receive messages from queue."""
        pass
    
    def add_message_handler(self, topic: str, handler: Callable[[Message], None]) -> None:
        """Add message handler for a topic."""
        if topic not in self.message_handlers:
            self.message_handlers[topic] = []
        self.message_handlers[topic].append(handler)
        logger.debug(f"Added message handler for topic: {topic}")
    
    def remove_message_handler(self, topic: str, handler: Callable[[Message], None]) -> None:
        """Remove message handler for a topic."""
        if topic in self.message_handlers:
            try:
                self.message_handlers[topic].remove(handler)
                logger.debug(f"Removed message handler for topic: {topic}")
            except ValueError:
                logger.warning(f"Handler not found for topic: {topic}")
    
    def process_message(self, message: Message) -> None:
        """Process received message with registered handlers."""
        handlers = self.message_handlers.get(message.topic, [])
        
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"\Error processing message with handler {handler.__name__}: {str(e)}")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        if exc_type:
            logger.error(f"Message queue operation failed: {exc_val}")
        return False