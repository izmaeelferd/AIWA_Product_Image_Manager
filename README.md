# AIWA Product Image Manager Pro

**Professional Bulk Product Image Renaming Tool for eCommerce Marketplaces**

---

## 📦 Overview

AIWA Product Image Manager Pro is a Windows desktop application that automates the tedious process of renaming product images using barcode data from Excel files. It's designed for high‑volume daily use by sellers on **Talabat, Snoonu, Shopify, Noon, Amazon**, and other platforms.

**Key workflow:**
1. Load an Excel file containing SKU and Barcode columns.
2. Select a ZIP archive (or folder) containing product images.
3. The software extracts the ZIP, scans all images, detects SKU from filenames, matches with Excel, and renames images using barcodes.
4. Outputs renamed images plus detailed reports (Excel, CSV, TXT).

---

## ✨ Features

- **Any Supplier Excel Format** – Automatically detects SKU, Barcode, and Product Name columns regardless of header variations.
- **Supports Multiple Image Formats** – JPG, JPEG, PNG, WEBP, BMP, GIF, TIFF, AVIF, HEIC.
- **Archive Support** – Extract ZIP, RAR, and 7z archives.
- **Recursive Folder Scanning** – Finds images in nested folders.
- **Intelligent SKU Extraction** – Handles filenames like `AW-393-2-PINK.webp`, `GA-506_FRONT.jpg`, `AW393 (1).png` and extracts the base SKU (`AW-393`, `GA-506`).
- **Automatic Image Ordering** – Uses suffix numbers (e.g., `-1`, `-2`) to determine main image and variants.
- **Bulk Rename** – Renames images as `Barcode.extension` for main, `Barcode_2.extension` for second, etc.
- **Reports** – Generates `Rename_Report.xlsx`, `.csv`, `.txt`, plus error reports for unmatched images.
- **Dark / Light Theme** – Choose your preferred appearance.
- **Progress & Logging** – Real-time progress bar and detailed log for every step.
- **Manual Column Mapping** – If auto‑detection fails, you can manually map columns and save supplier profiles.

---

## 📋 Requirements

- **Windows 10 / 11** (64‑bit recommended)
- **Python 3.10 or higher** (the application can be run as a script or as a standalone EXE)

---

## 🚀 Installation (for Developers)

### 1. Clone or Download the Repository
```bash
git clone https://github.com/izmaeelferd/AIWA_Product_Image_Manager.git
cd AIWA_Product_Image_Manager
python -m venv venv
pip install -r requirements.txt
python main.py
🖥️ Usage Guide
Step 1 – Load Excel File
Click Browse Excel.

Select your supplier Excel file (.xlsx, .xls, .csv, .tsv, .ods).

The software will automatically detect the sheet and columns.

If detection fails, a Manual Column Mapping section appears – select SKU and Barcode columns from dropdowns and click Apply Mapping.

Once loaded, you'll see a preview of the first 20 rows and a summary of detected pairs.

Step 2 – Select Image Archive
Click Browse ZIP/Folder.

Choose a ZIP, RAR, or 7z archive, or select a folder containing images.

The software will extract the archive (if needed) and recursively scan for images.

Step 3 – Preview
Click Preview.

A table will show the original filename, detected SKU, barcode, new filename, and status.

Check the log for details on SKU extraction and matching.

Step 4 – Choose Output Folder
Click Select Output Folder and choose where to save the renamed images.

Step 5 – Start Rename
Click Start Rename.

The software copies images to the output folder, renaming them with barcodes.

Progress is shown in the progress bar and log.

Upon completion, reports are generated automatically in the output folder.

Step 6 – Export ZIP (Optional)
After renaming, click Export ZIP to create a compressed archive of the renamed images.

📊 Reports Generated
After rename, the output folder contains:

Rename_Report.xlsx – Full list of all images with old name, SKU, barcode, new name, and status.

Rename_Report.csv – Same data in CSV format.

Rename_Report.txt – Human‑readable text report.

Errors.xlsx – List of images that failed (if any).

debug_log.txt – Detailed debug log for troubleshooting.

⚙️ Settings
Theme – Switch between Dark and Light mode from the Settings menu.

Supplier Mappings – After manually mapping columns, you can save the mapping for a supplier. Next time you load the same supplier's Excel, the mapping is applied automatically.

🧪 Troubleshooting
IssueSolution
Excel not loadingEnsure the file is not open in another program. Check that it contains at least one sheet with data.
SKU/Barcode column not detectedUse Manual Column Mapping to select the correct columns.
No images foundMake sure your ZIP file contains images (JPG, PNG, etc.) in any folder structure.
Some images unmatchedCheck the Errors.xlsx report. Common reasons: SKU not in Excel, barcode missing, or filename cannot be parsed.
Application crashesCheck logs/app.log for detailed error messages.
🔧 Building a Standalone EXE
To distribute the application without requiring Python, use PyInstaller:

bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "AIWA_Product_Image_Manager" --icon=assets/icon.ico main.py
(You can create an icon file and place it in assets/.)

The executable will be located in the dist/ folder.

🤝 Contributing
Fork the repository.

Create a feature branch (git checkout -b feature/amazing-feature).

Commit your changes (git commit -m 'Add some amazing feature').

Push to the branch (git push origin feature/amazing-feature).

Open a Pull Request.

📄 License
This project is licensed under the MIT License – see the LICENSE file for details.

📧 Contact
For questions or support, please open an issue on GitHub or contact the maintainer.

Happy renaming! 🚀
