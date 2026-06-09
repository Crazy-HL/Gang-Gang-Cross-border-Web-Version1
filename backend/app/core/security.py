import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone

from fastapi import Header, HTTPException, status

from app.core.config import get_settings
from app.db.base import User
from app.db.session import DbSession
from app.repositories.user_repository import get_user_by_id

settings = get_settings()


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip('=')


def _b64decode(value: str) -> bytes:
    padded = value + '=' * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode())


def hash_password(password: str) -> str:
    salt = secrets.token_urlsafe(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 120000).hex()
    return f'pbkdf2_sha256$120000${salt}${digest}'


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, digest = password_hash.split('$', 3)
        if algorithm != 'pbkdf2_sha256':
            return False
        candidate = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), int(iterations)).hex()
        return hmac.compare_digest(candidate, digest)
    except Exception:
        return False

def create_access_token(user: User) -> str:
    payload = {
        'sub': str(user.id),
        'mobile': user.mobile,
        'name': user.name,
        'role': user.role,
        'exp': int(datetime.now(timezone.utc).timestamp()) + settings.access_token_ttl_seconds,
    }
    body = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode()
    signature = hmac.new(settings.secret_key.encode(), body, hashlib.sha256).digest()
    return f'{_b64encode(body)}.{_b64encode(signature)}'


def decode_access_token(token: str):
    try:
        body_part, signature_part = token.split('.', 1)
        body = _b64decode(body_part)
        signature = _b64decode(signature_part)
        expected = hmac.new(settings.secret_key.encode(), body, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(body.decode())
        if int(payload.get('exp', 0)) < int(datetime.now(timezone.utc).timestamp()):
            return None
        return payload
    except Exception:
        return None


def get_token_from_authorization(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        return None
    return token


def get_current_user(db: DbSession, authorization: str | None = Header(default=None)) -> User:
    token = get_token_from_authorization(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    user = get_user_by_id(db, int(payload['sub']))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    return user
