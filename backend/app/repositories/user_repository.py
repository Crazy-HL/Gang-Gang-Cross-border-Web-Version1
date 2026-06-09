from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_mobile(db: Session, mobile: str) -> User | None:
    return db.scalar(select(User).where(User.mobile == mobile))


def create_user(db: Session, mobile: str, name: str | None = None, password_hash: str = '', role: str = 'user') -> User:
    user = User(mobile=mobile, name=name or f'用户{mobile[-4:]}', password_hash=password_hash, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
