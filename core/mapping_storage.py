import json
from pathlib import Path
from typing import Dict, Optional

class MappingStorage:
    def __init__(self, storage_file: str = "config/supplier_mappings.json"):
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self.mappings = self._load()

    def _load(self) -> Dict:
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save(self):
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.mappings, f, indent=4)

    def get_mapping(self, supplier: str) -> Optional[Dict]:
        return self.mappings.get(supplier)

    def set_mapping(self, supplier: str, mapping: Dict):
        self.mappings[supplier] = mapping
        self._save()

    def delete_mapping(self, supplier: str):
        if supplier in self.mappings:
            del self.mappings[supplier]
            self._save()

    def get_all_suppliers(self) -> list:
        return list(self.mappings.keys())
