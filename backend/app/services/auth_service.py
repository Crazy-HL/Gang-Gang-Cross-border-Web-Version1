from __future__ import annotations

import random
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

from fastapi import HTTPException
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.base import User
from app.repositories import admin_account_repository
from app.repositories.login_record_repository import create_login_record
from app.repositories.user_repository import create_user, get_user_by_mobile
from app.repositories.verification_code_repository import create_verification_code, get_latest_valid_code, mark_code_used
from app.services.sms_service import send_verification_sms

settings = get_settings()
ADMIN_PASSWORD_LOGIN_ACCOUNT = 'admin'
PHONE_NUMBER_PATTERN = re.compile(r'1\d{10}')
WECHAT_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token'
WECHAT_PHONE_NUMBER_URL = 'https://api.weixin.qq.com/wxa/business/getuserphonenumber'
WECHAT_MINI_SESSION_URL = 'https://api.weixin.qq.com/sns/jscode2session'
WECHAT_WEB_QRCONNECT_URL = 'https://open.weixin.qq.com/connect/qrconnect'
WECHAT_WEB_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token'
WECHAT_WEB_USER_INFO_URL = 'https://api.weixin.qq.com/sns/userinfo'
AVATAR_UPLOAD_ROOT = Path(__file__).resolve().parents[2] / 'uploads' / 'avatars'
AVATAR_ALLOWED_CONTENT_TYPES = {'image/jpeg': '.jpg', 'image/png': '.png'}
AVATAR_MAX_UPLOAD_BYTES = 2 * 1024 * 1024


def _generate_code() -> str:
    return f'{random.randint(0, 999999):06d}'


def _normalize_account(account: str) -> str:
    return account.strip()


def _is_phone_number(account: str) -> bool:
    return bool(PHONE_NUMBER_PATTERN.fullmatch(_normalize_account(account)))


def _can_use_password_login(account: str) -> bool:
    normalized = _normalize_account(account)
    return _is_phone_number(normalized) or normalized == ADMIN_PASSWORD_LOGIN_ACCOUNT


def _safe_filename(filename: str) -> str:
    name = filename.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
    name = re.sub(r'[^A-Za-z0-9._-]+', '-', name).strip('.-')
    return name or 'avatar'


def _clean_profile_name(name: str) -> str:
    return _normalize_account(name)[:80]


def _clean_avatar_url(avatar_url: str) -> str:
    avatar_url = _normalize_account(avatar_url)
    if not avatar_url:
        return ''
    if avatar_url.startswith('/uploads/avatars/') or avatar_url.startswith('https://') or avatar_url.startswith('http://'):
        return avatar_url[:512]
    return ''


def _wechat_web_mobile(openid: str) -> str:
    clean_openid = re.sub(r'[^A-Za-z0-9_-]+', '', _normalize_account(openid))[:24]
    return f'wx_web_{clean_openid or "user"}'


def _get_user_by_wechat_unionid(db: Session, unionid: str) -> User | None:
    unionid = _normalize_account(unionid)
    if not unionid:
        return None
    return db.execute(select(User).where(User.wechat_unionid == unionid)).scalars().first()


def _get_user_by_wechat_web_openid(db: Session, openid: str) -> User | None:
    openid = _normalize_account(openid)
    if not openid:
        return None
    return db.execute(select(User).where(User.wechat_web_openid == openid)).scalars().first()


def send_code(db: Session, mobile: str):
    mobile = _normalize_account(mobile)
    if not _is_phone_number(mobile):
        return {'ok': False, 'debugCode': None}
    code = _generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.verification_code_ttl_seconds)
    create_verification_code(db, mobile, code, expires_at)
    if settings.sms_enabled:
        send_verification_sms(mobile, code)
    return {'ok': True, 'debugCode': None if settings.sms_enabled else code}


