import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import shutil
from pathlib import Path
import pandas as pd
import time

from core.config_manager import ConfigManager
from core.database import Database
from core.file_handler import FileHandler
from core.excel_reader import ExcelReader
from core.sku_detector import SKUDetector
from core.renamer import Renamer
from core.report_generator import ReportGenerator

class MainWindow(ctk.CTkFrame):
    def __init__(self, master, config: ConfigManager, db: Database):
        super().__init__(master)
        self.master = master
        self.config = config
        self.db = db

        # State variables
        self.excel_path = None
        self.zip_path = None
        self.output_folder = None
        self.df = None
        self.sku_barcode_map = {}
        self.images = []
        self.rename_mapping = {}
        self.results = []
        self.is_running = False

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top frame: controls
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.controls_frame.grid_columnconfigure(0, weight=0)
        self.controls_frame.grid_columnconfigure(1, weight=0)
        self.controls_frame.grid_columnconfigure(2, weight=0)
        self.controls_frame.grid_columnconfigure(3, weight=0)
        self.controls_frame.grid_columnconfigure(4, weight=0)
        self.controls_frame.grid_columnconfigure(5, weight=0)
        self.controls_frame.grid_columnconfigure(6, weight=1)

        # Buttons
        self.btn_excel = ctk.CTkButton(self.controls_frame, text="Browse Excel", command=self.browse_excel)
        self.btn_excel.grid(row=0, column=0, padx=5, pady=5)

        self.btn_zip = ctk.CTkButton(self.controls_frame, text="Browse ZIP", command=self.browse_zip)
        self.btn_zip.grid(row=0, column=1, padx=5, pady=5)

        self.btn_output = ctk.CTkButton(self.controls_frame, text="Output Folder", command=self.browse_output)
        self.btn_output.grid(row=0, column=2, padx=5, pady=5)

        self.btn_preview = ctk.CTkButton(self.controls_frame, text="Preview", command=self.preview)
        self.btn_preview.grid(row=0, column=3, padx=5, pady=5)

        self.btn_start = ctk.CTkButton(self.controls_frame, text="Start Rename", command=self.start_rename)
        self.btn_start.grid(row=0, column=4, padx=5, pady=5)

        self.btn_export = ctk.CTkButton(self.controls_frame, text="Export ZIP", command=self.export_zip)
        self.btn_export.grid(row=0, column=5, padx=5, pady=5)

        self.btn_clear = ctk.CTkButton(self.controls_frame, text="Clear", command=self.clear_all)
        self.btn_clear.grid(row=0, column=6, padx=5, pady=5, sticky="e")

        # Status bar
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready", font=("Arial", 12))
        self.status_label.pack(side="left", padx=10)
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=400)
        self.progress_bar.pack(side="right", padx=10)
        self.progress_bar.set(0)

        # Main content: table and log
        self.main_panel = ctk.CTkFrame(self)
        self.main_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.main_panel.grid_rowconfigure(0, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)

        self.table_frame = ctk.CTkFrame(self.main_panel)
        self.table_frame.grid(row=0, column=0, sticky="nsew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        from tkinter import ttk
        self.tree = ttk.Treeview(self.table_frame, columns=("Old", "SKU", "Barcode", "New", "Status"), show="headings")
        self.tree.heading("Old", text="Old Name")
        self.tree.heading("SKU", text="Detected SKU")
        self.tree.heading("Barcode", text="Barcode")
        self.tree.heading("New", text="New Name")
        self.tree.heading("Status", text="Status")
        self.tree.column("Old", width=200)
        self.tree.column("SKU", width=100)
        self.tree.column("Barcode", width=120)
        self.tree.column("New", width=200)
        self.tree.column("Status", width=80)
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.log_frame = ctk.CTkFrame(self.main_panel)
        self.log_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        self.log_frame.grid_rowconfigure(0, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_text = ctk.CTkTextbox(self.log_frame, wrap="word", height=100)
        self.log_text.grid(row=0, column=0, sticky="nsew")

    def browse_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if file_path:
            self.excel_path = file_path
            self.log(f"Excel selected: {file_path}")
            self.status_label.configure(text=f"Excel: {os.path.basename(file_path)}")
            self.df = ExcelReader.read_excel(file_path)
            if self.df is not None:
                # Detect columns
                cols = ExcelReader.detect_columns(self.df)
                sku_col = cols.get('sku')
                barcode_col = cols.get('barcode')
                # Log detected columns with cleaned headers
                cleaned = cols.get('cleaned_headers', {})
                for col, clean in cleaned.items():
                    self.log(f"Original Header: '{col}' -> Normalized: '{clean}'")
                self.log(f"Detected SKU Column: '{sku_col}'")
                self.log(f"Detected Barcode Column: '{barcode_col}'")

                if sku_col and barcode_col:
                    # Validate SKU column
                    is_valid_sku = ExcelReader.validate_sku_column(self.df, sku_col)
                    if not is_valid_sku:
                        self.log("WARNING: SKU column validation failed - column may be numeric or contains no letters.")
                        # Try to find another column
                        for col in self.df.columns:
                            if col != sku_col and col != barcode_col:
                                if ExcelReader.validate_sku_column(self.df, col):
                                    sku_col = col
                                    self.log(f"Found alternative SKU column: '{sku_col}'")
                                    break
                    # Build mapping
                    self.sku_barcode_map = {}
                    row_count = 0
                    for idx, row in self.df.iterrows():
                        raw_sku = str(row[sku_col]).strip()
                        if raw_sku and raw_sku != 'nan':
                            norm_sku = SKUDetector.normalize_sku(raw_sku)
                            barcode = str(row[barcode_col]).strip()
                            if barcode and barcode != 'nan':
                                self.sku_barcode_map[norm_sku] = barcode
                                row_count += 1
                                if row_count <= 20:
                                    self.log(f"Row {idx+2}: SKU '{raw_sku}' -> Normalized '{norm_sku}' -> Barcode '{barcode}'")
                    self.log(f"Loaded {len(self.sku_barcode_map)} SKU-Barcode pairs from Excel (normalized).")
                    sample_keys = list(self.sku_barcode_map.keys())[:10]
                    self.log(f"Sample normalized SKUs: {sample_keys}")
                    if len(self.sku_barcode_map) == 0:
                        self.log("ERROR: No valid SKU-Barcode pairs loaded. Check column detection.")
                else:
                    self.log("Could not detect SKU and/or Barcode columns. Please check Excel format.")
            else:
                self.log("Failed to read Excel file.")

    def browse_zip(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archive files", "*.zip *.rar *.7z")])
        if file_path:
            self.zip_path = file_path
            self.log(f"Archive selected: {file_path}")
            self.status_label.configure(text=f"ZIP: {os.path.basename(file_path)}")

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.log(f"Output folder selected: {folder}")
            self.status_label.configure(text=f"Output: {folder}")

    def log(self, message):
        self.log_text.insert("end", f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see("end")
        self.db.add_history("log", message)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear_all(self):
        self.excel_path = None
        self.zip_path = None
        self.output_folder = None
        self.df = None
        self.sku_barcode_map = {}
        self.images = []
        self.rename_mapping = {}
        self.results = []
        self.clear_table()
        self.log_text.delete("1.0", "end")
        self.status_label.configure(text="Ready")
        self.progress_bar.set(0)
        self.log("Cleared all.")

    def preview(self):
        if not self.zip_path:
            messagebox.showerror("Error", "Please select a ZIP file first.")
            return
        if not self.sku_barcode_map:
            messagebox.showerror("Error", "Please load Excel with SKU-Barcode mapping.")
            return

        temp_dir = Path("temp") / "extract"
        FileHandler.delete_directory(str(temp_dir))
        FileHandler.ensure_directory(str(temp_dir))
        self.log(f"Extracting archive: {self.zip_path}")
        success = FileHandler.extract_archive(self.zip_path, str(temp_dir))
        if not success:
            self.log("Extraction failed.")
            return
        self.images = FileHandler.list_files(str(temp_dir), ['jpg','jpeg','png','gif','bmp','webp'], recursive=True)
        if not self.images:
            self.log("No images found in archive.")
            return
        self.log(f"Found {len(self.images)} images (including subfolders).")
        # Sample SKU extraction log
        sample_skus = []
        for i, img in enumerate(self.images[:10]):
            raw_sku = SKUDetector.extract_sku(os.path.basename(img))
            norm_sku = SKUDetector.normalize_sku(raw_sku) if raw_sku else None
            sample_skus.append(f"{os.path.basename(img)} -> raw: {raw_sku}, norm: {norm_sku}")
        self.log("Sample SKU extraction:")
        for s in sample_skus:
            self.log(f"  {s}")
        # Generate rename mapping
        self.rename_mapping = Renamer.generate_rename_mapping([os.path.basename(img) for img in self.images], self.sku_barcode_map)
        self.log(f"Generated mapping for {len(self.rename_mapping)} images.")
        self.clear_table()
        for old, new in self.rename_mapping.items():
            sku = SKUDetector.extract_sku(old)
            norm_sku = SKUDetector.normalize_sku(sku) if sku else ''
            barcode = self.sku_barcode_map.get(norm_sku, '')
            self.tree.insert("", "end", values=(old, sku, barcode, new, "Pending"))
        self.status_label.configure(text=f"Preview: {len(self.rename_mapping)} images ready.")

    def start_rename(self):
        if not self.rename_mapping:
            messagebox.showerror("Error", "Please run Preview first.")
            return
        if not self.output_folder:
            messagebox.showerror("Error", "Please select output folder.")
            return

        self.is_running = True
        self.btn_start.configure(state="disabled")
        self.progress_bar.set(0)
        self.log("Starting rename...")

        def run():
            temp_dir = Path("temp") / "extract"
            output_path = Path(self.output_folder)
            output_path.mkdir(parents=True, exist_ok=True)
            total = len(self.rename_mapping)
            processed = 0
            self.results = []
            full_path_map = {}
            for img_full in self.images:
                base = os.path.basename(img_full)
                full_path_map[base] = img_full
            for old_name, new_name in self.rename_mapping.items():
                src = full_path_map.get(old_name)
                if not src:
                    status = "Error: Source missing"
                    self.log(f"Source not found for {old_name}")
                    self.results.append({
                        'old_name': old_name,
                        'sku': SKUDetector.extract_sku(old_name),
                        'barcode': self.sku_barcode_map.get(SKUDetector.normalize_sku(SKUDetector.extract_sku(old_name) or ''), ''),
                        'new_name': new_name,
                        'status': status
                    })
                    processed += 1
                    continue
                dst = output_path / new_name
                try:
                    shutil.copy2(src, dst)
                    status = "Success"
                except Exception as e:
                    status = f"Error: {e}"
                    self.log(f"Failed to copy {old_name}: {e}")
                self.results.append({
                    'old_name': old_name,
                    'sku': SKUDetector.extract_sku(old_name),
                    'barcode': self.sku_barcode_map.get(SKUDetector.normalize_sku(SKUDetector.extract_sku(old_name) or ''), ''),
                    'new_name': new_name,
                    'status': status
                })
                processed += 1
                progress = processed / total
                self.progress_bar.set(progress)
                self.master.after(0, lambda idx=processed-1, st=status: self.update_table_status(idx, st))
            self.master.after(0, self.rename_complete)

        threading.Thread(target=run, daemon=True).start()

    def update_table_status(self, idx, status):
        children = self.tree.get_children()
        if idx < len(children):
            item = children[idx]
            values = list(self.tree.item(item, 'values'))
            values[4] = status
            self.tree.item(item, values=values)

    def rename_complete(self):
        self.is_running = False
        self.btn_start.configure(state="normal")
        self.log("Rename completed.")
        self.status_label.configure(text="Rename completed.")
        if self.output_folder:
            ReportGenerator.generate_report(self.results, self.output_folder)
            errors = [r for r in self.results if r['status'] != 'Success']
            if errors:
                ReportGenerator.generate_error_report(errors, self.output_folder)
                self.log(f"Generated error report for {len(errors)} errors.")
            self.log("Reports generated.")
        self.db.add_history("rename", f"Renamed {len(self.results)} images.")

    def export_zip(self):
        if not self.output_folder:
            messagebox.showerror("Error", "No output folder to zip.")
            return
        zip_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP files", "*.zip")])
        if zip_path:
            success = FileHandler.create_zip(self.output_folder, zip_path)
            if success:
                self.log(f"ZIP exported: {zip_path}")
                messagebox.showinfo("Export", f"ZIP created at {zip_path}")
            else:
                self.log("ZIP creation failed.")
