from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.base import User
from app.repositories.user_repository import create_user, get_user_by_mobile
from app.repositories.verification_code_repository import create_verification_code, get_latest_valid_code, mark_code_used
from app.services.sms_service import send_verification_sms

settings = get_settings()


def _generate_code() -> str:
    return f'{random.randint(0, 999999):06d}'


def send_code(db: Session, mobile: str):
    code = _generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.verification_code_ttl_seconds)
    create_verification_code(db, mobile, code, expires_at)
    if settings.sms_enabled:
        send_verification_sms(mobile, code)
    return {'ok': True, 'debugCode': None if settings.sms_enabled else code}


def _validate_code(db: Session, mobile: str, code: str) -> bool:
    stored = get_latest_valid_code(db, mobile)
    if not stored or stored.code != code:
        return False
    mark_code_used(db, stored)
    return True


def login_with_password(db: Session, mobile: str, password: str):
    user = get_user_by_mobile(db, mobile)
    if not user or not verify_password(password, user.password_hash):
        return {'ok': False, 'token': '', 'user': None}
    token = create_access_token(user)
    return {'ok': True, 'token': token, 'user': _to_user_payload(user)}


def login_with_code(db: Session, mobile: str, code: str):
    if not _validate_code(db, mobile, code):
        return {'ok': False, 'token': '', 'user': None}
    user = get_user_by_mobile(db, mobile)
    if not user:
        user = create_user(db, mobile)
    token = create_access_token(user)
    return {'ok': True, 'token': token, 'user': _to_user_payload(user)}


def register_with_code(db: Session, mobile: str, code: str, password: str):
    if not _validate_code(db, mobile, code):
        return {'ok': False, 'userId': None, 'token': '', 'user': None}
    user = get_user_by_mobile(db, mobile)
    password_hash = hash_password(password)
    if not user:
        user = create_user(db, mobile, password_hash=password_hash)
    else:
        user.password_hash = password_hash
        db.commit()
        db.refresh(user)
    token = create_access_token(user)
    return {'ok': True, 'userId': user.id, 'token': token, 'user': _to_user_payload(user)}


def get_me(user: User):
    return _to_user_payload(user)


def logout():
    return {'ok': True}


def _to_user_payload(user: User):
    return {'id': user.id, 'mobile': user.mobile, 'name': user.name, 'role': user.role}
