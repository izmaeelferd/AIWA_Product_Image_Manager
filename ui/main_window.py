from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QFileDialog, QMessageBox,
                               QTabWidget, QTableWidget, QTableWidgetItem,
                               QHeaderView, QProgressBar, QLabel, QTextEdit,
                               QSplitter, QMenuBar, QMenu, QLineEdit,
                               QComboBox, QGroupBox, QFormLayout, QCheckBox,
                               QApplication)
from PySide6.QtGui import QAction, QIcon, QFont, QColor, QPalette
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer, QSettings

from core.app import AppController
from core.config_manager import ConfigManager
from ui.excel_import_widget import ExcelImportWidget
from ui.rename_preview_widget import RenamePreviewWidget
from ui.settings_dialog import SettingsDialog
from ui.search_widget import SearchWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = AppController()
        self.controller.log_message.connect(self.append_log)
        self.controller.progress_update.connect(self.update_progress)
        self.controller.progress_max.connect(self.set_progress_max)
        self.controller.preview_ready.connect(self.on_preview_ready)
        self.controller.rename_complete.connect(self.on_rename_complete)

        self.config = ConfigManager()
        self.setWindowTitle("AIWA Product Image Manager Pro")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        settings_menu = menubar.addMenu("&Settings")
        settings_action = QAction("Preferences", self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)

        help_menu = menubar.addMenu("&Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: tabs for Excel import, preview, search
        tab_widget = QTabWidget()
        self.excel_widget = ExcelImportWidget(self.controller)
        self.preview_widget = RenamePreviewWidget(self.controller)
        self.search_widget = SearchWidget(self.controller)

        tab_widget.addTab(self.excel_widget, "Excel Import")
        tab_widget.addTab(self.preview_widget, "Rename Preview")
        tab_widget.addTab(self.search_widget, "Search")

        # Right panel: log and progress
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Progress
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(QLabel("Progress:"))
        progress_layout.addWidget(self.progress_bar)
        right_layout.addLayout(progress_layout)

        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        right_layout.addWidget(QLabel("Log:"))
        right_layout.addWidget(self.log_text)

        # Status
        self.status_label = QLabel("Ready")
        right_layout.addWidget(self.status_label)

        splitter.addWidget(tab_widget)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 400])

        layout.addWidget(splitter)

        # Bottom actions
        bottom_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Clear All")
        self.btn_clear.clicked.connect(self.clear_all)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_clear)
        layout.addLayout(bottom_layout)

    def apply_theme(self):
        theme = self.config.get("theme", "dark")
        if theme == "dark":
            dark_style = """
            QMainWindow { background-color: #2b2b2b; }
            QWidget { background-color: #2b2b2b; color: #ffffff; }
            QPushButton { background-color: #3c3c3c; border: 1px solid #555; padding: 5px; }
            QPushButton:hover { background-color: #4a4a4a; }
            QLineEdit, QTextEdit, QComboBox { background-color: #3c3c3c; border: 1px solid #555; }
            QTableWidget { background-color: #3c3c3c; alternate-background-color: #4a4a4a; }
            QHeaderView::section { background-color: #3c3c3c; color: #ffffff; }
            QTabWidget::pane { background-color: #2b2b2b; border: 1px solid #555; }
            QTabBar::tab { background-color: #3c3c3c; color: #ffffff; }
            QTabBar::tab:selected { background-color: #4a4a4a; }
            QMenuBar { background-color: #2b2b2b; color: #ffffff; }
            QMenuBar::item:selected { background-color: #3c3c3c; }
            QMenu { background-color: #2b2b2b; color: #ffffff; }
            QMenu::item:selected { background-color: #3c3c3c; }
            QProgressBar { background-color: #3c3c3c; border: 1px solid #555; }
            QProgressBar::chunk { background-color: #4a7a9c; }
            """
            self.setStyleSheet(dark_style)
        else:
            self.setStyleSheet("")

    def append_log(self, msg):
        self.log_text.append(msg)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def set_progress_max(self, max_val):
        self.progress_bar.setMaximum(max_val)

    def on_preview_ready(self, data):
        self.preview_widget.set_preview_data(data)
        self.status_label.setText(f"Preview ready: {data['total']} images, {data['matched']} matched")

    def on_rename_complete(self, data):
        self.status_label.setText(f"Rename complete: {data['success']} of {data['total']} succeeded")
        QMessageBox.information(self, "Complete", f"Renamed {data['success']} images.")

    def open_settings(self):
        dialog = SettingsDialog(self.config, self.controller.mapping_storage)
        dialog.exec()
        self.apply_theme()

    def show_about(self):
        QMessageBox.about(self, "About", "AIWA Product Image Manager Pro\nVersion 2.0\nPySide6 based")

    def clear_all(self):
        self.controller.excel_df = None
        self.controller.sku_barcode_map = {}
        self.controller.images = []
        self.controller.rename_mapping = {}
        self.controller.results = []
        self.preview_widget.clear()
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Cleared")
