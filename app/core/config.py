import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "First-Principles URL Shortener"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    BASE_URL: str = "http://localhost:8000"
    
    # Database
    DATABASE_FILE: str = "shortener.db"
    
    # Cache
    CACHE_CAPACITY: int = 1000
    
    # Base62 ID Offset (ensures initial generated keys are at least 3-4 chars)
    KEY_ID_OFFSET: int = 100000

    class Config:
        env_file = ".env"

settings = Settings()
