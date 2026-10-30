import re
import threading
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from app.core.config import settings
from app.core.base62 import encode_base62
from app.core.cache import URLCache
from app.core.exceptions import InvalidURLException, AliasConflictException, URLNotFoundException
from app.db.repositories import URLRepository

class URLShortenerService:
    """
    Business Logic Layer:
    Handles validation, deduplication, key generation, and caching.
    """
    def __init__(self, repo: URLRepository, cache: URLCache):
        self.repo = repo
        self.cache = cache

    def validate_target_url(self, url: str) -> str:
        url = url.strip()
        parsed = urlparse(url)
        if not (parsed.scheme in ("http", "https") and parsed.netloc):
            raise InvalidURLException("Invalid URL. Must include scheme (http:// or https://) and domain.")
        return url

    def shorten_url(self, raw_url: str, custom_alias: Optional[str] = None) -> Dict[str, Any]:
        original_url = self.validate_target_url(raw_url)

        # 1. Custom Alias Flow
        if custom_alias:
            alias = custom_alias.strip()
            if not re.match(r"^[a-zA-Z0-9_-]{3,30}$", alias):
                raise InvalidURLException("Alias must be 3-30 characters with alphanumeric, hyphens, or underscores.")

            existing = self.repo.find_by_key(alias)
            if existing:
                raise AliasConflictException(alias)

            created = self.repo.create_with_alias(original_url, alias)
            self.cache.set(alias, original_url)
            return {
                "short_key": alias,
                "original_url": original_url,
                "created_at": created["created_at"]
            }

        # 2. Idempotency / Deduplication Check
        existing = self.repo.find_by_original_url(original_url)
        if existing:
            key = existing["custom_key"]
            self.cache.set(key, original_url)
            return {
                "short_key": key,
                "original_url": original_url,
                "created_at": existing["created_at"]
            }

        # 3. Automatic Base62 Short Key Generation
        url_id = self.repo.create_with_autoincrement(original_url)
        generated_key = encode_base62(url_id + settings.KEY_ID_OFFSET)
        self.repo.update_key(url_id, generated_key)

        self.cache.set(generated_key, original_url)
        return {
            "short_key": generated_key,
            "original_url": original_url,
            "created_at": existing["created_at"] if existing else 0.0
        }

    def resolve_url(self, key: str, referrer: Optional[str] = None, user_agent: Optional[str] = None) -> str:
        # Cache Hit Check
        cached_url = self.cache.get(key)
        if cached_url:
            threading.Thread(
                target=self._async_log_click_by_key,
                args=(key, referrer, user_agent),
                daemon=True
            ).start()
            return cached_url

        # Cache Miss: Query Database
        record = self.repo.find_by_key(key)
        if not record:
            raise URLNotFoundException(key)

        original_url = record["original_url"]
        self.cache.set(key, original_url)

        threading.Thread(
            target=self.repo.record_click,
            args=(record["id"], referrer, user_agent),
            daemon=True
        ).start()

        return original_url

    def get_stats(self, key: str) -> Dict[str, Any]:
        record = self.repo.find_by_key(key)
        if not record:
            raise URLNotFoundException(key)

        recent_clicks = self.repo.get_recent_clicks(record["id"], limit=10)
        return {
            "short_key": record["custom_key"],
            "original_url": record["original_url"],
            "created_at": record["created_at"],
            "total_clicks": record["click_count"],
            "recent_events": recent_clicks
        }

    def _async_log_click_by_key(self, key: str, referrer: Optional[str], user_agent: Optional[str]):
        record = self.repo.find_by_key(key)
        if record:
            self.repo.record_click(record["id"], referrer, user_agent)
