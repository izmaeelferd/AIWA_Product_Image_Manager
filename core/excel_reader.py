import pandas as pd
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ExcelReader:
    @staticmethod
    def read_excel(file_path: str) -> Optional[pd.DataFrame]:
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            return df
        except Exception as e:
            logger.error(f"Excel read failed: {e}")
            return None

    @staticmethod
    def _clean_header(header: str) -> str:
        """Remove leading/trailing special characters, spaces, underscores, hyphens, dots, brackets, parentheses, etc."""
        if not isinstance(header, str):
            return ''
        # Remove leading/trailing whitespace and newlines
        header = header.strip()
        # Remove leading/trailing punctuation like *, ., -, _, etc.
        header = re.sub(r'^[\*\s\.\-_\(\)\[\]\{\}]+', '', header)
        header = re.sub(r'[\*\s\.\-_\(\)\[\]\{\}]+$', '', header)
        # Remove internal dots, underscores, hyphens (optional? but we will keep them for matching? We'll remove all non-alphanumeric for normalization)
        # For detection, we just clean and uppercase
        header = re.sub(r'[^A-Za-z0-9]', '', header)
        return header.upper()

    @staticmethod
    def detect_columns(df: pd.DataFrame) -> Dict[str, str]:
        """
        Auto-detect SKU and Barcode columns from a wide range of possible headers,
        ignoring leading special characters (*, etc.) and normalizing.
        """
        columns = {}
        # Clean and normalize column names
        cleaned_headers = {}
        for col in df.columns:
            cleaned = ExcelReader._clean_header(str(col))
            cleaned_headers[col] = cleaned

        # Define keyword lists (all uppercase, cleaned)
        sku_keywords = [
            'SKU', 'PRODUCTSKU', 'SELLERSKU', 'MERCHANTSKU', 'ITEMCODE',
            'PRODUCTCODE', 'CODE', 'MODEL', 'STOCKCODE', 'REFERENCE'
        ]
        barcode_keywords = [
            'BARCODE', 'EAN', 'UPC', 'GTIN', 'EAN13', 'EAN8',
            'PRODUCTBARCODE', 'BARCODENO', 'BARCODENUMBER'
        ]

        # First pass: find columns by keyword
        sku_col = None
        barcode_col = None
        for col, clean in cleaned_headers.items():
            if not sku_col:
                for kw in sku_keywords:
                    if clean == kw or clean.startswith(kw):
                        sku_col = col
                        break
            if not barcode_col:
                for kw in barcode_keywords:
                    if clean == kw or clean.startswith(kw):
                        barcode_col = col
                        break
            if sku_col and barcode_col:
                break

        # If not found, use heuristics: first column that looks like SKU (alphanumeric with letters)
        if not sku_col:
            for col in df.columns:
                # Check if column contains values with letters and digits
                sample = df[col].dropna().astype(str).head(20)
                # Check if more than 80% of values have at least one letter
                letter_count = sum(1 for v in sample if re.search(r'[A-Za-z]', v))
                if len(sample) > 0 and letter_count / len(sample) >= 0.8:
                    sku_col = col
                    break
            if sku_col:
                logger.info(f"Heuristic SKU column: {sku_col}")

        if not barcode_col:
            # Look for column with mostly numeric values
            for col in df.columns:
                if col == sku_col:
                    continue
                sample = df[col].dropna().astype(str).head(20)
                digit_count = sum(1 for v in sample if re.match(r'^\d+$', v))
                if len(sample) > 0 and digit_count / len(sample) >= 0.9:
                    barcode_col = col
                    break
            if barcode_col:
                logger.info(f"Heuristic Barcode column: {barcode_col}")

        # Fallback: use first two columns
        if not sku_col and len(df.columns) >= 1:
            sku_col = df.columns[0]
            logger.warning(f"Fallback SKU column: {sku_col}")
        if not barcode_col and len(df.columns) >= 2:
            barcode_col = df.columns[1]
            logger.warning(f"Fallback Barcode column: {barcode_col}")

        columns['sku'] = sku_col
        columns['barcode'] = barcode_col
        columns['cleaned_headers'] = cleaned_headers  # for debug

        logger.info(f"Detected columns: SKU='{sku_col}', Barcode='{barcode_col}'")
        # Log normalized headers
        for col, clean in cleaned_headers.items():
            logger.debug(f"Original: '{col}' -> Cleaned: '{clean}'")

        return columns

    @staticmethod
    def validate_sku_column(df: pd.DataFrame, sku_col: str) -> bool:
        """Validate that SKU column contains alphanumeric with alphabetic prefix, not mostly numeric."""
        sample = df[sku_col].dropna().astype(str).head(50)
        if len(sample) == 0:
            return False
        # Count rows that contain at least one letter
        has_letter = sum(1 for v in sample if re.search(r'[A-Za-z]', v))
        # Also check that not more than 90% are purely numeric
        is_numeric = sum(1 for v in sample if re.match(r'^\d+$', v))
        # If more than 90% are purely numeric, reject
        if len(sample) > 0 and is_numeric / len(sample) > 0.9:
            return False
        # If less than 80% have a letter, maybe it's not SKU
        if has_letter / len(sample) < 0.8:
            return False
        return True
