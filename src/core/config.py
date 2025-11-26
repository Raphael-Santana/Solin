from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Solin"
    debug: bool = False
    
    # Database Configuration
    database_url: str = "sqlite:///./solin.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenLibrary API
    openlibrary_base_url: str = "https://openlibrary.org"
    openlibrary_covers_url: str = "https://covers.openlibrary.org/b"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()