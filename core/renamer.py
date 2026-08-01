import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from .sku_detector import SKUDetector
import pandas as pd
import time
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
        debug_lines = []
        debug_data = []

        # Group images by normalized SKU
        groups = defaultdict(list)
        for img in images:
            raw_sku = SKUDetector.extract_sku(img)
            if not raw_sku:
                continue
            norm_sku = SKUDetector.normalize_sku(raw_sku)
            order = SKUDetector.extract_order_number(img)
            groups[norm_sku].append((img, raw_sku, order))

        # Process each group
        for norm_sku, items in groups.items():
            # Sort by order number
            items.sort(key=lambda x: x[2])
            if norm_sku not in sku_barcode_map:
                # Unmatched
                for img, raw, order in items:
                    debug_lines.append(f"Image: {img}")
                    debug_lines.append(f"Detected SKU: {raw}")
                    debug_lines.append(f"Normalized: {norm_sku}")
                    debug_lines.append("Lookup: NOT FOUND")
                    closest = SKUDetector.find_closest_matches(norm_sku, norm_keys)
                    debug_lines.append(f"Closest matches: {closest if closest else 'None'}")
                    debug_lines.append("Status: UNMATCHED")
                    debug_lines.append("-" * 30)
                    debug_data.append({
                        'Image': img,
                        'Detected SKU': raw,
                        'Normalized SKU': norm_sku,
                        'Excel SKU': '',
                        'Barcode': '',
                        'Matched': 'No',
                        'Reason': f'Not in dict. Closest: {closest if closest else "None"}'
                    })
                continue

            barcode = sku_barcode_map[norm_sku]
            for idx, (img, raw, order) in enumerate(items):
                suffix = idx + 1
                ext = Path(img).suffix
                new_name = f"{barcode}{ext}" if suffix == 1 else f"{barcode}_{suffix}{ext}"
                mapping[img] = new_name
                debug_lines.append(f"Image: {img}")
                debug_lines.append(f"Detected SKU: {raw}")
                debug_lines.append(f"Normalized: {norm_sku}")
                debug_lines.append("Lookup: FOUND")
                debug_lines.append(f"Barcode: {barcode}")
                debug_lines.append(f"New Name: {new_name}")
                debug_lines.append("Status: SUCCESS")
                debug_lines.append("-" * 30)
                debug_data.append({
                    'Image': img,
                    'Detected SKU': raw,
                    'Normalized SKU': norm_sku,
                    'Excel SKU': raw,
                    'Barcode': barcode,
                    'Matched': 'Yes',
                    'Reason': 'Exact match'
                })

        # Write debug log
        try:
            log_path = Path("debug_log.txt")
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("RENAME DEBUG LOG\n")
                f.write("=" * 50 + "\n")
                f.write(f"Total images processed: {len(images)}\n")
                f.write(f"Matched images: {len(mapping)}\n")
                f.write(f"Unmatched images: {len(images) - len(mapping)}\n")
                f.write("\n")
                f.write("\n".join(debug_lines))
            logger.info(f"Debug log written to {log_path}")
        except Exception as e:
            logger.error(f"Failed to write debug log: {e}")

        if debug_data:
            try:
                df = pd.DataFrame(debug_data)
                df.to_excel("debug_report.xlsx", index=False)
                logger.info("Debug report saved to debug_report.xlsx")
            except Exception as e:
                logger.error(f"Failed to generate debug report: {e}")

        # Summary
        matched_skus = set()
        unmatched_skus = set()
        for d in debug_data:
            if d['Matched'] == 'Yes':
                matched_skus.add(d['Normalized SKU'])
            else:
                unmatched_skus.add(d['Normalized SKU'])

        logger.info("=== RENAME MAPPING SUMMARY ===")
        logger.info(f"Total images: {len(images)}")
        logger.info(f"Matched images: {len(mapping)}")
        logger.info(f"Unmatched images: {len(images) - len(mapping)}")
        logger.info(f"Matched SKUs (unique): {len(matched_skus)}")
        logger.info(f"Unmatched SKUs (unique): {len(unmatched_skus)}")
        logger.info(f"Mapping generated for {len(mapping)} images.")

        return mapping
