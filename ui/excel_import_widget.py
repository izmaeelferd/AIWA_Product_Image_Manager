from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QFileDialog, QMessageBox, QLabel, QComboBox,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QGroupBox, QFormLayout, QLineEdit, QCheckBox)
from PySide6.QtCore import Qt
import os

class ExcelImportWidget(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.excel_file_path = None
        self.sheet_names = []

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # File selection
        file_layout = QHBoxLayout()
        self.btn_browse = QPushButton("Browse Excel")
        self.btn_browse.clicked.connect(self.browse_excel)
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.btn_browse)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        layout.addLayout(file_layout)

        # Sheet selection
        sheet_layout = QHBoxLayout()
        sheet_layout.addWidget(QLabel("Sheet:"))
        self.sheet_combo = QComboBox()
        self.sheet_combo.currentIndexChanged.connect(self.on_sheet_changed)
        sheet_layout.addWidget(self.sheet_combo)
        sheet_layout.addStretch()
        layout.addLayout(sheet_layout)

        # Column detection output
        self.detection_label = QLabel("")
        layout.addWidget(self.detection_label)

        # Preview table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(QLabel("Preview (first 20 rows):"))
        layout.addWidget(self.table)

        # Supplier mapping (manual mapping)
        mapping_group = QGroupBox("Manual Column Mapping")
        mapping_layout = QFormLayout()
        self.sku_combo = QComboBox()
        self.barcode_combo = QComboBox()
        self.name_combo = QComboBox()
        mapping_layout.addRow("SKU Column:", self.sku_combo)
        mapping_layout.addRow("Barcode Column:", self.barcode_combo)
        mapping_layout.addRow("Product Name:", self.name_combo)
        self.btn_apply_mapping = QPushButton("Apply Mapping")
        self.btn_apply_mapping.clicked.connect(self.apply_manual_mapping)
        mapping_layout.addRow(self.btn_apply_mapping)
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)

        # Load button
        self.btn_load = QPushButton("Load Excel")
        self.btn_load.clicked.connect(self.load_excel)
        layout.addWidget(self.btn_load)

    def browse_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel File", "",
            "Excel Files (*.xlsx *.xls *.xlsm *.csv *.tsv *.ods);;All Files (*)"
        )
        if file_path:
            self.excel_file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            # Get sheet names using controller's ExcelReader (if available)
            if hasattr(self.controller, 'excel_reader'):
                self.sheet_names = self.controller.excel_reader.get_sheet_names(file_path)
            else:
                # fallback: try to get sheet names using pandas
                try:
                    import pandas as pd
                    sheets = pd.read_excel(file_path, sheet_name=None, nrows=0)
                    self.sheet_names = list(sheets.keys())
                except:
                    self.sheet_names = []
            self.sheet_combo.clear()
            if self.sheet_names:
                self.sheet_combo.addItems(self.sheet_names)
            else:
                self.sheet_combo.addItem("Default")
            # Load initial preview (first sheet)
            self.load_excel()

    def on_sheet_changed(self):
        self.load_excel()

    def load_excel(self):
        if not self.excel_file_path:
            return
        sheet = self.sheet_combo.currentText() if self.sheet_combo.count() > 0 else None
        if sheet == "Default":
            sheet = None
        # Use controller to load
        result = self.controller.load_excel(self.excel_file_path, sheet)
        if result is None:
            QMessageBox.warning(self, "Error", "Failed to load Excel.")
            return
        if isinstance(result, dict) and result.get('error') == 'column_detection_failed':
            self.detection_label.setText("Column detection failed. Please map columns manually.")
            columns = result.get('columns', [])
            self.sku_combo.clear()
            self.barcode_combo.clear()
            self.name_combo.clear()
            self.sku_combo.addItems(columns)
            self.barcode_combo.addItems(columns)
            self.name_combo.addItems(columns)
            self.sku_combo.addItem("")
            self.barcode_combo.addItem("")
            self.name_combo.addItem("")
            QMessageBox.information(self, "Manual Mapping", "Please select SKU and Barcode columns from the dropdowns and click Apply Mapping.")
            return
        elif isinstance(result, dict):
            df = result.get('df')
            sku_col = result.get('sku_col')
            barcode_col = result.get('barcode_col')
            self.detection_label.setText(f"Detected: SKU='{sku_col}', Barcode='{barcode_col}', Pairs={result.get('mapping_size', 0)}")
            if df is not None:
                preview_df = df.head(20)
                self.table.setRowCount(preview_df.shape[0])
                self.table.setColumnCount(preview_df.shape[1])
                self.table.setHorizontalHeaderLabels(preview_df.columns)
                for i, row in preview_df.iterrows():
                    for j, val in enumerate(row):
                        self.table.setItem(i, j, QTableWidgetItem(str(val)))
                self.sku_combo.clear()
                self.barcode_combo.clear()
                self.name_combo.clear()
                self.sku_combo.addItems(list(df.columns))
                self.barcode_combo.addItems(list(df.columns))
                self.name_combo.addItems(list(df.columns))
                if sku_col:
                    self.sku_combo.setCurrentText(sku_col)
                if barcode_col:
                    self.barcode_combo.setCurrentText(barcode_col)

    def apply_manual_mapping(self):
        sku_col = self.sku_combo.currentText()
        barcode_col = self.barcode_combo.currentText()
        if not sku_col or not barcode_col:
            QMessageBox.warning(self, "Error", "Please select both SKU and Barcode columns.")
            return
        mapping = {'sku': sku_col, 'barcode': barcode_col}
        result = self.controller.load_excel(self.excel_file_path, self.sheet_combo.currentText(), mapping)
        if result and isinstance(result, dict):
            self.detection_label.setText(f"Manual mapping applied: SKU='{sku_col}', Barcode='{barcode_col}', Pairs={result.get('mapping_size', 0)}")
            self.load_excel()
