from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLineEdit, QLabel, QTableWidget, QTableWidgetItem,
                               QHeaderView, QComboBox)
from PySide6.QtCore import Qt

class SearchWidget(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search)
        search_layout.addWidget(self.search_input)
        self.search_type = QComboBox()
        self.search_type.addItems(["SKU", "Barcode", "Product Name"])
        search_layout.addWidget(self.search_type)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["SKU", "Barcode", "Product Name", "Image"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def search(self):
        # Simple search implementation (placeholder)
        query = self.search_input.text().strip()
        if not query:
            self.table.setRowCount(0)
            return
        # For demo, we show mock data if no real data
        # In full implementation, we would search the loaded data
        # Since we don't have a direct data model, we'll show placeholder
        self.table.setRowCount(1)
        self.table.setItem(0, 0, QTableWidgetItem("Sample SKU"))
        self.table.setItem(0, 1, QTableWidgetItem("Sample Barcode"))
        self.table.setItem(0, 2, QTableWidgetItem("Sample Product"))
        self.table.setItem(0, 3, QTableWidgetItem("sample.jpg"))
