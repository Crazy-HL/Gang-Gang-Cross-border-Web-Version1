from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default_factory=lambda: f"sqlite:///{Path(__file__).resolve().parents[2] / 'ganggang.db'}")

    model_config = SettingsConfigDict(env_prefix='GANGGANG_', env_file='.env', extra='ignore')


@lru_cache
def get_settings() -> Settings:
    return Settings()
