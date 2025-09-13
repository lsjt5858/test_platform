"""
Enhanced element locator utilities.
"""

from selenium.webdriver.common.by import By
from typing import Tuple, Dict, Any


class ElementLocator:
    """Utility class for creating and managing element locators."""
    
    @staticmethod
    def by_id(element_id: str) -> Tuple[By, str]:
        """Locate element by ID."""
        return (By.ID, element_id)
    
    @staticmethod
    def by_name(name: str) -> Tuple[By, str]:
        """Locate element by name attribute."""
        return (By.NAME, name)
    
    @staticmethod
    def by_class(class_name: str) -> Tuple[By, str]:
        """Locate element by class name."""
        return (By.CLASS_NAME, class_name)
    
    @staticmethod
    def by_tag(tag_name: str) -> Tuple[By, str]:
        """Locate element by tag name."""
        return (By.TAG_NAME, tag_name)
    
    @staticmethod
    def by_xpath(xpath: str) -> Tuple[By, str]:
        """Locate element by XPath."""
        return (By.XPATH, xpath)
    
    @staticmethod
    def by_css(css_selector: str) -> Tuple[By, str]:
        """Locate element by CSS selector."""
        return (By.CSS_SELECTOR, css_selector)
    
    @staticmethod
    def by_link_text(link_text: str) -> Tuple[By, str]:
        """Locate element by link text."""
        return (By.LINK_TEXT, link_text)
    
    @staticmethod
    def by_partial_link_text(partial_text: str) -> Tuple[By, str]:
        """Locate element by partial link text."""
        return (By.PARTIAL_LINK_TEXT, partial_text)
    
    @staticmethod
    def by_data_testid(testid: str) -> Tuple[By, str]:
        """Locate element by data-testid attribute."""
        return (By.CSS_SELECTOR, f'[data-testid="{testid}"]')
    
    @staticmethod
    def by_aria_label(label: str) -> Tuple[By, str]:
        """Locate element by aria-label attribute."""
        return (By.CSS_SELECTOR, f'[aria-label="{label}"]')
    
    @staticmethod
    def by_placeholder(placeholder: str) -> Tuple[By, str]:
        """Locate element by placeholder attribute."""
        return (By.CSS_SELECTOR, f'[placeholder="{placeholder}"]')
    
    @staticmethod
    def button_by_text(text: str) -> Tuple[By, str]:
        """Locate button by text content."""
        return (By.XPATH, f'//button[contains(text(), "{text}")]')
    
    @staticmethod
    def input_by_label(label: str) -> Tuple[By, str]:
        """Locate input by associated label."""
        return (By.XPATH, f'//label[contains(text(), "{label}")]/following-sibling::input | //input[@id=//label[contains(text(), "{label}")]/@for]')