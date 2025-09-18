"""
Singleton pattern implementation.
"""

import threading
from typing import Any, Dict


class SingletonMeta(type):
    """Thread-safe singleton metaclass.
    线程安全的单例元类。"""
    
    _instances: Dict[type, Any] = {}
    _lock: threading.Lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        """Control the instance creation process.
        控制实例创建过程。"""
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """Base singleton class. Inherit from this to make a class singleton.
    基础单例类。继承此类以使类成为单例。"""
    
    def __init__(self):
        """Initialize the singleton instance.
        初始化单例实例。"""
        if hasattr(self, '_initialized'):
            return
        self._initialized = True