import customtkinter as ctk
import threading
import os
import sys
import shutil
from pathlib import Path
from tkinter import filedialog, messagebox
import pandas as pd
import logging

from .config_manager import ConfigManager
from .database import Database
from .logger import setup_logger
from .file_handler import FileHandler
from .excel_reader import ExcelReader
from .sku_detector import SKUDetector
from .renamer import Renamer
from .report_generator import ReportGenerator
from ui.main_window import MainWindow

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AIWA Product Image Manager")
        self.geometry("1280x800")
        self.minsize(1024, 600)

        # Setup config
        self.config = ConfigManager()
        self.db = Database()

        # Setup logger
        self.logger = setup_logger("AIWA", "logs/app.log")
        self.logger.info("Application starting...")

        # Set theme
        theme = self.config.get("theme", "dark")
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")

        # Initialize main UI
        self.main_window = MainWindow(self, self.config, self.db)
        self.main_window.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.logger.info("Application closing")
        self.db.add_history("app_close", "Application closed")
        self.destroy()

    def run(self):
        self.mainloop()
