import json
from pathlib import Path
from typing import Any

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self.load()

    def load(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        return {}

    def save(self) -> None:
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value
        self.save()
