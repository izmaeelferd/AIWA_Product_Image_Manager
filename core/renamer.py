import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from .sku_detector import SKUDetector
import pandas as pd
from collections import defaultdict

logger = logging.getLogger(__name__)

class Renamer:
    @staticmethod
    def rename_files(directory: str, mapping: Dict[str, str]) -> List[Tuple[str, str, bool]]:
        results = []
        for old_name, new_name in mapping.items():
            old_path = Path(directory) / old_name
            new_path = Path(directory) / new_name
            if old_path.exists():
                try:
                    old_path.rename(new_path)
                    results.append((old_name, new_name, True))
                except Exception as e:
                    logger.error(f"Rename failed: {e}")
                    results.append((old_name, new_name, False))
            else:
                results.append((old_name, new_name, False))
        return results

    @staticmethod
    def generate_rename_mapping(images: List[str], sku_barcode_map: Dict[str, str]) -> Dict[str, str]:
        mapping = {}
        norm_keys = list(sku_barcode_map.keys())
        groups = defaultdict(list)
        for img in images:
            raw_sku = SKUDetector.extract_sku(img)
            if not raw_sku:
                continue
            norm_sku = SKUDetector.normalize_sku(raw_sku)
            order = SKUDetector.extract_order_number(img)
            groups[norm_sku].append((img, raw_sku, order))

        for norm_sku, items in groups.items():
            items.sort(key=lambda x: x[2])
            if norm_sku not in sku_barcode_map:
                continue
            barcode = sku_barcode_map[norm_sku]
            for idx, (img, raw, order) in enumerate(items):
                suffix = idx + 1
                ext = Path(img).suffix
                new_name = f"{barcode}{ext}" if suffix == 1 else f"{barcode}_{suffix}{ext}"
                mapping[img] = new_name

        return mapping
