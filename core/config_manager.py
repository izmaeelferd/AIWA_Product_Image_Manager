import json
from pathlib import Path
from typing import Any

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load()

    def _load(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value
        self._save()

    def get_last_folder(self, key: str) -> str:
        return self.get(f"last_folder_{key}", "")
