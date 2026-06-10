from datetime import datetime, timezone

from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.session import engine


def init_database():
    Base.metadata.create_all(bind=engine)
    _ensure_user_password_hash_column()
    _ensure_job_review_columns()


def _ensure_user_password_hash_column():
    inspector = inspect(engine)
    if 'users' not in inspector.get_table_names():
        return
    columns = {column['name'] for column in inspector.get_columns('users')}
    if 'password_hash' in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''"))


def _ensure_job_review_columns():
    inspector = inspect(engine)
    if 'jobs' not in inspector.get_table_names():
        return
    columns = {column['name'] for column in inspector.get_columns('jobs')}
    with engine.begin() as connection:
        if 'review_status' not in columns:
            connection.execute(text("ALTER TABLE jobs ADD COLUMN review_status VARCHAR(32) NOT NULL DEFAULT 'none'"))
        if 'review_note' not in columns:
            connection.execute(text("ALTER TABLE jobs ADD COLUMN review_note TEXT NOT NULL"))
