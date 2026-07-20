from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "Husky CRM"
    debug: bool = False

    # Database
    database_url: str = f"sqlite+aiosqlite:///{Path(__file__).parent.parent / 'huskycrm.db'}"

    # JWT
    secret_key: str = "change-me-to-a-random-secret-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "cors_origins":
                return [x.strip() for x in raw_val.split(",")]
            return raw_val


settings = Settings()

# In production, require a non-default secret key
if settings.debug is False and settings.secret_key == "change-me-to-a-random-secret-in-production":
    import warnings
    warnings.warn(
        "SECURITY: JWT secret_key is still the default value! "
        "Set SECRET_KEY in your .env file for production.",
        RuntimeWarning,
    )
