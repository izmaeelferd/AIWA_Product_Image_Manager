import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "database/app.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(str(self.db_path))

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # History table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT,
                    details TEXT,
                    timestamp TEXT
                )
            ''')
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            conn.commit()

    def add_history(self, action: str, details: str) -> None:
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO history (action, details, timestamp) VALUES (?, ?, ?)",
                (action, details, now)
            )
            conn.commit()

    def get_history(self, limit: int = 100) -> List[Dict[str, str]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT action, details, timestamp FROM history ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
        return [{'action': r[0], 'details': r[1], 'timestamp': r[2]} for r in rows]

    def get_setting(self, key: str, default: Any = None) -> Any:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
        if not row:
            return default
        try:
            return json.loads(row[0])
        except:
            return row[0]

    def set_setting(self, key: str, value: Any) -> None:
        val = json.dumps(value) if not isinstance(value, str) else value
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, val)
            )
            conn.commit()
