"""
UI-specific assertion utilities.
"""

from typing import List, Optional, Union
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from ..base_util.logger import get_logger
from ..base_util.exception_handler import TestAssertionError

logger = get_logger(__name__)


class UIAssertions:
    """UI-specific assertion utilities for web testing."""
    
    @staticmethod
    def assert_element_present(driver: webdriver.Remote, locator: tuple,
                              message: Optional[str] = None) -> None:
        """Assert element is present on page."""
        by, value = locator
        elements = driver.find_elements(by, value)
        
        if not elements:
            error_msg = message or f"Element not found: {locator}"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {'locator': locator})
        
        logger.debug(f"Element presence assertion passed: {locator}")
    
    @staticmethod
    def assert_element_visible(driver: webdriver.Remote, locator: tuple,
                              message: Optional[str] = None) -> None:
        """Assert element is visible on page."""
        by, value = locator
        elements = driver.find_elements(by, value)
        
        if not elements:
            error_msg = f"Element not found: {locator}"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {'locator': locator})
        
        element = elements[0]
        if not element.is_displayed():
            error_msg = message or f"Element not visible: {locator}"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {'locator': locator})
        
        logger.debug(f"Element visibility assertion passed: {locator}")
    
    @staticmethod
    def assert_element_text(driver: webdriver.Remote, locator: tuple, 
                           expected_text: str, exact_match: bool = True,
                           message: Optional[str] = None) -> None:
        """Assert element contains expected text."""
        by, value = locator
        elements = driver.find_elements(by, value)
        
        if not elements:
            error_msg = f"Element not found: {locator}"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {'locator': locator})
        
        actual_text = elements[0].text
        
        if exact_match:
            if actual_text != expected_text:
                error_msg = message or f"Expected text '{expected_text}', got '{actual_text}'"
                logger.error(error_msg)
                raise TestAssertionError(error_msg, {
                    'locator': locator,
                    'expected': expected_text,
                    'actual': actual_text
                })
        else:
            if expected_text not in actual_text:
                error_msg = message or f"Text '{expected_text}' not found in '{actual_text}'"
                logger.error(error_msg)
                raise TestAssertionError(error_msg, {
                    'locator': locator,
                    'expected': expected_text,
                    'actual': actual_text
                })
        
        logger.debug(f"Element text assertion passed: {locator}")
    
    @staticmethod
    def assert_page_title(driver: webdriver.Remote, expected_title: str,
                         exact_match: bool = True, message: Optional[str] = None) -> None:
        """Assert page title matches expected value."""
        actual_title = driver.title
        
        if exact_match:
            if actual_title != expected_title:
                error_msg = message or f"Expected title '{expected_title}', got '{actual_title}'"
                logger.error(error_msg)
                raise TestAssertionError(error_msg, {
                    'expected': expected_title,
                    'actual': actual_title
                })
        else:
            if expected_title not in actual_title:
                error_msg = message or f"Title '{expected_title}' not found in '{actual_title}'"
                logger.error(error_msg)
                raise TestAssertionError(error_msg, {
                    'expected': expected_title,
                    'actual': actual_title
                })
        
        logger.debug(f"Page title assertion passed: '{expected_title}'")
    
    @staticmethod
    def assert_url_contains(driver: webdriver.Remote, expected_substring: str,
                           message: Optional[str] = None) -> None:
        """Assert current URL contains expected substring."""
        current_url = driver.current_url
        
        if expected_substring not in current_url:
            error_msg = message or f"URL substring '{expected_substring}' not found in '{current_url}'"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {
                'expected_substring': expected_substring,
                'actual_url': current_url
            })
        
        logger.debug(f"URL contains assertion passed: '{expected_substring}'")
    
    @staticmethod
    def assert_element_attribute(driver: webdriver.Remote, locator: tuple,
                                attribute: str, expected_value: str,
                                message: Optional[str] = None) -> None:
        """Assert element attribute has expected value."""
        by, value = locator
        elements = driver.find_elements(by, value)
        
        if not elements:
            error_msg = f"Element not found: {locator}"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {'locator': locator})
        
        actual_value = elements[0].get_attribute(attribute)
        
        if actual_value != expected_value:
            error_msg = message or f"Expected {attribute}='{expected_value}', got '{actual_value}'"
            logger.error(error_msg)
            raise TestAssertionError(error_msg, {
                'locator': locator,
                'attribute': attribute,
                'expected': expected_value,
                'actual': actual_value
            })
        
        logger.debug(f"Element attribute assertion passed: {attribute}='{expected_value}'")