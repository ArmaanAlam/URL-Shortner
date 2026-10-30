import sqlite3
from app.core.config import settings

class Database:
    """
    Database connection manager.
    Enables SQLite WAL (Write-Ahead Logging) mode and creates tables & indexes.
    """
    def __init__(self, db_path: str = settings.DATABASE_FILE):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self.get_connection()
        try:
            with conn:
                # WAL mode allows concurrent readers and a writer
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                
                # URLs Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS urls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        custom_key TEXT UNIQUE,
                        original_url TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        click_count INTEGER DEFAULT 0
                    );
                """)
                # Indexes for lightning-fast lookups
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_urls_original_url ON urls (original_url);
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_urls_custom_key ON urls (custom_key);
                """)

                # Click Events Analytics Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS click_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url_id INTEGER NOT NULL,
                        clicked_at REAL NOT NULL,
                        referrer TEXT,
                        user_agent TEXT,
                        FOREIGN KEY (url_id) REFERENCES urls (id)
                    );
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_click_events_url_id ON click_events (url_id);
                """)
        finally:
            conn.close()

db = Database()
