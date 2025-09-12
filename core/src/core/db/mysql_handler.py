"""
MySQL database handler for test data operations.
"""

import pymysql
from typing import Any, Dict, List, Optional, Union, Tuple
from contextlib import contextmanager

from .base_db_handler import BaseDBHandler, DatabaseError
from ..base_util.logger import get_logger
from ..base_util.retry_util import retry, RetryConfig

logger = get_logger(__name__)


class MySQLHandler(BaseDBHandler):
    """MySQL database handler with connection pooling and retry support."""
    
    def __init__(self, connection_config: Dict[str, Any]):
        super().__init__(connection_config)
        self.connection_pool = []
        self.max_connections = connection_config.get('max_connections', 5)
    
    def connect(self) -> None:
        """Establish MySQL connection."""
        try:
            connection_params = {
                'host': self.config['host'],
                'port': self.config.get('port', 3306),
                'user': self.config['user'],
                'password': self.config['password'],
                'database': self.config.get('database', ''),
                'charset': self.config.get('charset', 'utf8mb4'),
                'autocommit': self.config.get('autocommit', True),
                'connect_timeout': self.config.get('connect_timeout', 10),
                'read_timeout': self.config.get('read_timeout', 30),
                'write_timeout': self.config.get('write_timeout', 30)
            }
            
            self.connection = pymysql.connect(**connection_params)
            self._connected = True
            logger.info(f"Connected to MySQL: {self.config['host']}:{self.config.get('port', 3306)}")
            
        except Exception as e:
            error_msg = f"Failed to connect to MySQL: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def disconnect(self) -> None:
        """Close MySQL connection."""
        if self.connection:
            try:
                self.connection.close()
                self._connected = False
                logger.debug("MySQL connection closed")
            except Exception as e:
                logger.warning(f"Error closing MySQL connection: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if MySQL connection is active."""
        if not self.connection:
            return False
        
        try:
            self.connection.ping(reconnect=False)
            return True
        except:
            self._connected = False
            return False
    
    @retry(RetryConfig(max_attempts=3, exceptions=(pymysql.Error,)))
    def execute_query(self, query: str, params: Optional[Union[Dict, Tuple]] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        if not self.is_connected():
            self.connect()
        
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                
            logger.debug(f"Query executed successfully: {query[:100]}...")
            return results
            
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg, {'query': query, 'params': params})
    
    @retry(RetryConfig(max_attempts=3, exceptions=(pymysql.Error,)))
    def execute_non_query(self, query: str, params: Optional[Union[Dict, Tuple]] = None) -> int:
        """Execute INSERT, UPDATE, DELETE queries and return affected rows."""
        if not self.is_connected():
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(query, params)
                
                if not self.config.get('autocommit', True):
                    self.connection.commit()
                
            logger.debug(f"Non-query executed successfully: {query[:100]}...")
            return affected_rows
            
        except Exception as e:
            if not self.config.get('autocommit', True):
                self.connection.rollback()
            
            error_msg = f"Non-query execution failed: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg, {'query': query, 'params': params})
    
    def execute_many(self, query: str, params_list: List[Union[Dict, Tuple]]) -> int:
        """Execute query with multiple parameter sets."""
        if not self.is_connected():
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.executemany(query, params_list)
                
                if not self.config.get('autocommit', True):
                    self.connection.commit()
                
            logger.debug(f"Batch query executed: {len(params_list)} operations")
            return affected_rows
            
        except Exception as e:
            if not self.config.get('autocommit', True):
                self.connection.rollback()
            
            error_msg = f"Batch execution failed: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg, {'query': query, 'batch_size': len(params_list)})
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        if not self.is_connected():
            self.connect()
        
        original_autocommit = self.connection.get_autocommit()
        
        try:
            self.connection.autocommit(False)
            yield self
            self.connection.commit()
            logger.debug("Transaction committed")
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Transaction rolled back: {str(e)}")
            raise
            
        finally:
            self.connection.autocommit(original_autocommit)
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get table structure information."""
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)
    
    def get_table_count(self, table_name: str, where_clause: str = "") -> int:
        """Get row count from table."""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        result = self.execute_query(query)
        return result[0]['count'] if result else 0
    
    def truncate_table(self, table_name: str) -> None:
        """Truncate table (remove all data)."""
        query = f"TRUNCATE TABLE {table_name}"
        self.execute_non_query(query)
        logger.info(f"Table {table_name} truncated")
    
    def get_databases(self) -> List[str]:
        """Get list of all databases."""
        query = "SHOW DATABASES"
        results = self.execute_query(query)
        return [row['Database'] for row in results]
    
    def get_tables(self, database: str = None) -> List[str]:
        """Get list of tables in database."""
        if database:
            query = f"SHOW TABLES FROM {database}"
        else:
            query = "SHOW TABLES"
        
        results = self.execute_query(query)
        # Handle different result formats
        table_key = list(results[0].keys())[0] if results else None
        return [row[table_key] for row in results] if table_key else []