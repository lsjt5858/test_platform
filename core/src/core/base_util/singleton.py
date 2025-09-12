"""
Singleton pattern implementation.
"""

import threading
from typing import Any, Dict


class SingletonMeta(type):
    """Thread-safe singleton metaclass."""
    
    _instances: Dict[type, Any] = {}
    _lock: threading.Lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """Base singleton class. Inherit from this to make a class singleton."""
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True