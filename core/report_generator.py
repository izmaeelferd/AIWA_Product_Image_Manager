import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ReportGenerator:
    @staticmethod
    def generate_report(data: List[Dict], output_folder: str, base_name: str = "Rename_Report") -> bool:
        """
        Generate Excel, CSV, TXT reports.
        data: list of dicts with keys: old_name, sku, barcode, new_name, status
        """
        try:
            output_path = Path(output_folder)
            output_path.mkdir(parents=True, exist_ok=True)
            df = pd.DataFrame(data)
            # Excel
            excel_path = output_path / f"{base_name}.xlsx"
            df.to_excel(excel_path, index=False)
            # CSV
            csv_path = output_path / f"{base_name}.csv"
            df.to_csv(csv_path, index=False)
            # TXT
            txt_path = output_path / f"{base_name}.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("RENAME REPORT\n")
                f.write("="*50 + "\n")
                for row in data:
                    f.write(f"Old: {row.get('old_name')}\n")
                    f.write(f"SKU: {row.get('sku')}\n")
                    f.write(f"Barcode: {row.get('barcode')}\n")
                    f.write(f"New: {row.get('new_name')}\n")
                    f.write(f"Status: {row.get('status')}\n")
                    f.write("-"*30 + "\n")
            return True
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return False

    @staticmethod
    def generate_error_report(errors: List[Dict], output_folder: str) -> bool:
        try:
            output_path = Path(output_folder)
            output_path.mkdir(parents=True, exist_ok=True)
            df = pd.DataFrame(errors)
            excel_path = output_path / "Errors.xlsx"
            df.to_excel(excel_path, index=False)
            return True
        except:
            return False