def _validate_code(db: Session, mobile: str, code: str) -> bool:
    mobile = _normalize_account(mobile)
    if not _is_phone_number(mobile):
        return False
    stored = get_latest_valid_code(db, mobile)
    if not stored or stored.code != code:
        return False
    mark_code_used(db, stored)
    return True


def _record_login(db: Session, user: User, login_method: str, ip_address: str = '', user_agent: str = ''):
    create_login_record(db, user, login_method, ip_address, user_agent)


def login_with_password(db: Session, mobile: str, password: str, ip_address: str = '', user_agent: str = ''):
    mobile = _normalize_account(mobile)
    if not _can_use_password_login(mobile):
        return {'ok': False, 'token': '', 'user': None, 'needsPasswordSetup': False, 'reason': 'invalid_account'}
    user = get_user_by_mobile(db, mobile)
    if user and not user.password_hash:
        return {'ok': False, 'token': '', 'user': None, 'needsPasswordSetup': False, 'reason': 'password_not_set'}
    if not user or not verify_password(password, user.password_hash):
        return {'ok': False, 'token': '', 'user': None, 'needsPasswordSetup': False, 'reason': 'invalid_credentials'}
    _record_login(db, user, 'password', ip_address, user_agent)
    token = create_access_token(user)
    return {'ok': True, 'token': token, 'user': _to_user_payload(user, db), 'needsPasswordSetup': False, 'reason': ''}


def login_with_code(db: Session, mobile: str, code: str, ip_address: str = '', user_agent: str = ''):
    mobile = _normalize_account(mobile)
    if not _validate_code(db, mobile, code):
        return {'ok': False, 'token': '', 'user': None, 'needsPasswordSetup': False, 'reason': 'invalid_code'}
    user = get_user_by_mobile(db, mobile)
    if not user:
        user = create_user(db, mobile)
    needs_password_setup = not bool(user.password_hash)
    _record_login(db, user, 'sms_code', ip_address, user_agent)
    token = create_access_token(user)
    return {'ok': True, 'token': token, 'user': _to_user_payload(user, db), 'needsPasswordSetup': needs_password_setup, 'reason': ''}


def fetch_wechat_phone_number(phone_code: str) -> str:
    phone_code = _normalize_account(phone_code)
    if not phone_code or not settings.wechat_mini_appid or not settings.wechat_mini_secret:
        return ''

    try:
        token_response = httpx.get(
            WECHAT_ACCESS_TOKEN_URL,
            params={
                'grant_type': 'client_credential',
                'appid': settings.wechat_mini_appid,
                'secret': settings.wechat_mini_secret,
            },
            timeout=settings.wechat_api_timeout_seconds,
        )
        token_data = token_response.json()
        access_token = token_data.get('access_token', '')
        if not access_token:
            return ''

        phone_response = httpx.post(
            WECHAT_PHONE_NUMBER_URL,
            params={'access_token': access_token},
            json={'code': phone_code},
            timeout=settings.wechat_api_timeout_seconds,
        )
        phone_data = phone_response.json()
    except (httpx.HTTPError, ValueError):
        return ''

    if int(phone_data.get('errcode', 0)) != 0:
        return ''
    phone_info = phone_data.get('phone_info') or {}
    return _normalize_account(phone_info.get('purePhoneNumber') or phone_info.get('phoneNumber') or '')


def fetch_wechat_mini_session(login_code: str) -> dict:
    login_code = _normalize_account(login_code)
    if not login_code or not settings.wechat_mini_appid or not settings.wechat_mini_secret:
        return {}

    try:
        response = httpx.get(
            WECHAT_MINI_SESSION_URL,
            params={
                'appid': settings.wechat_mini_appid,
                'secret': settings.wechat_mini_secret,
                'js_code': login_code,
                'grant_type': 'authorization_code',
            },
            timeout=settings.wechat_api_timeout_seconds,
        )
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return {}

    if int(data.get('errcode', 0) or 0) != 0:
        return {}
    return {
        'openid': _normalize_account(data.get('openid', '')),
        'unionid': _normalize_account(data.get('unionid', '')),
    }


