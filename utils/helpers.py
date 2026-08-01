import os
import re
import hashlib
from datetime import datetime

def generate_id():
    return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def format_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
