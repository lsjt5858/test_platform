"""
Configuration management module for the test platform.
Provides centralized configuration loading and management.
"""

from .config_loader import ConfigLoader, get_config, reload_global_config

__all__ = [
    'ConfigLoader',
    'get_config', 
    'reload_global_config'
]