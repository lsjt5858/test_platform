"""
Custom exception classes for the test platform.
"""


class BaseTestException(Exception):
    """Base exception class for all test platform exceptions."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message


class TestConfigError(BaseTestException):
    """Exception raised for configuration-related errors."""
    pass


class TestTimeoutError(BaseTestException):
    """Exception raised when operations timeout."""
    pass


class TestDataError(BaseTestException):
    """Exception raised for test data related errors."""
    pass


class TestEnvironmentError(BaseTestException):
    """Exception raised for environment setup errors."""
    pass


class TestAssertionError(BaseTestException):
    """Exception raised for custom test assertions."""
    pass