def login_with_wechat_phone(db: Session, phone_code: str, login_code: str = '', ip_address: str = '', user_agent: str = ''):
    mobile = fetch_wechat_phone_number(phone_code)
    if not _is_phone_number(mobile):
        return {'ok': False, 'token': '', 'user': None, 'needsPasswordSetup': False, 'reason': 'invalid_wechat_phone_code'}

    wechat_session = fetch_wechat_mini_session(login_code) if login_code else {}
    mini_openid = _normalize_account(wechat_session.get('openid', ''))
    unionid = _normalize_account(wechat_session.get('unionid', ''))

    user = get_user_by_mobile(db, mobile)
    if not user and unionid:
        user = _get_user_by_wechat_unionid(db, unionid)
        if user and user.mobile.startswith('wx_web_'):
            user.mobile = mobile
    if not user:
        user = create_user(db, mobile)
    if mini_openid:
        user.wechat_mini_openid = mini_openid
    if unionid:
        user.wechat_unionid = unionid
    if mini_openid or unionid:
        db.commit()
        db.refresh(user)
    _record_login(db, user, 'wechat_phone', ip_address, user_agent)
    token = create_access_token(user)
    return {'ok': True, 'token': token, 'user': _to_user_payload(user, db), 'needsPasswordSetup': False, 'reason': ''}


def build_wechat_web_login_url(redirect_uri: str, state: str = '') -> str:
    redirect_uri = _normalize_account(redirect_uri)
    state = _normalize_account(state)[:128]
    if not redirect_uri or not settings.wechat_web_appid:
        return ''
    query = urlencode({
        'appid': settings.wechat_web_appid,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'snsapi_login',
        'state': state,
    })
    return f'{WECHAT_WEB_QRCONNECT_URL}?{query}#wechat_redirect'


def fetch_wechat_web_user(code: str) -> dict:
    code = _normalize_account(code)
    if not code or not settings.wechat_web_appid or not settings.wechat_web_secret:
        return {}

    try:
        token_response = httpx.get(
            WECHAT_WEB_ACCESS_TOKEN_URL,
            params={
                'appid': settings.wechat_web_appid,
                'secret': settings.wechat_web_secret,
                'code': code,
                'grant_type': 'authorization_code',
            },
            timeout=settings.wechat_api_timeout_seconds,
        )
        token_data = token_response.json()
        access_token = _normalize_account(token_data.get('access_token', ''))
        openid = _normalize_account(token_data.get('openid', ''))
        if not access_token or not openid:
            return {}

        user_response = httpx.get(
            WECHAT_WEB_USER_INFO_URL,
            params={
                'access_token': access_token,
                'openid': openid,
                'lang': 'zh_CN',
            },
            timeout=settings.wechat_api_timeout_seconds,
        )
        user_data = user_response.json()
    except (httpx.HTTPError, ValueError):
        return {}

    if int(user_data.get('errcode', 0) or 0) != 0:
        return {}
    return {
        'openid': openid,
        'unionid': _normalize_account(user_data.get('unionid') or token_data.get('unionid', '')),
        'nickname': _clean_profile_name(user_data.get('nickname', '')),
        'headimgurl': _clean_avatar_url(user_data.get('headimgurl', '')),
    }


