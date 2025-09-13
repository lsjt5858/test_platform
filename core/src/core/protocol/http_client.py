import json
import time
from urllib.parse import urljoin, urlparse
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ..config.config_loader import ConfigLoader
from ..base_util.logger import get_logger
from ..base_util.retry_util import retry, RetryConfig
from ..base_util.exception_handler import BaseTestException

logger = get_logger(__name__)


class HttpClientError(BaseTestException):
    """Exception raised for HTTP client errors."""
    pass


@dataclass
class RequestConfig:
    """Configuration for HTTP requests."""
    timeout: Union[float, tuple] = 30.0
    allow_redirects: bool = True
    verify_ssl: bool = True
    stream: bool = False
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    auth: Optional[tuple] = None
    proxies: Dict[str, str] = field(default_factory=dict)


@dataclass 
class RetryPolicy:
    """HTTP retry policy configuration."""
    total: int = 3
    backoff_factor: float = 0.3
    status_forcelist: List[int] = field(default_factory=lambda: [500, 502, 503, 504])
    method_whitelist: List[str] = field(default_factory=lambda: ["HEAD", "GET", "OPTIONS"])


@dataclass
class ResponseValidator:
    """Response validation configuration."""
    expected_status_codes: List[int] = field(default_factory=lambda: [200])
    expected_content_type: Optional[str] = None
    custom_validators: List[Callable] = field(default_factory=list)


