"""
Common pytest fixtures for the test platform.
"""

import pytest
from typing import Dict, Any, Optional
from pathlib import Path

from ..config.config_loader import ConfigLoader
from ..protocol.http_client import HttpClient
from ..db.mysql_handler import MySQLHandler
from ..db.redis_handler import RedisHandler
from ..base_util.logger import Logger


@pytest.fixture(scope="session")
def config():
    """Provide test configuration."""
    test_env = pytest.config.getoption("--env", default="test")
    return ConfigLoader(env=test_env)


@pytest.fixture(scope="session")
def http_client(config):
    """Provide HTTP client for API testing."""
    base_url = config.get("API", "base_url", fallback="http://localhost:8000")
    client = HttpClient(base_url=base_url)
    yield client
    client.close()


@pytest.fixture(scope="session")
def mysql_db(config):
    """Provide MySQL database handler."""
    db_config = {
        'host': config.get("DATABASE", "host", fallback="localhost"),
        'port': config.get("DATABASE", "port", fallback=3306),
        'user': config.get("DATABASE", "user", fallback="test"),
        'password': config.get("DATABASE", "password", fallback="test"),
        'database': config.get("DATABASE", "name", fallback="test_db")
    }
    
    db = MySQLHandler(db_config)
    yield db
    db.disconnect()


@pytest.fixture(scope="session") 
def redis_cache(config):
    """Provide Redis cache handler."""
    redis_config = {
        'host': config.get("REDIS", "host", fallback="localhost"),
        'port': config.get("REDIS", "port", fallback=6379),
        'db': config.get("REDIS", "db", fallback=0),
        'password': config.get("REDIS", "password")
    }
    
    redis_handler = RedisHandler(redis_config)
    yield redis_handler
    redis_handler.disconnect()


@pytest.fixture
def test_data_path():
    """Provide path to test data directory."""
    return Path(__file__).parent.parent.parent / "test_data"


@pytest.fixture
def logger():
    """Provide test logger."""
    Logger.configure_logging(level="DEBUG")
    return Logger.get_logger("test")


class CommonFixtures:
    """Collection of common test fixtures."""
    
    @staticmethod
    @pytest.fixture
    def clean_database(mysql_db):
        """Clean database before and after test."""
        # Clean before test
        yield mysql_db
        # Clean after test - implement specific cleanup logic
        
    @staticmethod
    @pytest.fixture
    def clean_redis(redis_cache):
        """Clean Redis cache before and after test."""
        redis_cache.flushdb()
        yield redis_cache
        redis_cache.flushdb()
        
    @staticmethod
    @pytest.fixture
    def mock_time(monkeypatch):
        """Mock time for consistent testing."""
        import time
        import datetime
        
        fixed_time = datetime.datetime(2023, 1, 1, 12, 0, 0)
        fixed_timestamp = fixed_time.timestamp()
        
        monkeypatch.setattr(time, "time", lambda: fixed_timestamp)
        monkeypatch.setattr(datetime, "datetime", 
                           type("MockDateTime", (), {
                               "now": lambda: fixed_time,
                               "utcnow": lambda: fixed_time
                           }))
        
        return fixed_time