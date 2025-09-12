"""
Protocol handling module for the test platform.
Provides HTTP client, authentication, and other protocol implementations.
"""

from .http_client import HttpClient, RequestConfig, RetryPolicy, ResponseValidator, HttpClientError
from .auth_handler import AuthHandler, AuthConfig
from .curl_util import CurlUtil

__all__ = [
    'HttpClient',
    'RequestConfig',
    'RetryPolicy', 
    'ResponseValidator',
    'HttpClientError',
    'AuthHandler',
    'AuthConfig',
    'CurlUtil'
]