"""
Enhanced assertion utilities for comprehensive test automation.
"""

import json
import re
import time
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta

import pytest
import requests
from jsonpath_ng import parse as jsonpath_parse
from jsonschema import validate, ValidationError

from ..base_util.logger import get_logger
from ..base_util.exception_handler import TestAssertionError

logger = get_logger(__name__)


class EnhancedAssertions:
    """Enhanced assertion utilities for test automation."""
    
    # HTTP Response Assertions
    @staticmethod
    def assert_status_code(response: requests.Response, expected_code: int = 200, 
                          message: Optional[str] = None) -> None:
        """Assert HTTP response status code."""
        actual_code = response.status_code
        if actual_code != expected_code:
            error_msg = message or f"Expected status code {expected_code}, got {actual_code}"
            logger.error(f"{error_msg}. Response: {response.text[:200]}...")
            raise TestAssertionError(error_msg, {
                'expected': expected_code,
                'actual': actual_code,
                'response_body': response.text[:500]
            })
        
        logger.debug(f"Status code assertion passed: {expected_code}")
    
    @staticmethod
    def assert_status_code_in(response: requests.Response, expected_codes: List[int],
                             message: Optional[str] = None) -> None:
        """Assert HTTP response status code is in expected list."""
        actual_code = response.status_code
        if actual_code not in expected_codes:
            error_msg = message or f"Expected status code in {expected_codes}, got {actual_code}"
            logger.error(f"{error_msg}. Response: {response.text[:200]}...")
            raise TestAssertionError(error_msg, {
                'expected': expected_codes,
                'actual': actual_code,
                'response_body': response.text[:500]
            })
        
        logger.debug(f"Status code in range assertion passed: {actual_code} in {expected_codes}")
    
    @staticmethod
    def assert_response_time(response: requests.Response, max_time: float,
                           message: Optional[str] = None) -> None:
        """Assert response time is within acceptable limit."""
        actual_time = response.elapsed.total_seconds()
        if actual_time > max_time:
            error_msg = message or f"Response time {actual_time:.3f}s exceeded limit {max_time}s"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {
                'expected_max': max_time,
                'actual': actual_time
            })
        
        logger.debug(f"Response time assertion passed: {actual_time:.3f}s <= {max_time}s")
    
    @staticmethod
    def assert_content_type(response: requests.Response, expected_type: str,
                           message: Optional[str] = None) -> None:
        """Assert response content type."""
        actual_type = response.headers.get('content-type', '').split(';')[0]
        if actual_type != expected_type:
            error_msg = message or f"Expected content-type '{expected_type}', got '{actual_type}'"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {
                'expected': expected_type,
                'actual': actual_type
            })
        
        logger.debug(f"Content type assertion passed: {expected_type}")
    
    # JSON Response Assertions
    @staticmethod
    def assert_json_key(response: requests.Response, key: str,
                       message: Optional[str] = None) -> None:
        """Assert JSON response contains key."""
        try:
            json_data = response.json()
        except ValueError:
            error_msg = "Response is not valid JSON"
            logger.error(error_msg)
            raise TestAssertionError(error_msg)
        
        if key not in json_data:
            error_msg = message or f"Key '{key}' not found in JSON response"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {
                'key': key,
                'available_keys': list(json_data.keys()) if isinstance(json_data, dict) else []
            })
        
        logger.debug(f"JSON key assertion passed: '{key}' found")
    
    @staticmethod
    def assert_json_schema(response: requests.Response, schema: Dict[str, Any],
                          message: Optional[str] = None) -> None:
        """Assert JSON response matches schema."""
        try:
            json_data = response.json()
        except ValueError:
            error_msg = "Response is not valid JSON"
            logger.error(error_msg)
            raise TestAssertionError(error_msg)
        
        try:
            validate(instance=json_data, schema=schema)
            logger.debug("JSON schema validation passed")
        except ValidationError as e:
            error_msg = message or f"JSON schema validation failed: {e.message}"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {
                'validation_error': str(e),
                'failed_path': list(e.path) if e.path else [],
                'schema': schema
            })
    
    @staticmethod
    def assert_jsonpath(response: requests.Response, jsonpath: str, expected_value: Any,
                       message: Optional[str] = None) -> None:
        """Assert JSONPath expression matches expected value."""
        try:
            json_data = response.json()
        except ValueError:
            error_msg = "Response is not valid JSON"
            logger.error(error_msg)
            raise TestAssertionError(error_msg)
        
        try:
            jsonpath_expr = jsonpath_parse(jsonpath)
            matches = [match.value for match in jsonpath_expr.find(json_data)]
            
            if not matches:
                error_msg = f"JSONPath '{jsonpath}' found no matches"
                logger.error(error_msg)
                raise TestAssertionError(error_msg, {'jsonpath': jsonpath})
            
            actual_value = matches[0] if len(matches) == 1 else matches
            
            if actual_value != expected_value:
                error_msg = message or f"JSONPath '{jsonpath}' expected {expected_value}, got {actual_value}"
                logger.error(error_msg)
                raise TestAssertionError(error_msg, {
                    'jsonpath': jsonpath,
                    'expected': expected_value,
                    'actual': actual_value
                })
            
            logger.debug(f"JSONPath assertion passed: '{jsonpath}' = {expected_value}")
            
        except Exception as e:
            error_msg = f"JSONPath evaluation failed: {str(e)}"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {'jsonpath': jsonpath})
    
    # Database Assertions
    @staticmethod
    def assert_db_record_exists(db_handler, table: str, conditions: Dict[str, Any],
                               message: Optional[str] = None) -> None:
        """Assert database record exists matching conditions."""
        where_clause = " AND ".join([f"{k} = %s" for k in conditions.keys()])
        query = f"SELECT COUNT(*) as count FROM {table} WHERE {where_clause}"
        
        result = db_handler.execute_query(query, tuple(conditions.values()))
        count = result[0]['count']
        
        if count == 0:
            error_msg = message or f"No records found in {table} matching {conditions}"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {
                'table': table,
                'conditions': conditions
            })
        
        logger.debug(f"DB record existence assertion passed: {count} records found")
    
    @staticmethod
    def assert_eventually(condition_func: Callable[[], bool], 
                         timeout: float = 10.0,
                         interval: float = 0.5,
                         message: Optional[str] = None) -> None:
        """Assert condition becomes true within timeout period."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    logger.debug(f"Eventually assertion passed after {time.time() - start_time:.2f}s")
                    return
            except Exception as e:
                logger.debug(f"Condition evaluation failed: {str(e)}")
            
            time.sleep(interval)
        
        error_msg = message or f"Condition did not become true within {timeout}s"
        logger.error(error_msg)
        raise TestAssertionError(error_msg, {
            'timeout': timeout,
            'elapsed': time.time() - start_time
        })


# Convenience functions for common assertions
def assert_api_success(response: requests.Response, expected_status: int = 200) -> None:
    """Quick assertion for successful API response."""
    EnhancedAssertions.assert_status_code(response, expected_status)
    EnhancedAssertions.assert_content_type(response, 'application/json')


def assert_api_error(response: requests.Response, expected_status: int = 400,
                    error_key: str = 'error') -> None:
    """Quick assertion for API error response."""
    EnhancedAssertions.assert_status_code(response, expected_status)
    EnhancedAssertions.assert_json_key(response, error_key)