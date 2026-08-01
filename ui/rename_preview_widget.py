from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QFileDialog, QMessageBox, QLabel, QProgressBar)
from PySide6.QtCore import Qt
import os

class RenamePreviewWidget(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.preview_data = []
        self.rename_mapping = {}

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls = QHBoxLayout()
        self.btn_browse_zip = QPushButton("Browse ZIP/Folder")
        self.btn_browse_zip.clicked.connect(self.browse_zip)
        self.btn_preview = QPushButton("Preview")
        self.btn_preview.clicked.connect(self.run_preview)
        self.btn_start = QPushButton("Start Rename")
        self.btn_start.clicked.connect(self.start_rename)
        self.btn_export = QPushButton("Export ZIP")
        self.btn_export.clicked.connect(self.export_zip)
        self.btn_output = QPushButton("Select Output Folder")
        self.btn_output.clicked.connect(self.select_output)
        controls.addWidget(self.btn_browse_zip)
        controls.addWidget(self.btn_preview)
        controls.addWidget(self.btn_start)
        controls.addWidget(self.btn_export)
        controls.addWidget(self.btn_output)
        controls.addStretch()
        layout.addLayout(controls)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Old Name", "SKU", "Barcode", "New Name", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Progress
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Store paths
        self.zip_path = None
        self.output_folder = None

    def browse_zip(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Archive or Folder", "",
            "Archives (*.zip *.rar *.7z);;All Files (*)"
        )
        if file_path:
            self.zip_path = file_path
            self.status_label.setText(f"Archive: {os.path.basename(file_path)}")

    def select_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.status_label.setText(f"Output: {folder}")

    def run_preview(self):
        if not self.zip_path:
            QMessageBox.warning(self, "Error", "Please select a ZIP file.")
            return
        if not self.controller.sku_barcode_map:
            QMessageBox.warning(self, "Error", "Please load Excel with SKU-Barcode mapping first.")
            return
        self.status_label.setText("Extracting and previewing...")
        self.controller.extract_and_preview(self.zip_path)

    def set_preview_data(self, data):
        self.preview_data = data['data']
        self.table.setRowCount(len(self.preview_data))
        for i, row in enumerate(self.preview_data):
            self.table.setItem(i, 0, QTableWidgetItem(row['old_name']))
            self.table.setItem(i, 1, QTableWidgetItem(row['sku'] or ''))
            self.table.setItem(i, 2, QTableWidgetItem(row['barcode'] or ''))
            self.table.setItem(i, 3, QTableWidgetItem(row['new_name']))
            self.table.setItem(i, 4, QTableWidgetItem(row['status']))
        self.status_label.setText(f"Preview ready: {data['total']} images, {data['matched']} matched")

    def start_rename(self):
        if not self.output_folder:
            QMessageBox.warning(self, "Error", "Please select output folder.")
            return
        if not self.preview_data:
            QMessageBox.warning(self, "Error", "Please run preview first.")
            return
        self.btn_start.setEnabled(False)
        self.controller.start_rename(self.output_folder)
        self.btn_start.setEnabled(True)

    def export_zip(self):
        if not self.output_folder:
            QMessageBox.warning(self, "Error", "No output folder selected.")
            return
        zip_path, _ = QFileDialog.getSaveFileName(self, "Save ZIP", "", "ZIP Files (*.zip)")
        if zip_path:
            from core.file_handler import FileHandler
            success = FileHandler.create_zip(self.output_folder, zip_path)
            if success:
                QMessageBox.information(self, "Success", f"ZIP created: {zip_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to create ZIP.")

    def clear(self):
        self.table.setRowCount(0)
        self.preview_data = []
        self.status_label.setText("Cleared")
