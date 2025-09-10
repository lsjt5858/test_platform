import os
from configparser import ConfigParser

class ConfigLoader:
    def __init__(self, env="default"):
        self.config = ConfigParser()
        config_path = f"config/env/config_{env}.ini"
        if not os.path.exists(config_path):
            config_path = "config/env/config_default.ini"
        self.config.read(config_path)

    def get(self, section, key, fallback=None):
        return self.config.get(section, key, fallback=fallback)