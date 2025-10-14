from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageType(str, Enum):
    """Storage types."""
    JSON = "json"
    SQL = "sql"
    IN_MEMORY = "memory"


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8") # path to .env file

    # And if .env was not there:
    STORAGE_TYPE: StorageType = StorageType.JSON # Type of Storage
    DB_PATH: Path = Path("notes.json") # Json file location

    # or SQL:
    # STORAGE_TYPE: StorageType = StorageType.SQL
    # SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"


settings = Settings() # The Only instance of settings
