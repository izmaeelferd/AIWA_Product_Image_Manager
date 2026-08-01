import os
import shutil
import zipfile
import logging
from pathlib import Path
from typing import List, Optional
import py7zr
import rarfile

logger = logging.getLogger(__name__)

class FileHandler:
    @staticmethod
    def extract_archive(archive_path: str, extract_to: str) -> bool:
        """Extract ZIP, RAR, 7z archives."""
        try:
            extract_to = Path(extract_to)
            extract_to.mkdir(parents=True, exist_ok=True)
            ext = Path(archive_path).suffix.lower()
            if ext == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(extract_to)
            elif ext == '.rar':
                with rarfile.RarFile(archive_path) as rf:
                    rf.extractall(extract_to)
            elif ext == '.7z':
                with py7zr.SevenZipFile(archive_path, mode='r') as sz:
                    sz.extractall(extract_to)
            else:
                logger.error(f"Unsupported archive format: {ext}")
                return False
            return True
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return False

    @staticmethod
    def list_files(directory: str, extensions: List[str] = None, recursive: bool = True) -> List[str]:
        """
        List files in directory, optionally recursive.
        extensions: list of extensions without dot, e.g., ['jpg', 'png']
        """
        try:
            path = Path(directory)
            if not path.exists():
                return []
            if extensions:
                extensions = [ext.lower().strip('.') for ext in extensions]
            files = []
            if recursive:
                for root, _, filenames in os.walk(directory):
                    for f in filenames:
                        if extensions:
                            if Path(f).suffix.lower().strip('.') in extensions:
                                files.append(os.path.join(root, f))
                        else:
                            files.append(os.path.join(root, f))
            else:
                for f in path.iterdir():
                    if f.is_file():
                        if extensions:
                            if f.suffix.lower().strip('.') in extensions:
                                files.append(str(f))
                        else:
                            files.append(str(f))
            return files
        except Exception as e:
            logger.error(f"List files failed: {e}")
            return []

    @staticmethod
    def copy_file(src: str, dst: str, overwrite: bool = False) -> bool:
        try:
            dst_path = Path(dst)
            if dst_path.exists() and not overwrite:
                return False
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            logger.error(f"Copy failed: {e}")
            return False

    @staticmethod
    def move_file(src: str, dst: str, overwrite: bool = False) -> bool:
        try:
            dst_path = Path(dst)
            if dst_path.exists() and not overwrite:
                return False
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dst)
            return True
        except Exception as e:
            logger.error(f"Move failed: {e}")
            return False

    @staticmethod
    def create_zip(source_dir: str, output_zip: str) -> bool:
        try:
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zf.write(file_path, arcname)
            return True
        except Exception as e:
            logger.error(f"Zip creation failed: {e}")
            return False

    @staticmethod
    def delete_directory(path: str) -> bool:
        try:
            shutil.rmtree(path, ignore_errors=True)
            return True
        except:
            return False

    @staticmethod
    def ensure_directory(path: str) -> bool:
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except:
            return False
