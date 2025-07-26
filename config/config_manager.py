"""
Configuration Manager for Test Automation Framework

This module handles environment-specific configurations and settings
for the test automation framework, following SOLID principles.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BrowserConfig:
    """Browser configuration settings"""
    name: str = "chrome"
    headless: bool = False
    window_size: tuple = (1920, 1080)
    implicit_wait: int = 10
    page_load_timeout: int = 30
    download_dir: Optional[str] = None


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration"""
    name: str
    base_url: str
    api_base_url: str
    database_url: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    debug: bool = False


class ConfigManager:
    """
    Central configuration manager for the test automation framework.
    
    Provides environment-specific configurations and browser settings
    following the Single Responsibility Principle.
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self._load_environment_variables()
        self._setup_environments()
        self._setup_browser_configs()
        
    def _load_environment_variables(self):
        """Load environment variables from .env file if present"""
        env_file = self.project_root / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
    
    def _setup_environments(self):
        """Setup environment configurations"""
        self.environments = {
            'local': EnvironmentConfig(
                name='local',
                base_url=os.getenv('LOCAL_BASE_URL', 'http://localhost:5001'),
                api_base_url=os.getenv('LOCAL_API_URL', 'http://localhost:5001/api'),
                timeout=int(os.getenv('LOCAL_TIMEOUT', '30')),
                debug=True
            ),
            'staging': EnvironmentConfig(
                name='staging',
                base_url=os.getenv('STAGING_BASE_URL', 'https://staging.example.com'),
                api_base_url=os.getenv('STAGING_API_URL', 'https://staging.example.com/api'),
                timeout=int(os.getenv('STAGING_TIMEOUT', '45')),
                debug=False
            ),
            'production': EnvironmentConfig(
                name='production',
                base_url=os.getenv('PROD_BASE_URL', 'https://production.example.com'),
                api_base_url=os.getenv('PROD_API_URL', 'https://production.example.com/api'),
                timeout=int(os.getenv('PROD_TIMEOUT', '60')),
                debug=False
            )
        }
    
    def _setup_browser_configs(self):
        """Setup browser configurations"""
        self.browser_configs = {
            'chrome': BrowserConfig(
                name='chrome',
                headless=os.getenv('HEADLESS', 'false').lower() == 'true',
                window_size=(
                    int(os.getenv('WINDOW_WIDTH', '1920')),
                    int(os.getenv('WINDOW_HEIGHT', '1080'))
                ),
                implicit_wait=int(os.getenv('IMPLICIT_WAIT', '10')),
                page_load_timeout=int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
            ),
            'firefox': BrowserConfig(
                name='firefox',
                headless=os.getenv('HEADLESS', 'false').lower() == 'true',
                window_size=(
                    int(os.getenv('WINDOW_WIDTH', '1920')),
                    int(os.getenv('WINDOW_HEIGHT', '1080'))
                ),
                implicit_wait=int(os.getenv('IMPLICIT_WAIT', '10')),
                page_load_timeout=int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
            ),
            'edge': BrowserConfig(
                name='edge',
                headless=os.getenv('HEADLESS', 'false').lower() == 'true',
                window_size=(
                    int(os.getenv('WINDOW_WIDTH', '1920')),
                    int(os.getenv('WINDOW_HEIGHT', '1080'))
                ),
                implicit_wait=int(os.getenv('IMPLICIT_WAIT', '10')),
                page_load_timeout=int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
            ),
            'headless': BrowserConfig(
                name='chrome',
                headless=True,
                window_size=(
                    int(os.getenv('WINDOW_WIDTH', '1920')),
                    int(os.getenv('WINDOW_HEIGHT', '1080'))
                ),
                implicit_wait=int(os.getenv('IMPLICIT_WAIT', '10')),
                page_load_timeout=int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
            )
        }
    
    def get_environment_config(self, env_name: str = None) -> EnvironmentConfig:
        """
        Get environment configuration by name.
        
        Args:
            env_name: Environment name (local, staging, production)
            
        Returns:
            EnvironmentConfig object
            
        Raises:
            ValueError: If environment name is not found
        """
        if env_name is None:
            env_name = os.getenv('TEST_ENV', 'local')
            
        if env_name not in self.environments:
            raise ValueError(f"Environment '{env_name}' not found. Available: {list(self.environments.keys())}")
            
        return self.environments[env_name]
    
    def get_browser_config(self, browser_name: str = None) -> BrowserConfig:
        """
        Get browser configuration by name.
        
        Args:
            browser_name: Browser name (chrome, firefox, edge, headless)
            
        Returns:
            BrowserConfig object
            
        Raises:
            ValueError: If browser name is not found
        """
        if browser_name is None:
            browser_name = os.getenv('DEFAULT_BROWSER', 'chrome')
            
        if browser_name not in self.browser_configs:
            raise ValueError(f"Browser '{browser_name}' not found. Available: {list(self.browser_configs.keys())}")
            
        return self.browser_configs[browser_name]
    
    def get_reports_dir(self) -> Path:
        """Get reports directory path"""
        reports_dir = self.project_root / 'reports'
        reports_dir.mkdir(exist_ok=True)
        return reports_dir
    
    def get_screenshots_dir(self) -> Path:
        """Get screenshots directory path"""
        screenshots_dir = self.get_reports_dir() / 'screenshots'
        screenshots_dir.mkdir(exist_ok=True)
        return screenshots_dir
    
    def get_logs_dir(self) -> Path:
        """Get logs directory path"""
        logs_dir = self.get_reports_dir() / 'logs'
        logs_dir.mkdir(exist_ok=True)
        return logs_dir
    
    def get_test_data_dir(self) -> Path:
        """Get test data directory path"""
        test_data_dir = self.project_root / 'test_data'
        test_data_dir.mkdir(exist_ok=True)
        return test_data_dir
    
    def create_directories(self):
        """Create all necessary directories"""
        directories = [
            'reports/html',
            'reports/json', 
            'reports/screenshots',
            'reports/logs',
            'test_data',
            'config',
            'pages',
            'utils',
            'tests/ui',
            'tests/api',
            'tests/integration'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py files for Python packages
            if any(pkg in directory for pkg in ['pages', 'utils', 'tests', 'config']):
                init_file = dir_path / '__init__.py'
                if not init_file.exists():
                    init_file.touch()
    
    def get_database_config(self, env_name: str = None) -> Dict[str, Any]:
        """
        Get database configuration for the specified environment.
        
        Args:
            env_name: Environment name
            
        Returns:
            Database configuration dictionary
        """
        env_config = self.get_environment_config(env_name)
        
        return {
            'url': env_config.database_url,
            'timeout': env_config.timeout,
            'retry_count': env_config.retry_count
        }
    
    def get_api_config(self, env_name: str = None) -> Dict[str, Any]:
        """
        Get API configuration for the specified environment.
        
        Args:
            env_name: Environment name
            
        Returns:
            API configuration dictionary
        """
        env_config = self.get_environment_config(env_name)
        
        return {
            'base_url': env_config.api_base_url,
            'timeout': env_config.timeout,
            'retry_count': env_config.retry_count,
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        }
    
    def save_config_to_file(self, filepath: str = None):
        """
        Save current configuration to a JSON file.
        
        Args:
            filepath: Path to save the configuration file
        """
        if filepath is None:
            filepath = self.project_root / 'config' / 'current_config.json'
        
        config_data = {
            'environments': {
                name: {
                    'name': config.name,
                    'base_url': config.base_url,
                    'api_base_url': config.api_base_url,
                    'timeout': config.timeout,
                    'retry_count': config.retry_count,
                    'debug': config.debug
                }
                for name, config in self.environments.items()
            },
            'browsers': {
                name: {
                    'name': config.name,
                    'headless': config.headless,
                    'window_size': config.window_size,
                    'implicit_wait': config.implicit_wait,
                    'page_load_timeout': config.page_load_timeout
                }
                for name, config in self.browser_configs.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def validate_configuration(self, env_name: str = None, browser_name: str = None) -> bool:
        """
        Validate the configuration for the specified environment and browser.
        
        Args:
            env_name: Environment name to validate
            browser_name: Browser name to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate environment config
            env_config = self.get_environment_config(env_name)
            if not env_config.base_url:
                return False
                
            # Validate browser config
            browser_config = self.get_browser_config(browser_name)
            if not browser_config.name:
                return False
                
            return True
            
        except (ValueError, AttributeError):
            return False


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        ConfigManager instance
    """
    return config_manager


# Convenience functions for quick access
def get_base_url(env_name: str = None) -> str:
    """Get base URL for the specified environment"""
    return config_manager.get_environment_config(env_name).base_url


def get_api_base_url(env_name: str = None) -> str:
    """Get API base URL for the specified environment"""
    return config_manager.get_environment_config(env_name).api_base_url


def is_debug_mode(env_name: str = None) -> bool:
    """Check if debug mode is enabled for the specified environment"""
    return config_manager.get_environment_config(env_name).debug


def get_timeout(env_name: str = None) -> int:
    """Get timeout value for the specified environment"""
    return config_manager.get_environment_config(env_name).timeout


# Initialize directories on import
config_manager.create_directories()