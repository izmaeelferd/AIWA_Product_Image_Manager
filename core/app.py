import sys
import os
from pathlib import Path
import threading
import shutil
import time

from PySide6.QtCore import QObject, Signal

from .config_manager import ConfigManager
from .logger import setup_logger
from .excel_reader import ExcelReader
from .sku_detector import SKUDetector
from .renamer import Renamer
from .file_handler import FileHandler
from .report_generator import ReportGenerator
from .mapping_storage import MappingStorage

class AppController(QObject):
    log_message = Signal(str)
    progress_update = Signal(int)
    progress_max = Signal(int)
    status_update = Signal(str)
    preview_ready = Signal(dict)
    rename_complete = Signal(dict)

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.logger = setup_logger("AIWA", "logs/app.log")
        self.mapping_storage = MappingStorage()
        self.excel_reader = ExcelReader  # class reference for static methods
        self.excel_df = None
        self.sku_barcode_map = {}
        self.images = []
        self.rename_mapping = {}
        self.results = []
        self.is_running = False
        self.current_work = None

    def load_excel(self, file_path: str, sheet: str = None, mapping: dict = None):
        self.log_message.emit(f"Loading Excel: {file_path}")
        df = ExcelReader.read_excel(file_path, sheet)
        if df is None:
            self.log_message.emit("Failed to read Excel file.")
            return None
        self.excel_df = df
        if mapping and mapping.get('sku') and mapping.get('barcode'):
            sku_col = mapping['sku']
            barcode_col = mapping['barcode']
            self.log_message.emit(f"Using manual mapping: SKU={sku_col}, Barcode={barcode_col}")
        else:
            cols = ExcelReader.detect_columns(df)
            sku_col = cols.get('sku')
            barcode_col = cols.get('barcode')
            self.log_message.emit(f"Auto-detected: SKU={sku_col}, Barcode={barcode_col}")
        if not sku_col or not barcode_col:
            self.log_message.emit("Could not detect SKU/Barcode columns.")
            return {'error': 'column_detection_failed', 'columns': list(df.columns)}
        self.sku_barcode_map = {}
        for idx, row in df.iterrows():
            raw_sku = str(row[sku_col]).strip()
            if raw_sku and raw_sku != 'nan':
                norm_sku = SKUDetector.normalize_sku(raw_sku)
                barcode = str(row[barcode_col]).strip()
                if barcode and barcode != 'nan':
                    self.sku_barcode_map[norm_sku] = barcode
        self.log_message.emit(f"Loaded {len(self.sku_barcode_map)} SKU-Barcode pairs.")
        return {'df': df, 'sku_col': sku_col, 'barcode_col': barcode_col, 'mapping_size': len(self.sku_barcode_map)}

    def extract_and_preview(self, archive_path: str):
        self.log_message.emit(f"Extracting archive: {archive_path}")
        temp_dir = Path("temp") / "extract"
        FileHandler.delete_directory(str(temp_dir))
        FileHandler.ensure_directory(str(temp_dir))
        success = FileHandler.extract_archive(archive_path, str(temp_dir))
        if not success:
            self.log_message.emit("Extraction failed.")
            return
        self.images = FileHandler.list_files(str(temp_dir), ['jpg','jpeg','png','gif','bmp','webp'], recursive=True)
        self.log_message.emit(f"Found {len(self.images)} images.")
        self.rename_mapping = Renamer.generate_rename_mapping(
            [os.path.basename(img) for img in self.images],
            self.sku_barcode_map
        )
        self.log_message.emit(f"Generated mapping for {len(self.rename_mapping)} images.")
        preview_data = []
        for old, new in self.rename_mapping.items():
            sku = SKUDetector.extract_sku(old)
            norm = SKUDetector.normalize_sku(sku) if sku else ''
            barcode = self.sku_barcode_map.get(norm, '')
            preview_data.append({
                'old_name': old,
                'sku': sku,
                'barcode': barcode,
                'new_name': new,
                'status': 'Pending'
            })
        self.preview_ready.emit({'data': preview_data, 'total': len(preview_data), 'matched': len(preview_data)})

    def start_rename(self, output_folder: str):
        if not self.rename_mapping or not self.images:
            self.log_message.emit("No rename mapping or images. Run preview first.")
            return
        self.is_running = True
        self.log_message.emit("Starting rename...")
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        full_path_map = {}
        for img_full in self.images:
            base = os.path.basename(img_full)
            full_path_map[base] = img_full

        total = len(self.rename_mapping)
        self.progress_max.emit(total)
        processed = 0
        self.results = []

        for old_name, new_name in self.rename_mapping.items():
            if not self.is_running:
                break
            src = full_path_map.get(old_name)
            if not src:
                status = "Source missing"
                self.log_message.emit(f"Source not found: {old_name}")
            else:
                dst = output_path / new_name
                try:
                    shutil.copy2(src, dst)
                    status = "Success"
                except Exception as e:
                    status = f"Error: {str(e)}"
                    self.log_message.emit(f"Copy failed: {old_name} -> {e}")
            self.results.append({
                'old_name': old_name,
                'sku': SKUDetector.extract_sku(old_name),
                'barcode': self.sku_barcode_map.get(SKUDetector.normalize_sku(SKUDetector.extract_sku(old_name) or ''), ''),
                'new_name': new_name,
                'status': status
            })
            processed += 1
            self.progress_update.emit(processed)

        self.is_running = False
        if self.results:
            ReportGenerator.generate_report(self.results, output_folder)
            errors = [r for r in self.results if r['status'] != 'Success']
            if errors:
                ReportGenerator.generate_error_report(errors, output_folder)
        self.rename_complete.emit({'total': len(self.results), 'success': sum(1 for r in self.results if r['status'] == 'Success')})

    def cancel_rename(self):
        self.is_running = False
        self.log_message.emit("Rename cancelled.")