class HttpClient:
    """Enhanced HTTP client with comprehensive features for test automation."""
    
    def __init__(self, 
                 base_url: Optional[str] = None,
                 env: str = "default",
                 request_config: Optional[RequestConfig] = None,
                 retry_policy: Optional[RetryPolicy] = None):
        
        self.config = ConfigLoader(env)
        self.base_url = base_url or self.config.get("API", "base_url", "")
        self.request_config = request_config or RequestConfig()
        self.retry_policy = retry_policy or RetryPolicy()
        
        # Setup session with retry strategy
        self.session = requests.Session()
        self._setup_retry_strategy()
        self._setup_default_headers()
        
        # Request/response hooks and middleware
        self.request_hooks: List[Callable] = []
        self.response_hooks: List[Callable] = []
        
        # Request tracking
        self.request_history: List[Dict[str, Any]] = []
        self.max_history = 100
        
        logger.debug(f"HttpClient initialized with base_url: {self.base_url}")
    
    def _setup_retry_strategy(self) -> None:
        """Setup retry strategy for the session."""
        retry_strategy = Retry(
            total=self.retry_policy.total,
            backoff_factor=self.retry_policy.backoff_factor,
            status_forcelist=self.retry_policy.status_forcelist,
            method_whitelist=self.retry_policy.method_whitelist
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _setup_default_headers(self) -> None:
        """Setup default headers for the session."""
        default_headers = {
            'User-Agent': f'TestPlatform-HttpClient/1.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        # Add configured headers
        default_headers.update(self.request_config.headers)
        
        self.session.headers.update(default_headers)
    
    def add_request_hook(self, hook: Callable) -> None:
        """Add a request pre-processing hook."""
        self.request_hooks.append(hook)
        logger.debug(f"Added request hook: {hook.__name__}")
    
    def add_response_hook(self, hook: Callable) -> None:
        """Add a response post-processing hook."""
        self.response_hooks.append(hook)
        logger.debug(f"Added response hook: {hook.__name__}")
    
    def set_auth(self, auth: Union[tuple, requests.auth.AuthBase]) -> None:
        """Set authentication for all requests."""
        self.session.auth = auth
        logger.debug("Authentication configured")
    
    def set_headers(self, headers: Dict[str, str]) -> None:
        """Set headers for all requests."""
        self.session.headers.update(headers)
        logger.debug(f"Headers updated: {list(headers.keys())}")
    
    def set_cookies(self, cookies: Dict[str, str]) -> None:
        """Set cookies for all requests."""
        self.session.cookies.update(cookies)
        logger.debug(f"Cookies updated: {list(cookies.keys())}")
    
    def _build_url(self, path: str) -> str:
        """Build complete URL from base_url and path."""
        if path.startswith(('http://', 'https://')):
            return path
        
        if not self.base_url:
            raise HttpClientError("No base_url configured and path is not absolute URL")
        
        return urljoin(self.base_url.rstrip('/') + '/', path.lstrip('/'))
    
    def _execute_request_hooks(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute all request hooks."""
        request_data = {
            'method': method,
            'url': url,
            'kwargs': kwargs
        }
        
        for hook in self.request_hooks:
            try:
                request_data = hook(request_data) or request_data
            except Exception as e:
                logger.warning(f"Request hook {hook.__name__} failed: {str(e)}")
        
        return request_data
    
    def _execute_response_hooks(self, response: requests.Response) -> requests.Response:
        """Execute all response hooks."""
        for hook in self.response_hooks:
            try:
                response = hook(response) or response
            except Exception as e:
                logger.warning(f"Response hook {hook.__name__} failed: {str(e)}")
        
        return response
    
    def _log_request(self, method: str, url: str, **kwargs) -> None:
        """Log request details."""
        logger.info(f"{method.upper()} {url}")
        
        if kwargs.get('headers'):
            logger.debug(f"Request headers: {kwargs['headers']}")
        
        if kwargs.get('json'):
            logger.debug(f"Request JSON: {json.dumps(kwargs['json'], indent=2)}")
        elif kwargs.get('data'):
            logger.debug(f"Request data: {kwargs['data']}")
    
    def _log_response(self, response: requests.Response, elapsed_time: float) -> None:
        """Log response details."""
        logger.info(
            f"Response: {response.status_code} {response.reason} "
            f"({elapsed_time:.3f}s) [{len(response.content)} bytes]"
        )
        
        if logger.getEffectiveLevel() <= 10:  # DEBUG level
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Log response content if it's JSON or small text
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    response_json = response.json()
                    logger.debug(f"Response JSON: {json.dumps(response_json, indent=2)}")
                except:
                    logger.debug(f"Response text: {response.text[:500]}...")
            elif len(response.text) < 1000:
                logger.debug(f"Response text: {response.text}")
    
    def _track_request(self, method: str, url: str, response: requests.Response, 
                      elapsed_time: float, **kwargs) -> None:
        """Track request in history."""
        request_record = {
            'timestamp': time.time(),
            'method': method.upper(),
            'url': url,
            'status_code': response.status_code,
            'elapsed_time': elapsed_time,
            'request_size': len(str(kwargs.get('data', '') or kwargs.get('json', ''))),
            'response_size': len(response.content),
            'headers_sent': dict(kwargs.get('headers', {})),
            'headers_received': dict(response.headers)
        }
        
        self.request_history.append(request_record)
        
        # Keep history within limits
        if len(self.request_history) > self.max_history:
            self.request_history.pop(0)
    
    def _validate_response(self, response: requests.Response, 
                          validator: Optional[ResponseValidator] = None) -> None:
        """Validate response according to validation rules."""
        if not validator:
            return
        
        # Check status code
        if validator.expected_status_codes and response.status_code not in validator.expected_status_codes:
            raise HttpClientError(
                f"Unexpected status code: {response.status_code}. "
                f"Expected: {validator.expected_status_codes}"
            )
        
        # Check content type
        if validator.expected_content_type:
            content_type = response.headers.get('content-type', '').split(';')[0]
            if content_type != validator.expected_content_type:
                raise HttpClientError(
                    f"Unexpected content type: {content_type}. "
                    f"Expected: {validator.expected_content_type}"
                )
        
        # Run custom validators
        for custom_validator in validator.custom_validators:
            try:
                custom_validator(response)
            except Exception as e:
                raise HttpClientError(f"Custom validation failed: {str(e)}")
    
    def request(self, method: str, path: str, 
                validator: Optional[ResponseValidator] = None,
                **kwargs) -> requests.Response:
        """Make HTTP request with full feature support."""
        
        url = self._build_url(path)
        
        # Apply request config defaults
        kwargs.setdefault('timeout', self.request_config.timeout)
        kwargs.setdefault('allow_redirects', self.request_config.allow_redirects)
        kwargs.setdefault('verify', self.request_config.verify_ssl)
        kwargs.setdefault('stream', self.request_config.stream)
        
        # Merge default cookies
        if self.request_config.cookies:
            cookies = kwargs.get('cookies', {})
            cookies.update(self.request_config.cookies)
            kwargs['cookies'] = cookies
        
        # Merge default proxies
        if self.request_config.proxies:
            kwargs.setdefault('proxies', self.request_config.proxies)
        
        # Execute request hooks
        request_data = self._execute_request_hooks(method, url, **kwargs)
        method = request_data['method']
        url = request_data['url'] 
        kwargs = request_data['kwargs']
        
        self._log_request(method, url, **kwargs)
        
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            elapsed_time = time.time() - start_time
            
            # Execute response hooks
            response = self._execute_response_hooks(response)
            
            self._log_response(response, elapsed_time)
            self._track_request(method, url, response, elapsed_time, **kwargs)
            
            # Validate response
            self._validate_response(response, validator)
            
            return response
            
        except requests.exceptions.RequestException as e:
            elapsed_time = time.time() - start_time
            error_msg = f"Request failed after {elapsed_time:.3f}s: {str(e)}"
            logger.error(error_msg)
            raise HttpClientError(error_msg)
    
    # HTTP method convenience functions
    def get(self, path: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make GET request."""
        if params:
            kwargs['params'] = params
        return self.request('GET', path, **kwargs)
    
    def post(self, path: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make POST request."""
        if data:
            kwargs['data'] = data
        if json:
            kwargs['json'] = json
        return self.request('POST', path, **kwargs)
    
    def put(self, path: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make PUT request."""
        if data:
            kwargs['data'] = data
        if json:
            kwargs['json'] = json
        return self.request('PUT', path, **kwargs)
    
    def delete(self, path: str, **kwargs) -> requests.Response:
        """Make DELETE request."""
        return self.request('DELETE', path, **kwargs)
    
    def patch(self, path: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make PATCH request."""
        if data:
            kwargs['data'] = data
        if json:
            kwargs['json'] = json
        return self.request('PATCH', path, **kwargs)
    
    def head(self, path: str, **kwargs) -> requests.Response:
        """Make HEAD request."""
        return self.request('HEAD', path, **kwargs)
    
    def options(self, path: str, **kwargs) -> requests.Response:
        """Make OPTIONS request."""
        return self.request('OPTIONS', path, **kwargs)
    
    # Utility methods
    def get_request_history(self) -> List[Dict[str, Any]]:
        """Get request history."""
        return self.request_history.copy()
    
    def clear_request_history(self) -> None:
        """Clear request history."""
        self.request_history.clear()
        logger.debug("Request history cleared")
    
    def close(self) -> None:
        """Close the session."""
        if self.session:
            self.session.close()
            logger.debug("HTTP session closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()