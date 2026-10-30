import time
from typing import Optional, List, Dict, Any
from app.db.session import Database

class URLRepository:
    """
    Data Access Object (DAO) / Repository Pattern:
    Encapsulates all raw SQL queries and DB operations.
    """
    def __init__(self, db: Database):
        self.db = db

    def find_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        conn = self.db.get_connection()
        try:
            row = conn.execute(
                "SELECT id, custom_key, original_url, created_at, click_count FROM urls WHERE custom_key = ?",
                (key,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def find_by_original_url(self, original_url: str) -> Optional[Dict[str, Any]]:
        conn = self.db.get_connection()
        try:
            row = conn.execute(
                "SELECT id, custom_key, original_url, created_at, click_count FROM urls WHERE original_url = ? AND custom_key IS NOT NULL",
                (original_url,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def create_with_alias(self, original_url: str, alias: str) -> Dict[str, Any]:
        conn = self.db.get_connection()
        now = time.time()
        try:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO urls (custom_key, original_url, created_at, click_count) VALUES (?, ?, ?, 0)",
                    (alias, original_url, now)
                )
                return {
                    "id": cursor.lastrowid,
                    "custom_key": alias,
                    "original_url": original_url,
                    "created_at": now,
                    "click_count": 0
                }
        finally:
            conn.close()

    def create_with_autoincrement(self, original_url: str) -> int:
        conn = self.db.get_connection()
        now = time.time()
        try:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO urls (original_url, created_at, click_count) VALUES (?, ?, 0)",
                    (original_url, now)
                )
                return cursor.lastrowid
        finally:
            conn.close()

    def update_key(self, url_id: int, key: str) -> None:
        conn = self.db.get_connection()
        try:
            with conn:
                conn.execute("UPDATE urls SET custom_key = ? WHERE id = ?", (key, url_id))
        finally:
            conn.close()

    def record_click(self, url_id: int, referrer: Optional[str], user_agent: Optional[str]) -> None:
        conn = self.db.get_connection()
        now = time.time()
        try:
            with conn:
                conn.execute("UPDATE urls SET click_count = click_count + 1 WHERE id = ?", (url_id,))
                conn.execute(
                    "INSERT INTO click_events (url_id, clicked_at, referrer, user_agent) VALUES (?, ?, ?, ?)",
                    (url_id, now, referrer or "", user_agent or "")
                )
        except Exception:
            pass
        finally:
            conn.close()

    def get_recent_clicks(self, url_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        conn = self.db.get_connection()
        try:
            rows = conn.execute(
                "SELECT clicked_at, referrer, user_agent FROM click_events WHERE url_id = ? ORDER BY clicked_at DESC LIMIT ?",
                (url_id, limit)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
