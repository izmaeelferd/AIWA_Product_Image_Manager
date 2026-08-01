from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QComboBox, QTabWidget, QWidget,
                               QFormLayout, QLineEdit, QMessageBox, QTableWidget,
                               QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, config_manager, mapping_storage):
        super().__init__()
        self.config = config_manager
        self.mapping_storage = mapping_storage
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # Theme tab
        theme_tab = QWidget()
        theme_layout = QFormLayout(theme_tab)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.config.get("theme", "dark"))
        theme_layout.addRow("Theme:", self.theme_combo)
        tabs.addTab(theme_tab, "Theme")

        # Supplier mappings tab
        map_tab = QWidget()
        map_layout = QVBoxLayout(map_tab)
        self.map_table = QTableWidget()
        self.map_table.setColumnCount(2)
        self.map_table.setHorizontalHeaderLabels(["Supplier", "Mapping"])
        self.map_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        map_layout.addWidget(self.map_table)
        self.load_mappings()
        tabs.addTab(map_tab, "Supplier Mappings")

        layout.addWidget(tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save_settings)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def load_mappings(self):
        suppliers = self.mapping_storage.get_all_suppliers()
        self.map_table.setRowCount(len(suppliers))
        for i, supplier in enumerate(suppliers):
            mapping = self.mapping_storage.get_mapping(supplier)
            self.map_table.setItem(i, 0, QTableWidgetItem(supplier))
            self.map_table.setItem(i, 1, QTableWidgetItem(str(mapping)))

    def save_settings(self):
        self.config.set("theme", self.theme_combo.currentText())
        self.accept()
