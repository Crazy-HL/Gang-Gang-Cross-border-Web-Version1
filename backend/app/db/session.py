from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()
engine_options = {}
if settings.database_url.startswith('sqlite'):
    engine_options['connect_args'] = {'check_same_thread': False}
else:
    engine_options['pool_pre_ping'] = True
    engine_options['pool_recycle'] = 3600
engine = create_engine(settings.database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]
