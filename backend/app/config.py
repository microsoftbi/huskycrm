from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "Husky CRM"
    debug: bool = True

    # Database
    database_url: str = f"sqlite+aiosqlite:///{Path(__file__).parent.parent / 'huskycrm.db'}"

    # JWT
    secret_key: str = "change-me-to-a-random-secret-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
