"""
Global pytest configuration and fixtures for the test automation framework.

This file contains shared fixtures and configuration that can be used
across all test modules in the project.
"""

import os
import pytest
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

# Import our configuration manager
try:
    from config.config_manager import ConfigManager, get_config
except ImportError:
    # Fallback if config_manager is not available
    class ConfigManager:
        def get_environment_config(self, env_name=None):
            class EnvConfig:
                base_url = "http://localhost:5001"
                timeout = 30
                debug = True
            return EnvConfig()
        
        def get_browser_config(self, browser_name=None):
            class BrowserConfig:
                name = "chrome"
                headless = False
                window_size = (1920, 1080)
                implicit_wait = 10
                page_load_timeout = 30
            return BrowserConfig()
        
        def get_screenshots_dir(self):
            return Path("reports/screenshots")
        
        def get_logs_dir(self):
            return Path("reports/logs")
    
    def get_config():
        return ConfigManager()


def pytest_addoption(parser):
    """Add custom command line options for pytest"""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to run tests on: chrome, firefox, edge, headless"
    )
    parser.addoption(
        "--env",
        action="store", 
        default="local",
        help="Environment to run tests against: local, staging, production"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode"
    )


def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    # Register custom markers
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "api: mark test as API test")
    config.addinivalue_line("markers", "ui: mark test as UI test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "screenshots").mkdir(exist_ok=True)
    (reports_dir / "logs").mkdir(exist_ok=True)
    (reports_dir / "html").mkdir(exist_ok=True)
    (reports_dir / "json").mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def config():
    """Global configuration fixture"""
    return get_config()


@pytest.fixture(scope="session")
def environment(request):
    """Environment configuration fixture"""
    env_name = request.config.getoption("--env")
    return env_name


@pytest.fixture(scope="session")
def browser_name(request):
    """Browser name fixture"""
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    
    if headless and browser != "headless":
        return "headless"
    return browser


@pytest.fixture(scope="session")
def base_url(config, environment):
    """Base URL fixture for the test environment"""
    env_config = config.get_environment_config(environment)
    return env_config.base_url


@pytest.fixture(scope="function")
def driver(request, config, browser_name):
    """
    WebDriver fixture that provides browser instances for tests.
    
    This fixture:
    - Creates a WebDriver instance based on the browser parameter
    - Configures the browser with appropriate options
    - Handles cleanup after test completion
    - Captures screenshots on test failure
    """
    browser_config = config.get_browser_config(browser_name)
    driver_instance = None
    
    try:
        if browser_config.name == "chrome" or browser_name == "headless":
            options = ChromeOptions()
            
            # Chrome-specific options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_argument(f"--window-size={browser_config.window_size[0]},{browser_config.window_size[1]}")
            
            if browser_config.headless or browser_name == "headless":
                options.add_argument("--headless")
            
            # Create Chrome driver
            service = ChromeService(ChromeDriverManager().install())
            driver_instance = webdriver.Chrome(service=service, options=options)
            
        elif browser_config.name == "firefox":
            options = FirefoxOptions()
            
            if browser_config.headless:
                options.add_argument("--headless")
            
            # Create Firefox driver
            service = FirefoxService(GeckoDriverManager().install())
            driver_instance = webdriver.Firefox(service=service, options=options)
            
        elif browser_config.name == "edge":
            options = EdgeOptions()
            
            if browser_config.headless:
                options.add_argument("--headless")
            
            # Create Edge driver
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver_instance = webdriver.Edge(service=service, options=options)
            
        else:
            raise ValueError(f"Unsupported browser: {browser_config.name}")
        
        # Configure timeouts
        driver_instance.implicitly_wait(browser_config.implicit_wait)
        driver_instance.set_page_load_timeout(browser_config.page_load_timeout)
        
        # Maximize window if not headless
        if not browser_config.headless and browser_name != "headless":
            driver_instance.maximize_window()
        else:
            driver_instance.set_window_size(*browser_config.window_size)
        
        yield driver_instance
        
    except Exception as e:
        logging.error(f"Failed to create WebDriver: {e}")
        raise
        
    finally:
        # Cleanup
        if driver_instance:
            # Take screenshot on test failure
            if request.node.rep_call.failed if hasattr(request.node, 'rep_call') else False:
                take_screenshot(driver_instance, request.node.name, config)
            
            driver_instance.quit()


def take_screenshot(driver, test_name, config):
    """Take screenshot on test failure"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"{test_name}_{timestamp}.png"
        screenshot_path = config.get_screenshots_dir() / screenshot_name
        
        driver.save_screenshot(str(screenshot_path))
        logging.info(f"Screenshot saved: {screenshot_path}")
        
    except Exception as e:
        logging.error(f"Failed to take screenshot: {e}")


@pytest.fixture(scope="function")
def api_client(config, environment):
    """API client fixture for API testing"""
    import requests
    
    class APIClient:
        def __init__(self, base_url, timeout=30):
            self.base_url = base_url.rstrip('/')
            self.timeout = timeout
            self.session = requests.Session()
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
        
        def get(self, endpoint, **kwargs):
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            return self.session.get(url, timeout=self.timeout, **kwargs)
        
        def post(self, endpoint, **kwargs):
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            return self.session.post(url, timeout=self.timeout, **kwargs)
        
        def put(self, endpoint, **kwargs):
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            return self.session.put(url, timeout=self.timeout, **kwargs)
        
        def delete(self, endpoint, **kwargs):
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            return self.session.delete(url, timeout=self.timeout, **kwargs)
    
    env_config = config.get_environment_config(environment)
    api_base_url = getattr(env_config, 'api_base_url', env_config.base_url + '/api')
    
    return APIClient(api_base_url, env_config.timeout)


@pytest.fixture(scope="function")
def test_user_data():
    """Test user data fixture"""
    return {
        'admin': {
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin'
        },
        'regular_user': {
            'username': 'testuser', 
            'password': 'password123',
            'role': 'user'
        }
    }


@pytest.fixture(scope="function")
def logger():
    """Logger fixture for tests"""
    # Create logger
    test_logger = logging.getLogger('test_automation')
    test_logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("reports/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create file handler
    log_file = logs_dir / f"test_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    if not test_logger.handlers:
        test_logger.addHandler(file_handler)
    
    return test_logger


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for screenshot functionality"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)