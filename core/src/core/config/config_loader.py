import os
import json
import yaml
from pathlib import Path
from configparser import ConfigParser
from typing import Any, Dict, Optional, Union

from ..base_util.logger import get_logger
from ..base_util.exception_handler import TestConfigError
from ..base_util.singleton import Singleton

logger = get_logger(__name__)


class ConfigLoader(Singleton):
    """Enhanced configuration loader with support for multiple formats and environments."""
    
    def __init__(self, env: str = "default", config_dir: str = "config"):
        super().__init__()
        if hasattr(self, '_config_loaded'):
            return
            
        self.env = env
        self.config_dir = Path(config_dir)
        self.config = ConfigParser()
        self._config_cache: Dict[str, Any] = {}
        
        self._load_configurations()
        self._config_loaded = True
    
    def _load_configurations(self):
        """Load configuration from multiple sources and formats."""
        # Load INI configuration
        self._load_ini_config()
        
        # Load JSON configuration if exists
        self._load_json_config()
        
        # Load YAML configuration if exists  
        self._load_yaml_config()
        
        # Load environment variables
        self._load_env_vars()
    
    def _load_ini_config(self):
        """Load INI configuration files."""
        env_dir = self.config_dir / "env"
        
        # Try environment-specific config first
        config_files = [
            env_dir / f"config_{self.env}.ini",
            env_dir / "config_default.ini",
            self.config_dir / "config.ini"
        ]
        
        loaded_files = []
        for config_file in config_files:
            if config_file.exists():
                try:
                    self.config.read(str(config_file))
                    loaded_files.append(str(config_file))
                    logger.debug(f"Loaded INI config: {config_file}")
                except Exception as e:
                    logger.warning(f"Failed to load INI config {config_file}: {str(e)}")
        
        if not loaded_files:
            logger.warning("No INI configuration files found")
    
    def _load_json_config(self):
        """Load JSON configuration files."""
        json_files = [
            self.config_dir / f"config_{self.env}.json",
            self.config_dir / "config.json"
        ]
        
        for json_file in json_files:
            if json_file.exists():
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json_config = json.load(f)
                        self._config_cache.update(json_config)
                        logger.debug(f"Loaded JSON config: {json_file}")
                        break
                except Exception as e:
                    logger.warning(f"Failed to load JSON config {json_file}: {str(e)}")
    
    def _load_yaml_config(self):
        """Load YAML configuration files."""
        yaml_files = [
            self.config_dir / f"config_{self.env}.yaml",
            self.config_dir / f"config_{self.env}.yml",
            self.config_dir / "config.yaml",
            self.config_dir / "config.yml"
        ]
        
        for yaml_file in yaml_files:
            if yaml_file.exists():
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        yaml_config = yaml.safe_load(f)
                        if yaml_config:
                            self._config_cache.update(yaml_config)
                            logger.debug(f"Loaded YAML config: {yaml_file}")
                            break
                except Exception as e:
                    logger.warning(f"Failed to load YAML config {yaml_file}: {str(e)}")
    
    def _load_env_vars(self):
        """Load configuration from environment variables."""
        # Load environment variables with TEST_PLATFORM_ prefix
        env_config = {}
        for key, value in os.environ.items():
            if key.startswith('TEST_PLATFORM_'):
                # Convert TEST_PLATFORM_DB_HOST to db.host
                config_key = key[14:].lower().replace('_', '.')
                env_config[config_key] = value
        
        if env_config:
            self._config_cache.update({"env": env_config})
            logger.debug(f"Loaded {len(env_config)} environment variables")
    
    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get configuration value from INI format."""
        try:
            return self.config.get(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    def get_value(self, key_path: str, fallback: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'db.host')."""
        # Check environment variables first
        env_key = f"env.{key_path}"
        if env_key in self._config_cache.get("env", {}):
            return self._config_cache["env"][env_key]
        
        # Navigate through nested dictionary
        keys = key_path.split('.')
        current = self._config_cache
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return fallback
        
        return current
    
    def get_section(self, section: str) -> Dict[str, str]:
        """Get entire section as dictionary from INI config."""
        try:
            return dict(self.config.items(section))
        except Exception:
            return {}
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary."""
        all_config = {}
        
        # Add INI sections
        for section in self.config.sections():
            all_config[section] = self.get_section(section)
        
        # Add JSON/YAML config
        all_config.update(self._config_cache)
        
        return all_config
    
    def has_section(self, section: str) -> bool:
        """Check if section exists in INI config."""
        return self.config.has_section(section)
    
    def has_option(self, section: str, key: str) -> bool:
        """Check if option exists in INI config."""
        return self.config.has_option(section, key)
    
    def reload_config(self):
        """Reload configuration from all sources."""
        self.config.clear()
        self._config_cache.clear()
        self._load_configurations()
        logger.info("Configuration reloaded")


# Global config instance
_global_config: Optional[ConfigLoader] = None


def get_config(env: str = None, config_dir: str = None) -> ConfigLoader:
    """Get global configuration instance."""
    global _global_config
    
    if _global_config is None:
        env = env or os.getenv('TEST_ENV', 'default')
        config_dir = config_dir or os.getenv('CONFIG_DIR', 'config')
        _global_config = ConfigLoader(env=env, config_dir=config_dir)
    
    return _global_config


def reload_global_config():
    """Reload global configuration."""
    global _global_config
    if _global_config:
        _global_config.reload_config()