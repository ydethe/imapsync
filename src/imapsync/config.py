from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    IMAP_SERVER: str
    IMAP_PORT: int
    USERNAME: str
    PASSWORD: str
    SAVE_DIR: Path


config = Config()
