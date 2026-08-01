import re
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

class SKUDetector:
    @staticmethod
    def normalize_sku(sku: str) -> str:
        """Normalize SKU: remove all non-alphanumeric, uppercase."""
        if not sku:
            return ''
        sku = re.sub(r'[^A-Za-z0-9]', '', sku)
        return sku.upper()

    @staticmethod
    def extract_sku(filename: str) -> Optional[str]:
        """
        Extract raw SKU from filename (e.g., 'AW-1011-1.jpeg' -> 'AW-1011').
        Handles parentheses, brackets, spaces, and any alphabetical prefix.
        """
        name = Path(filename).stem
        name = re.sub(r'\s*\([^)]*\)$', '', name)
        name = name.replace(' ', '').replace('[', '').replace(']', '')
        match = re.match(r'^([A-Za-z]+[-_]?\d+)', name)
        if match:
            return match.group(1)
        match = re.search(r'([A-Za-z]+[-_]?\d+)', name)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def extract_order_number(filename: str) -> int:
        """Extract image order number from filename, default 1."""
        name = Path(filename).stem
        sku = SKUDetector.extract_sku(name)
        if sku:
            remaining = re.sub(re.escape(sku), '', name, flags=re.IGNORECASE)
        else:
            remaining = name
        numbers = re.findall(r'\d+', remaining)
        if numbers:
            return int(numbers[0])
        return 1

    @staticmethod
    def find_closest_matches(norm_sku: str, available_keys: List[str]) -> List[str]:
        matches = []
        letters = re.match(r'^([A-Z]+)', norm_sku)
        if letters:
            prefix = letters.group(1)
            for key in available_keys:
                if key.startswith(prefix):
                    matches.append(key)
        digits = re.search(r'(\d+)$', norm_sku)
        if digits:
            num = digits.group(1)
            for key in available_keys:
                if key.endswith(num):
                    matches.append(key)
        unique = list(dict.fromkeys(matches))
        return unique[:5]
