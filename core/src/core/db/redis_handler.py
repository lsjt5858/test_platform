"""
Redis handler for caching and session management in tests.
"""

import json
import redis
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

from .base_db_handler import BaseDBHandler, DatabaseError
from ..base_util.logger import get_logger
from ..base_util.retry_util import retry, RetryConfig

logger = get_logger(__name__)


class RedisHandler(BaseDBHandler):
    """Redis handler with connection pooling and serialization support."""
    
    def __init__(self, connection_config: Dict[str, Any]):
        super().__init__(connection_config)
        self.connection_pool = None
    
    def connect(self) -> None:
        """Establish Redis connection."""
        try:
            pool_params = {
                'host': self.config['host'],
                'port': self.config.get('port', 6379),
                'db': self.config.get('db', 0),
                'password': self.config.get('password'),
                'socket_timeout': self.config.get('socket_timeout', 5),
                'socket_connect_timeout': self.config.get('socket_connect_timeout', 5),
                'socket_keepalive': self.config.get('socket_keepalive', True),
                'socket_keepalive_options': {},
                'max_connections': self.config.get('max_connections', 10),
                'decode_responses': True,
                'encoding': 'utf-8',
                'health_check_interval': self.config.get('health_check_interval', 30)
            }
            
            # Remove None values
            pool_params = {k: v for k, v in pool_params.items() if v is not None}
            
            self.connection_pool = redis.ConnectionPool(**pool_params)
            self.connection = redis.Redis(connection_pool=self.connection_pool)
            
            # Test connection
            self.connection.ping()
            self._connected = True
            
            logger.info(f"Connected to Redis: {self.config['host']}:{self.config.get('port', 6379)}")
            
        except Exception as e:
            error_msg = f"Failed to connect to Redis: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def disconnect(self) -> None:
        """Close Redis connection pool."""
        if self.connection_pool:
            try:
                self.connection_pool.disconnect()
                self._connected = False
                logger.debug("Redis connection pool closed")
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if Redis connection is active."""
        if not self.connection:
            return False
        
        try:
            self.connection.ping()
            return True
        except:
            self._connected = False
            return False
    
    @retry(RetryConfig(max_attempts=3, exceptions=(redis.RedisError,)))
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute Redis command (for compatibility with base class)."""
        # This method is mainly for compatibility with BaseDBHandler
        # Direct Redis operations should use specific methods
        logger.warning("Generic execute_query not recommended for Redis. Use specific methods.")
        return None
    
    def set(self, key: str, value: Any, expire: Optional[Union[int, timedelta]] = None) -> bool:
        """Set key-value pair with optional expiration."""
        if not self.is_connected():
            self.connect()
        
        try:
            # Serialize complex objects to JSON
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = self.connection.set(key, value, ex=expire)
            logger.debug(f"Set key '{key}' with value type: {type(value).__name__}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to set key '{key}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key with JSON deserialization support."""
        if not self.is_connected():
            self.connect()
        
        try:
            value = self.connection.get(key)
            if value is None:
                return default
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            error_msg = f"Failed to get key '{key}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        if not self.is_connected():
            self.connect()
        
        try:
            result = self.connection.delete(*keys)
            logger.debug(f"Deleted {result} keys: {keys[:5]}..." if len(keys) > 5 else f"Deleted {result} keys: {keys}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to delete keys {keys}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        if not self.is_connected():
            self.connect()
        
        try:
            return self.connection.exists(*keys)
        except Exception as e:
            error_msg = f"Failed to check existence of keys {keys}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def expire(self, key: str, time: Union[int, timedelta]) -> bool:
        """Set expiration time for key."""
        if not self.is_connected():
            self.connect()
        
        try:
            return self.connection.expire(key, time)
        except Exception as e:
            error_msg = f"Failed to set expiration for key '{key}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        if not self.is_connected():
            self.connect()
        
        try:
            return self.connection.keys(pattern)
        except Exception as e:
            error_msg = f"Failed to get keys with pattern '{pattern}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def flushdb(self) -> bool:
        """Clear current database."""
        if not self.is_connected():
            self.connect()
        
        try:
            result = self.connection.flushdb()
            logger.info(f"Flushed database {self.config.get('db', 0)}")
            return result
        except Exception as e:
            error_msg = f"Failed to flush database: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    # Hash operations
    def hset(self, name: str, key: str, value: Any) -> int:
        """Set field in hash."""
        if not self.is_connected():
            self.connect()
        
        try:
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value, ensure_ascii=False)
            return self.connection.hset(name, key, value)
        except Exception as e:
            error_msg = f"Failed to set hash field '{name}.{key}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def hget(self, name: str, key: str) -> Any:
        """Get field from hash."""
        if not self.is_connected():
            self.connect()
        
        try:
            value = self.connection.hget(name, key)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            error_msg = f"Failed to get hash field '{name}.{key}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        """Get all fields from hash."""
        if not self.is_connected():
            self.connect()
        
        try:
            result = self.connection.hgetall(name)
            # Try to deserialize JSON values
            for key, value in result.items():
                try:
                    result[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass
            return result
        except Exception as e:
            error_msg = f"Failed to get all hash fields from '{name}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    # List operations
    def lpush(self, name: str, *values: Any) -> int:
        """Push values to the left of list."""
        if not self.is_connected():
            self.connect()
        
        try:
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list, tuple)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    serialized_values.append(value)
            
            return self.connection.lpush(name, *serialized_values)
        except Exception as e:
            error_msg = f"Failed to push to list '{name}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def rpop(self, name: str) -> Any:
        """Pop value from right of list."""
        if not self.is_connected():
            self.connect()
        
        try:
            value = self.connection.rpop(name)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            error_msg = f"Failed to pop from list '{name}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)