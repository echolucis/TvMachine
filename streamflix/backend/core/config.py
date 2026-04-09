from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://streamflix:streamflix_password@db:5432/streamflix"
    
    # TMDB API
    tmdb_api_key: str = ""
    
    # JWT Settings
    jwt_secret_key: str = "your_super_secret_jwt_key_change_this_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Application
    app_name: str = "StreamFlix"
    app_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
