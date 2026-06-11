from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import ModelConfig


def model_config_to_dict(config: ModelConfig):
    return {
        'id': config.id,
        'provider': config.provider,
        'modelName': config.model_name,
        'baseUrl': config.base_url,
        'temperature': config.temperature,
        'maxTokens': config.max_tokens,
        'enabled': config.enabled,
    }


def get_model_config(db: Session) -> ModelConfig | None:
    query = select(ModelConfig).order_by(ModelConfig.id.asc())
    return db.scalar(query)


def upsert_model_config(db: Session, provider: str, model_name: str, api_key: str, base_url: str, temperature: float, max_tokens: int, enabled: bool):
    config = get_model_config(db)
    if not config:
        config = ModelConfig()
        db.add(config)
    config.provider = provider
    config.model_name = model_name
    if api_key:
        config.api_key = api_key
    config.base_url = base_url
    config.temperature = temperature
    config.max_tokens = max_tokens
    config.enabled = enabled
    db.commit()
    db.refresh(config)
    return config
