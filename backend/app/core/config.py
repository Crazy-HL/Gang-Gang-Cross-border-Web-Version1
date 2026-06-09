from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default_factory=lambda: f"sqlite:///{Path(__file__).resolve().parents[2] / 'ganggang.db'}")
    secret_key: str = 'change-me-in-production'
    access_token_ttl_seconds: int = 24 * 60 * 60
    verification_code_ttl_seconds: int = 5 * 60
    sms_enabled: bool = False
    sms_sign_name: str = '阿里云短信测试'
    sms_template_code: str = 'SMS_154950909'
    sms_endpoint: str = 'dysmsapi.aliyuncs.com'
    alibaba_cloud_access_key_id: str = Field(default='', validation_alias='ALIBABA_CLOUD_ACCESS_KEY_ID')
    alibaba_cloud_access_key_secret: str = Field(default='', validation_alias='ALIBABA_CLOUD_ACCESS_KEY_SECRET')

    model_config = SettingsConfigDict(env_prefix='GANGGANG_', env_file='.env', extra='ignore')


@lru_cache
def get_settings() -> Settings:
    return Settings()
