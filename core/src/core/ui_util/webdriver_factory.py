"""
WebDriver factory for managing browser instances.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions

from ..base_util.logger import get_logger
from ..base_util.exception_handler import TestEnvironmentError

logger = get_logger(__name__)


@dataclass
class BrowserConfig:
    """Configuration for browser setup."""
    browser: str = "chrome"  # chrome, firefox, safari, edge
    headless: bool = False
    window_size: tuple = (1920, 1080)
    implicit_wait: int = 10
    page_load_timeout: int = 30
    script_timeout: int = 30
    download_dir: Optional[str] = None
    user_data_dir: Optional[str] = None
    binary_location: Optional[str] = None
    extensions: List[str] = None
    prefs: Dict[str, Any] = None
    arguments: List[str] = None


class WebDriverFactory:
    """Factory for creating and managing WebDriver instances."""
    
    _drivers: Dict[str, webdriver.Remote] = {}
    
    @classmethod
    def create_driver(cls, config: BrowserConfig) -> webdriver.Remote:
        """Create WebDriver instance based on configuration."""
        browser = config.browser.lower()
        
        if browser == "chrome":
            return cls._create_chrome_driver(config)
        elif browser == "firefox":
            return cls._create_firefox_driver(config)
        elif browser == "safari":
            return cls._create_safari_driver(config)
        else:
            raise TestEnvironmentError(f"Unsupported browser: {browser}")
    
    @classmethod
    def _create_chrome_driver(cls, config: BrowserConfig) -> webdriver.Chrome:
        """Create Chrome WebDriver instance."""
        options = ChromeOptions()
        
        if config.headless:
            options.add_argument("--headless")
        
        options.add_argument(f"--window-size={config.window_size[0]},{config.window_size[1]}")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        if config.download_dir:
            prefs = {"download.default_directory": config.download_dir}
            options.add_experimental_option("prefs", prefs)
        
        if config.user_data_dir:
            options.add_argument(f"--user-data-dir={config.user_data_dir}")
        
        if config.binary_location:
            options.binary_location = config.binary_location
        
        if config.extensions:
            for ext in config.extensions:
                options.add_extension(ext)
        
        if config.arguments:
            for arg in config.arguments:
                options.add_argument(arg)
        
        if config.prefs:
            options.add_experimental_option("prefs", config.prefs)
        
        try:
            driver = webdriver.Chrome(options=options)
            cls._setup_driver_timeouts(driver, config)
            logger.info(f"Chrome WebDriver created successfully")
            return driver
            
        except Exception as e:
            error_msg = f"Failed to create Chrome WebDriver: {str(e)}"
            logger.error(error_msg)
            raise TestEnvironmentError(error_msg)
    
    @classmethod
    def _create_firefox_driver(cls, config: BrowserConfig) -> webdriver.Firefox:
        """Create Firefox WebDriver instance."""
        options = FirefoxOptions()
        
        if config.headless:
            options.add_argument("--headless")
        
        if config.binary_location:
            options.binary_location = config.binary_location
        
        if config.arguments:
            for arg in config.arguments:
                options.add_argument(arg)
        
        try:
            driver = webdriver.Firefox(options=options)
            driver.set_window_size(*config.window_size)
            cls._setup_driver_timeouts(driver, config)
            logger.info(f"Firefox WebDriver created successfully")
            return driver
            
        except Exception as e:
            error_msg = f"Failed to create Firefox WebDriver: {str(e)}"
            logger.error(error_msg)
            raise TestEnvironmentError(error_msg)
    
    @classmethod
    def _create_safari_driver(cls, config: BrowserConfig) -> webdriver.Safari:
        """Create Safari WebDriver instance."""
        try:
            driver = webdriver.Safari()
            driver.set_window_size(*config.window_size)
            cls._setup_driver_timeouts(driver, config)
            logger.info(f"Safari WebDriver created successfully")
            return driver
            
        except Exception as e:
            error_msg = f"Failed to create Safari WebDriver: {str(e)}"
            logger.error(error_msg)
            raise TestEnvironmentError(error_msg)
    
    @classmethod
    def _setup_driver_timeouts(cls, driver: webdriver.Remote, config: BrowserConfig) -> None:
        """Setup timeouts for WebDriver."""
        driver.implicitly_wait(config.implicit_wait)
        driver.set_page_load_timeout(config.page_load_timeout)
        driver.set_script_timeout(config.script_timeout)
    
    @classmethod
    def get_driver(cls, name: str = "default") -> Optional[webdriver.Remote]:
        """Get existing WebDriver instance by name."""
        return cls._drivers.get(name)
    
    @classmethod
    def register_driver(cls, driver: webdriver.Remote, name: str = "default") -> None:
        """Register WebDriver instance with name."""
        cls._drivers[name] = driver
        logger.debug(f"WebDriver registered with name: {name}")
    
    @classmethod
    def quit_driver(cls, name: str = "default") -> None:
        """Quit and remove WebDriver instance."""
        if name in cls._drivers:
            try:
                cls._drivers[name].quit()
                del cls._drivers[name]
                logger.debug(f"WebDriver '{name}' quit successfully")
            except Exception as e:
                logger.warning(f"Error quitting WebDriver '{name}': {str(e)}")
    
    @classmethod
    def quit_all_drivers(cls) -> None:
        """Quit all registered WebDriver instances."""
        for name in list(cls._drivers.keys()):
            cls.quit_driver(name)
        logger.info("All WebDrivers quit successfully")