def login_with_wechat_web(db: Session, code: str, ip_address: str = '', user_agent: str = ''):
    wechat_user = fetch_wechat_web_user(code)
    web_openid = _normalize_account(wechat_user.get('openid', ''))
    unionid = _normalize_account(wechat_user.get('unionid', ''))
    if not web_openid:
        return {'ok': False, 'token': '', 'user': None, 'needsPasswordSetup': False, 'reason': 'invalid_wechat_code'}

    user = _get_user_by_wechat_unionid(db, unionid) if unionid else None
    if not user:
        user = _get_user_by_wechat_web_openid(db, web_openid)
    if not user:
        user = get_user_by_mobile(db, _wechat_web_mobile(web_openid))
    if not user:
        user = create_user(db, _wechat_web_mobile(web_openid))

    nickname = _clean_profile_name(wechat_user.get('nickname', ''))
    avatar_url = _clean_avatar_url(wechat_user.get('headimgurl', ''))
    if nickname:
        user.name = nickname
    if avatar_url:
        user.avatar_url = avatar_url
    if unionid:
        user.wechat_unionid = unionid
    user.wechat_web_openid = web_openid
    db.commit()
    db.refresh(user)

    _record_login(db, user, 'wechat_web', ip_address, user_agent)
    token = create_access_token(user)
    return {'ok': True, 'token': token, 'user': _to_user_payload(user, db), 'needsPasswordSetup': not bool(user.password_hash), 'reason': ''}


def update_profile(db: Session, user: User, name: str = '', avatar_url: str = ''):
    clean_name = _clean_profile_name(name)
    clean_avatar_url = _clean_avatar_url(avatar_url)

    if clean_name:
        user.name = clean_name
    if clean_avatar_url:
        user.avatar_url = clean_avatar_url
    db.commit()
    db.refresh(user)
    return _to_user_payload(user, db)


def save_profile_avatar(db: Session, user: User, filename: str, content_type: str, content: bytes):
    if content_type not in AVATAR_ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail='Unsupported avatar type')
    if not content:
        raise HTTPException(status_code=400, detail='Empty avatar')
    if len(content) > AVATAR_MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail='Avatar too large')

    safe_name = _safe_filename(filename)
    stem = safe_name.rsplit('.', 1)[0] or 'avatar'
    suffix = AVATAR_ALLOWED_CONTENT_TYPES[content_type]
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    stored_filename = f'user-{user.id}-{timestamp}-{stem}{suffix}'
    AVATAR_UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    (AVATAR_UPLOAD_ROOT / stored_filename).write_bytes(content)

    avatar_url = f'/uploads/avatars/{stored_filename}'
    user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    return {'ok': True, 'avatarUrl': avatar_url, 'user': _to_user_payload(user, db)}


def register_with_code(db: Session, mobile: str, code: str, password: str, ip_address: str = '', user_agent: str = ''):
    mobile = _normalize_account(mobile)
    if not _is_phone_number(mobile):
        return {'ok': False, 'userId': None, 'token': '', 'user': None, 'reason': 'invalid_mobile'}
    user = get_user_by_mobile(db, mobile)
    if user:
        reason = 'password_not_set' if not user.password_hash else 'already_registered'
        return {'ok': False, 'userId': None, 'token': '', 'user': None, 'reason': reason}
    if not _validate_code(db, mobile, code):
        return {'ok': False, 'userId': None, 'token': '', 'user': None, 'reason': 'invalid_code'}
    password_hash = hash_password(password)
    user = create_user(db, mobile, password_hash=password_hash)
    _record_login(db, user, 'register', ip_address, user_agent)
    token = create_access_token(user)
    return {'ok': True, 'userId': user.id, 'token': token, 'user': _to_user_payload(user, db), 'reason': ''}


def set_password(db: Session, user: User, password: str):
    if len(password) < 6:
        return {'ok': False, 'user': None, 'reason': 'password_too_short'}
    user.password_hash = hash_password(password)
    db.commit()
    db.refresh(user)
    return {'ok': True, 'user': _to_user_payload(user, db), 'reason': ''}


def get_me(user: User, db: Session | None = None):
    return _to_user_payload(user, db)


def logout():
    return {'ok': True}


def _to_user_payload(user: User, db: Session | None = None):
    role = user.role
    if role != 'admin' and db and admin_account_repository.is_active_admin(db, user.id):
        role = 'admin'
    return {'id': user.id, 'mobile': user.mobile, 'name': user.name, 'avatarUrl': getattr(user, 'avatar_url', '') or '', 'role': role}
