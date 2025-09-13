"""
Test Platform Core Layer

The core layer provides fundamental infrastructure for the test platform including:
- Base utilities (logging, retry, file operations, etc.)
- Configuration management
- Database operations (MySQL, Redis, Elasticsearch)
- Protocol handling (HTTP, authentication)
- Message queue operations (Kafka, RabbitMQ)
- Testing utilities (pytest integration, assertions)
- UI automation support

This follows the 4-layer architecture:
Core -> App -> Biz -> Test
"""

__version__ = "1.0.0"

# Core infrastructure imports
from . import base_util
from . import config
from . import db
from . import protocol
from . import mq
from . import pytest_util
from . import ui_util

__all__ = [
    'base_util',
    'config', 
    'db',
    'protocol',
    'mq',
    'pytest_util',
    'ui_util'
]