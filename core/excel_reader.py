import pandas as pd
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

logger = logging.getLogger(__name__)

class ExcelReader:
    SUPPORTED_EXTENSIONS = ['.xlsx', '.xls', '.xlsm', '.csv', '.tsv', '.ods']

    @staticmethod
    def read_excel(file_path: str, sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        try:
            ext = Path(file_path).suffix.lower()
            if ext == '.csv':
                # Try common encodings
                for enc in ['utf-8-sig', 'utf-8', 'cp1252', 'latin1']:
                    try:
                        df = pd.read_csv(file_path, encoding=enc, dtype=str, keep_default_na=False)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
            elif ext == '.tsv':
                df = pd.read_csv(file_path, sep='\t', dtype=str, keep_default_na=False)
            elif ext == '.ods':
                try:
                    import odfpy  # noqa
                    df = pd.read_excel(file_path, engine='odf', sheet_name=sheet_name, dtype=str, keep_default_na=False)
                except:
                    df = pd.read_excel(file_path, engine='openpyxl', sheet_name=sheet_name, dtype=str, keep_default_na=False)
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str, keep_default_na=False)
            df = df.fillna('')
            return df
        except Exception as e:
            logger.error(f"Excel read failed: {e}")
            return None

    @staticmethod
    def get_sheet_names(file_path: str) -> List[str]:
        try:
            sheets = pd.read_excel(file_path, sheet_name=None, nrows=0)
            return list(sheets.keys())
        except:
            return []

    @staticmethod
    def _clean_header(header: str) -> str:
        if not isinstance(header, str):
            return ''
        header = header.strip()
        header = re.sub(r'^[\*\s\.\-_\(\)\[\]\{\}/\\]+', '', header)
        header = re.sub(r'[\*\s\.\-_\(\)\[\]\{\}/\\]+$', '', header)
        header = re.sub(r'[^A-Za-z0-9]', '', header)
        return header.upper()

    @staticmethod
    def _normalize_header(header: str) -> str:
        return ExcelReader._clean_header(header)

    @staticmethod
    def detect_columns(df: pd.DataFrame) -> Dict[str, str]:
        cleaned = {col: ExcelReader._normalize_header(str(col)) for col in df.columns}
        sku_keywords = [
            'SKU', 'SKUCODE', 'PRODUCTSKU', 'MERCHANTSKU', 'SELLERSKU',
            'ITEMCODE', 'PRODUCTCODE', 'CODE', 'MODEL', 'REFERENCE',
            'PRODUCTREFERENCE', 'STOCKCODE', 'VENDORSKU', 'MASTERSKU', 'ITEMSKU'
        ]
        barcode_keywords = [
            'BARCODE', 'EAN', 'EAN13', 'UPC', 'GTIN', 'PRODUCTBARCODE',
            'BARCODENUMBER', 'BARCODENO', 'BARCODEID'
        ]
        name_keywords = [
            'PRODUCTNAME', 'NAME', 'TITLE', 'NAMEENGLISH', 'PRODUCTTITLE',
            'DESCRIPTION', 'ITEMNAME', 'PRODUCT'
        ]
        sku_col = None
        barcode_col = None
        name_col = None
        for col, norm in cleaned.items():
            if not sku_col and norm in sku_keywords:
                sku_col = col
            if not barcode_col and norm in barcode_keywords:
                barcode_col = col
            if not name_col and norm in name_keywords:
                name_col = col
        if not sku_col:
            for col, norm in cleaned.items():
                if any(kw in norm for kw in sku_keywords):
                    sku_col = col
                    break
        if not barcode_col:
            for col, norm in cleaned.items():
                if any(kw in norm for kw in barcode_keywords):
                    barcode_col = col
                    break
        if not name_col:
            for col, norm in cleaned.items():
                if any(kw in norm for kw in name_keywords):
                    name_col = col
                    break
        # Heuristics
        if not sku_col:
            for col in df.columns:
                sample = df[col].astype(str).head(50).tolist()
                if not sample:
                    continue
                letter_count = sum(1 for v in sample if re.search(r'[A-Za-z]', v))
                if letter_count / len(sample) >= 0.7:
                    sku_col = col
                    break
        if not barcode_col:
            for col in df.columns:
                if col == sku_col:
                    continue
                sample = df[col].astype(str).head(50).tolist()
                if not sample:
                    continue
                digit_count = sum(1 for v in sample if re.match(r'^\d+$', v))
                if digit_count / len(sample) >= 0.8:
                    barcode_col = col
                    break
        return {
            'sku': sku_col,
            'barcode': barcode_col,
            'name': name_col,
            'cleaned_headers': cleaned
        }

    @staticmethod
    def validate_sku_column(df: pd.DataFrame, sku_col: str) -> bool:
        if sku_col not in df.columns:
            return False
        sample = df[sku_col].astype(str).dropna().head(50).tolist()
        if not sample:
            return False
        has_letter = sum(1 for v in sample if re.search(r'[A-Za-z]', v))
        is_numeric = sum(1 for v in sample if re.match(r'^\d+$', v))
        if len(sample) == 0:
            return False
        if is_numeric / len(sample) > 0.9:
            return False
        if has_letter / len(sample) < 0.7:
            return False
        return True

    @staticmethod
    def validate_barcode_column(df: pd.DataFrame, barcode_col: str) -> bool:
        if barcode_col not in df.columns:
            return False
        sample = df[barcode_col].astype(str).dropna().head(50).tolist()
        if not sample:
            return False
        digit_count = sum(1 for v in sample if re.match(r'^\d+$', v))
        if len(sample) == 0:
            return False
        return digit_count / len(sample) >= 0.8

    @staticmethod
    def apply_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> Tuple[pd.DataFrame, Dict[str, str]]:
        new_df = df.copy()
        used = {}
        for target, source in mapping.items():
            if source in df.columns:
                used[target] = source
                new_df.rename(columns={source: target}, inplace=True)
        return new_df, used
