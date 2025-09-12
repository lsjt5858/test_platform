"""
Authentication handler for various authentication methods.
"""

import base64
import hashlib
import hmac
import time
import json
from typing import Dict, Optional, Any, Union
from dataclasses import dataclass
from urllib.parse import urlencode

import requests

from ..base_util.logger import get_logger
from ..base_util.exception_handler import BaseTestException

logger = get_logger(__name__)


class AuthenticationError(BaseTestException):
    """Exception raised for authentication errors."""
    pass


@dataclass
class AuthConfig:
    """Configuration for authentication."""
    auth_type: str  # basic, bearer, oauth2, apikey, custom
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    auth_url: Optional[str] = None
    token_url: Optional[str] = None
    scope: Optional[str] = None
    custom_headers: Dict[str, str] = None


class AuthHandler:
    """Handler for various authentication mechanisms."""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.cached_tokens: Dict[str, Any] = {}
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on configuration."""
        auth_type = self.config.auth_type.lower()
        
        if auth_type == "basic":
            return self._get_basic_auth_headers()
        elif auth_type == "bearer":
            return self._get_bearer_auth_headers()
        elif auth_type == "oauth2":
            return self._get_oauth2_auth_headers()
        elif auth_type == "apikey":
            return self._get_apikey_auth_headers()
        elif auth_type == "custom":
            return self._get_custom_auth_headers()
        else:
            raise AuthenticationError(f"Unsupported authentication type: {auth_type}")
    
    def _get_basic_auth_headers(self) -> Dict[str, str]:
        """Generate Basic authentication headers."""
        if not self.config.username or not self.config.password:
            raise AuthenticationError("Username and password required for Basic auth")
        
        credentials = f"{self.config.username}:{self.config.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        logger.debug(f"Generated Basic auth for user: {self.config.username}")
        return {"Authorization": f"Basic {encoded_credentials}"}
    
    def _get_bearer_auth_headers(self) -> Dict[str, str]:
        """Generate Bearer token authentication headers."""
        if not self.config.token:
            raise AuthenticationError("Token required for Bearer auth")
        
        logger.debug("Using Bearer token authentication")
        return {"Authorization": f"Bearer {self.config.token}"}
    
    def _get_oauth2_auth_headers(self) -> Dict[str, str]:
        """Generate OAuth2 authentication headers."""
        # Check if we have a cached valid token
        cache_key = f"oauth2_{self.config.client_id}"
        cached_token = self.cached_tokens.get(cache_key)
        
        if cached_token and cached_token['expires_at'] > time.time():
            logger.debug("Using cached OAuth2 token")
            return {"Authorization": f"Bearer {cached_token['access_token']}"}
        
        # Get new token
        access_token = self._get_oauth2_token()
        return {"Authorization": f"Bearer {access_token}"}
    
    def _get_oauth2_token(self) -> str:
        """Get OAuth2 access token."""
        if not all([self.config.client_id, self.config.client_secret, self.config.token_url]):
            raise AuthenticationError(
                "client_id, client_secret, and token_url required for OAuth2"
            )
        
        # Prepare token request
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret
        }
        
        if self.config.scope:
            token_data['scope'] = self.config.scope
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        try:
            logger.info(f"Requesting OAuth2 token from {self.config.token_url}")
            response = requests.post(
                self.config.token_url,
                data=urlencode(token_data),
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            token_response = response.json()
            
            access_token = token_response.get('access_token')
            if not access_token:
                raise AuthenticationError("No access_token in OAuth2 response")
            
            # Cache token with expiration
            expires_in = token_response.get('expires_in', 3600)  # Default 1 hour
            cache_key = f"oauth2_{self.config.client_id}"
            
            self.cached_tokens[cache_key] = {
                'access_token': access_token,
                'expires_at': time.time() + expires_in - 60  # 60s buffer
            }
            
            logger.info("OAuth2 token obtained successfully")
            return access_token
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to obtain OAuth2 token: {str(e)}"
            logger.error(error_msg)
            raise AuthenticationError(error_msg)
        except KeyError as e:
            error_msg = f"Invalid OAuth2 token response format: {str(e)}"
            logger.error(error_msg)
            raise AuthenticationError(error_msg)
    
    def _get_apikey_auth_headers(self) -> Dict[str, str]:
        """Generate API key authentication headers."""
        if not self.config.api_key:
            raise AuthenticationError("API key required for API key auth")
        
        logger.debug(f"Using API key authentication with header: {self.config.api_key_header}")
        return {self.config.api_key_header: self.config.api_key}
    
    def _get_custom_auth_headers(self) -> Dict[str, str]:
        """Get custom authentication headers."""
        if not self.config.custom_headers:
            raise AuthenticationError("Custom headers required for custom auth")
        
        logger.debug("Using custom authentication headers")
        return self.config.custom_headers.copy()
    
    def generate_signature(self, 
                          method: str,
                          url: str, 
                          params: Optional[Dict] = None,
                          body: Optional[str] = None,
                          secret: Optional[str] = None) -> str:
        """Generate HMAC signature for request (useful for custom auth)."""
        secret = secret or self.config.client_secret
        if not secret:
            raise AuthenticationError("Secret required for signature generation")
        
        # Build string to sign
        string_to_sign_parts = [method.upper(), url]
        
        if params:
            query_string = urlencode(sorted(params.items()))
            string_to_sign_parts.append(query_string)
        
        if body:
            string_to_sign_parts.append(body)
        
        string_to_sign = "".join(string_to_sign_parts)
        
        # Generate HMAC signature
        signature = hmac.new(
            secret.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        logger.debug(f"Generated signature for {method} {url}")
        return signature
    
    def refresh_oauth2_token(self) -> str:
        """Force refresh OAuth2 token."""
        cache_key = f"oauth2_{self.config.client_id}"
        if cache_key in self.cached_tokens:
            del self.cached_tokens[cache_key]
        
        return self._get_oauth2_token()
    
    def clear_cached_tokens(self) -> None:
        """Clear all cached tokens."""
        self.cached_tokens.clear()
        logger.debug("Cleared all cached authentication tokens")
    
    def is_token_expired(self, auth_type: str = "oauth2") -> bool:
        """Check if cached token is expired."""
        cache_key = f"{auth_type}_{self.config.client_id}"
        cached_token = self.cached_tokens.get(cache_key)
        
        if not cached_token:
            return True
        
        return cached_token['expires_at'] <= time.time()
    
    def get_auth_info(self) -> Dict[str, Any]:
        """Get current authentication information (excluding sensitive data)."""
        return {
            'auth_type': self.config.auth_type,
            'username': self.config.username,
            'has_token': bool(self.config.token),
            'has_api_key': bool(self.config.api_key),
            'api_key_header': self.config.api_key_header,
            'client_id': self.config.client_id,
            'auth_url': self.config.auth_url,
            'token_url': self.config.token_url,
            'scope': self.config.scope,
            'cached_tokens': list(self.cached_tokens.keys())
        }