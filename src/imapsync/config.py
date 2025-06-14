from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ImapConfiguration(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="allow",
    )

    LABEL: str
    IMAP_SERVER: str
    IMAP_PORT: int
    USERNAME: str
    PASSWORD: str
    MAILBOX: str


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        env_nested_delimiter="__",
    )

    LOGLEVEL: str
    SAVE_DIR: Path
    IMAP_LIST: List[ImapConfiguration]
    SYNC_PERIOD: int

    @field_validator("IMAP_LIST", mode="before")
    @classmethod
    def validate_endpoints(cls, configs: dict) -> List[ImapConfiguration]:
        return [ImapConfiguration(**config) for config in configs.values()]


config = Config()
