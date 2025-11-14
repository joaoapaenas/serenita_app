# app/core/config_service.py
import toml
from typing import Any

class ConfigService:
    def __init__(self, config_path: str = "config.toml"):
        with open(config_path, "r") as f:
            self._config = toml.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._config
        for k in keys:
            if not isinstance(value, dict) or k not in value:
                return default
            value = value[k]
        return value
