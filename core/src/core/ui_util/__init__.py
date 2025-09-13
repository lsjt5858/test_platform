"""
UI automation utilities module for the test platform.
Provides Selenium WebDriver management, page object patterns, and UI testing utilities.
"""

from .webdriver_factory import WebDriverFactory, BrowserConfig
from .page_base import BasePage
from .element_locator import ElementLocator
from .ui_assertions import UIAssertions

__all__ = [
    'WebDriverFactory',
    'BrowserConfig',
    'BasePage',
    'ElementLocator', 
    'UIAssertions'
]