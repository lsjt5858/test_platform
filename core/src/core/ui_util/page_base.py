"""
Base page object class for UI automation.
"""

from typing import Any, List, Optional, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from ..base_util.logger import get_logger
from ..base_util.wait_util import wait_until, WaitConfig
from ..base_util.exception_handler import TestAssertionError

logger = get_logger(__name__)


class BasePage:
    """Base class for page objects implementing common UI operations."""
    
    def __init__(self, driver: webdriver.Remote, base_url: str = ""):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)
        self.actions = ActionChains(driver)
    
    def navigate_to(self, url: str) -> None:
        """Navigate to URL."""
        full_url = url if url.startswith('http') else f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        logger.info(f"Navigating to: {full_url}")
        self.driver.get(full_url)
    
    def get_current_url(self) -> str:
        """Get current page URL."""
        return self.driver.current_url
    
    def get_title(self) -> str:
        """Get page title."""
        return self.driver.title
    
    def find_element(self, locator: tuple, timeout: int = 10) -> WebElement:
        """Find single element with wait."""
        by, value = locator
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        logger.debug(f"Element found: {locator}")
        return element
    
    def find_elements(self, locator: tuple, timeout: int = 10) -> List[WebElement]:
        """Find multiple elements with wait."""
        by, value = locator
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        elements = self.driver.find_elements(by, value)
        logger.debug(f"Found {len(elements)} elements: {locator}")
        return elements
    
    def click(self, locator: tuple, timeout: int = 10) -> None:
        """Click element."""
        element = self.wait_for_clickable(locator, timeout)
        element.click()
        logger.debug(f"Clicked element: {locator}")
    
    def type_text(self, locator: tuple, text: str, clear: bool = True, timeout: int = 10) -> None:
        """Type text into element."""
        element = self.find_element(locator, timeout)
        if clear:
            element.clear()
        element.send_keys(text)
        logger.debug(f"Typed text '{text}' into element: {locator}")
    
    def get_text(self, locator: tuple, timeout: int = 10) -> str:
        """Get element text."""
        element = self.find_element(locator, timeout)
        text = element.text
        logger.debug(f"Got text '{text}' from element: {locator}")
        return text
    
    def get_attribute(self, locator: tuple, attribute: str, timeout: int = 10) -> str:
        """Get element attribute value."""
        element = self.find_element(locator, timeout)
        value = element.get_attribute(attribute)
        logger.debug(f"Got attribute '{attribute}' = '{value}' from element: {locator}")
        return value
    
    def is_element_present(self, locator: tuple, timeout: int = 3) -> bool:
        """Check if element is present."""
        try:
            self.find_element(locator, timeout)
            return True
        except:
            return False
    
    def is_element_visible(self, locator: tuple, timeout: int = 10) -> bool:
        """Check if element is visible."""
        try:
            by, value = locator
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except:
            return False
    
    def wait_for_element(self, locator: tuple, timeout: int = 10) -> WebElement:
        """Wait for element to be present."""
        return self.find_element(locator, timeout)
    
    def wait_for_clickable(self, locator: tuple, timeout: int = 10) -> WebElement:
        """Wait for element to be clickable."""
        by, value = locator
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        logger.debug(f"Element is clickable: {locator}")
        return element
    
    def wait_for_text(self, locator: tuple, text: str, timeout: int = 10) -> bool:
        """Wait for element to contain specific text."""
        try:
            by, value = locator
            WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element((by, value), text)
            )
            logger.debug(f"Text '{text}' found in element: {locator}")
            return True
        except:
            return False
    
    def scroll_to_element(self, locator: tuple, timeout: int = 10) -> None:
        """Scroll element into view."""
        element = self.find_element(locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        logger.debug(f"Scrolled to element: {locator}")
    
    def hover_over(self, locator: tuple, timeout: int = 10) -> None:
        """Hover over element."""
        element = self.find_element(locator, timeout)
        self.actions.move_to_element(element).perform()
        logger.debug(f"Hovered over element: {locator}")
    
    def drag_and_drop(self, source_locator: tuple, target_locator: tuple, timeout: int = 10) -> None:
        """Drag and drop element."""
        source = self.find_element(source_locator, timeout)
        target = self.find_element(target_locator, timeout)
        self.actions.drag_and_drop(source, target).perform()
        logger.debug(f"Dragged from {source_locator} to {target_locator}")
    
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript."""
        result = self.driver.execute_script(script, *args)
        logger.debug(f"Executed script: {script[:100]}...")
        return result
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot and return path."""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        screenshot_path = self.driver.save_screenshot(filename)
        logger.info(f"Screenshot saved: {filename}")
        return screenshot_path
    
    def switch_to_frame(self, locator: tuple = None, timeout: int = 10) -> None:
        """Switch to iframe."""
        if locator:
            frame = self.find_element(locator, timeout)
            self.driver.switch_to.frame(frame)
        else:
            self.driver.switch_to.default_content()
        logger.debug(f"Switched to frame: {locator or 'default'}")
    
    def switch_to_window(self, window_handle: str = None) -> None:
        """Switch to window."""
        if window_handle:
            self.driver.switch_to.window(window_handle)
        else:
            # Switch to last opened window
            self.driver.switch_to.window(self.driver.window_handles[-1])
        logger.debug(f"Switched to window: {window_handle or 'latest'}")
    
    def close_current_window(self) -> None:
        """Close current window."""
        self.driver.close()
        logger.debug("Closed current window")
    
    def refresh_page(self) -> None:
        """Refresh current page."""
        self.driver.refresh()
        logger.debug("Page refreshed")
    
    def go_back(self) -> None:
        """Go back in browser history."""
        self.driver.back()
        logger.debug("Navigated back")
    
    def go_forward(self) -> None:
        """Go forward in browser history."""
        self.driver.forward()
        logger.debug("Navigated forward")