"""
cURL utility for generating and executing cURL commands.
"""

import json
import shlex
import subprocess
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode

from ..base_util.logger import get_logger
from ..base_util.exception_handler import BaseTestException

logger = get_logger(__name__)


class CurlError(BaseTestException):
    """Exception raised for cURL related errors."""
    pass


class CurlUtil:
    """Utility for generating and executing cURL commands."""
    
    @staticmethod
    def build_curl_command(method: str,
                          url: str,
                          headers: Optional[Dict[str, str]] = None,
                          data: Optional[Union[str, Dict]] = None,
                          params: Optional[Dict[str, str]] = None,
                          auth: Optional[tuple] = None,
                          cookies: Optional[Dict[str, str]] = None,
                          timeout: Optional[int] = None,
                          follow_redirects: bool = True,
                          verify_ssl: bool = True,
                          output_file: Optional[str] = None,
                          include_headers: bool = False,
                          verbose: bool = False) -> str:
        """
        Build cURL command string from parameters.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            data: Request body data
            params: URL parameters
            auth: Basic auth tuple (username, password)
            cookies: Cookies dictionary
            timeout: Request timeout in seconds
            follow_redirects: Whether to follow redirects
            verify_ssl: Whether to verify SSL certificates
            output_file: Output file path
            include_headers: Include response headers in output
            verbose: Verbose output
            
        Returns:
            Complete cURL command string
        """
        curl_parts = ['curl']
        
        # Add method
        if method.upper() != 'GET':
            curl_parts.extend(['-X', method.upper()])
        
        # Add headers
        if headers:
            for key, value in headers.items():
                curl_parts.extend(['-H', f'{key}: {value}'])
        
        # Add authentication
        if auth:
            username, password = auth
            curl_parts.extend(['-u', f'{username}:{password}'])
        
        # Add cookies
        if cookies:
            cookie_string = '; '.join(f'{k}={v}' for k, v in cookies.items())
            curl_parts.extend(['-H', f'Cookie: {cookie_string}'])
        
        # Add request body
        if data:
            if isinstance(data, dict):
                # JSON data
                curl_parts.extend(['-H', 'Content-Type: application/json'])
                curl_parts.extend(['-d', json.dumps(data)])
            else:
                # String data
                curl_parts.extend(['-d', str(data)])
        
        # Add URL parameters
        if params:
            param_string = urlencode(params)
            separator = '&' if '?' in url else '?'
            url = f'{url}{separator}{param_string}'
        
        # Add options
        if not follow_redirects:
            curl_parts.append('--no-location')
        else:
            curl_parts.append('-L')
        
        if not verify_ssl:
            curl_parts.append('-k')
        
        if timeout:
            curl_parts.extend(['--max-time', str(timeout)])
        
        if include_headers:
            curl_parts.append('-i')
        
        if verbose:
            curl_parts.append('-v')
        
        if output_file:
            curl_parts.extend(['-o', output_file])
        
        # Add URL (must be last)
        curl_parts.append(url)
        
        # Build command string with proper escaping
        return ' '.join(shlex.quote(part) for part in curl_parts)
    
    @staticmethod
    def execute_curl(curl_command: str,
                    capture_output: bool = True,
                    timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute cURL command and return results."""
        try:
            logger.debug(f"Executing cURL command: {curl_command}")
            
            # Parse command into list
            command_parts = shlex.split(curl_command)
            
            # Execute command
            result = subprocess.run(
                command_parts,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            execution_result = {
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
            if result.returncode == 0:
                logger.debug("cURL command executed successfully")
            else:
                logger.warning(f"cURL command failed with return code: {result.returncode}")
                logger.warning(f"Error output: {result.stderr}")
            
            return execution_result
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"cURL command timed out after {timeout}s"
            logger.error(error_msg)
            raise CurlError(error_msg)
        
        except subprocess.SubprocessError as e:
            error_msg = f"Failed to execute cURL command: {str(e)}"
            logger.error(error_msg)
            raise CurlError(error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error executing cURL: {str(e)}"
            logger.error(error_msg)
            raise CurlError(error_msg)
    
    @staticmethod
    def request_to_curl(method: str,
                       url: str,
                       **kwargs) -> str:
        """Convert request parameters to cURL command (similar to requests format)."""
        curl_kwargs = {}
        
        # Map common requests parameters to curl parameters
        if 'headers' in kwargs:
            curl_kwargs['headers'] = kwargs['headers']
        
        if 'json' in kwargs:
            curl_kwargs['data'] = kwargs['json']
        
        if 'data' in kwargs:
            curl_kwargs['data'] = kwargs['data']
        
        if 'params' in kwargs:
            curl_kwargs['params'] = kwargs['params']
        
        if 'auth' in kwargs:
            curl_kwargs['auth'] = kwargs['auth']
        
        if 'cookies' in kwargs:
            curl_kwargs['cookies'] = kwargs['cookies']
        
        if 'timeout' in kwargs:
            curl_kwargs['timeout'] = kwargs['timeout']
        
        if 'allow_redirects' in kwargs:
            curl_kwargs['follow_redirects'] = kwargs['allow_redirects']
        
        if 'verify' in kwargs:
            curl_kwargs['verify_ssl'] = kwargs['verify']
        
        return CurlUtil.build_curl_command(method, url, **curl_kwargs)
    
    @staticmethod
    def curl_to_requests_kwargs(curl_command: str) -> Dict[str, Any]:
        """Parse cURL command and extract parameters for requests library."""
        # This is a simplified parser - full cURL parsing is quite complex
        # For production use, consider using a dedicated library like `uncurl`
        
        import re
        
        kwargs = {
            'method': 'GET',
            'headers': {},
            'params': {},
        }
        
        # Extract method
        method_match = re.search(r'-X\\s+(\\w+)', curl_command)
        if method_match:
            kwargs['method'] = method_match.group(1)
        
        # Extract headers
        header_matches = re.findall(r"-H\\s+['\\\"]([^'\\\"]+)['\\\"]?", curl_command)
        for header in header_matches:
            if ':' in header:
                key, value = header.split(':', 1)
                kwargs['headers'][key.strip()] = value.strip()
        
        # Extract URL (simplified)
        url_match = re.search(r'curl.*?\\s+([^\\s]+)$', curl_command)
        if url_match:
            kwargs['url'] = url_match.group(1).strip("'\"")
        
        # Extract data
        data_match = re.search(r"-d\\s+['\\\"]([^'\\\"]+)['\\\"]?", curl_command)
        if data_match:
            data = data_match.group(1)
            try:
                kwargs['json'] = json.loads(data)
            except json.JSONDecodeError:
                kwargs['data'] = data
        
        # Extract basic auth
        auth_match = re.search(r'-u\\s+([^\\s]+)', curl_command)
        if auth_match:
            auth_string = auth_match.group(1).strip("'\"")
            if ':' in auth_string:
                username, password = auth_string.split(':', 1)
                kwargs['auth'] = (username, password)
        
        logger.debug(f"Parsed cURL command to requests kwargs: {list(kwargs.keys())}")
        return kwargs
    
    @staticmethod
    def generate_curl_test_cases(base_url: str,
                               endpoints: List[Dict[str, Any]]) -> List[str]:
        """Generate cURL test cases for multiple endpoints."""
        curl_commands = []
        
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET')
            path = endpoint.get('path', '/')
            url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
            
            curl_command = CurlUtil.build_curl_command(
                method=method,
                url=url,
                headers=endpoint.get('headers'),
                data=endpoint.get('data'),
                params=endpoint.get('params'),
                auth=endpoint.get('auth')
            )
            
            curl_commands.append(curl_command)
        
        logger.info(f"Generated {len(curl_commands)} cURL test cases")
        return curl_commands
    
    @staticmethod
    def save_curl_script(curl_commands: List[str],
                        output_file: str,
                        add_shebang: bool = True) -> None:
        """Save cURL commands to a shell script file."""
        try:
            with open(output_file, 'w') as f:
                if add_shebang:
                    f.write('#!/bin/bash\
\
')
                
                f.write('# Generated cURL test script\
')
                f.write(f'# Total commands: {len(curl_commands)}\
\
')
                
                for i, command in enumerate(curl_commands, 1):
                    f.write(f'# Test case {i}\
')
                    f.write(f'{command}\
\
')
            
            logger.info(f"Saved {len(curl_commands)} cURL commands to {output_file}")
            
        except Exception as e:
            error_msg = f"Failed to save cURL script: {str(e)}"
            logger.error(error_msg)
            raise CurlError(error_msg)