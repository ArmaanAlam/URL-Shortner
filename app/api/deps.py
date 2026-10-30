from app.db.session import db
from app.db.repositories import URLRepository
from app.core.cache import cache
from app.services.shortener_service import URLShortenerService

repo = URLRepository(db=db)
shortener_service = URLShortenerService(repo=repo, cache=cache)

def get_shortener_service() -> URLShortenerService:
    """Dependency injection provider for FastAPI endpoints."""
    return shortener_service
