from fastapi import APIRouter, Depends, File, Query, Request, UploadFile

from app.core.security import get_current_user
from app.db.base import User
from app.db.session import DbSession
from app.models import AuthLoginResponse, AuthMeResponse, AuthRegisterResponse, AuthCodeResponse, AuthPasswordResponse, AuthProfileResponse, AvatarUploadResponse, CodeLoginRequest, LogoutResponse, MobileRequest, PasswordLoginRequest, ProfileUpdateRequest, RegisterRequest, SetPasswordRequest, WechatPhoneLoginRequest, WechatWebLoginRequest, WechatWebLoginUrlResponse
from app.services import auth_service

router = APIRouter(prefix='/api/auth', tags=['auth'])


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get('x-forwarded-for', '').split(',', 1)[0].strip()
    if forwarded_for:
        return forwarded_for
    return request.client.host if request.client else ''


def _user_agent(request: Request) -> str:
    return request.headers.get('user-agent', '')


@router.post('/code', response_model=AuthCodeResponse)
def send_code(payload: MobileRequest, db: DbSession):
    return auth_service.send_code(db, payload.mobile)


@router.post('/login', response_model=AuthLoginResponse)
def login(payload: PasswordLoginRequest, request: Request, db: DbSession):
    return auth_service.login_with_password(db, payload.mobile, payload.password, _client_ip(request), _user_agent(request))


@router.post('/login/code', response_model=AuthLoginResponse)
def login_code(payload: CodeLoginRequest, request: Request, db: DbSession):
    return auth_service.login_with_code(db, payload.mobile, payload.code, _client_ip(request), _user_agent(request))


@router.post('/wechat/phone-login', response_model=AuthLoginResponse)
def wechat_phone_login(payload: WechatPhoneLoginRequest, request: Request, db: DbSession):
    return auth_service.login_with_wechat_phone(db, payload.phoneCode, payload.loginCode, _client_ip(request), _user_agent(request))


@router.get('/wechat/web/login-url', response_model=WechatWebLoginUrlResponse)
def wechat_web_login_url(redirectUri: str = Query(..., min_length=1), state: str = Query('', max_length=128)):
    url = auth_service.build_wechat_web_login_url(redirectUri, state)
    if not url:
        return {'ok': False, 'url': '', 'reason': 'wechat_web_not_configured'}
    return {'ok': True, 'url': url, 'reason': ''}


@router.post('/wechat/web-login', response_model=AuthLoginResponse)
def wechat_web_login(payload: WechatWebLoginRequest, request: Request, db: DbSession):
    return auth_service.login_with_wechat_web(db, payload.code, _client_ip(request), _user_agent(request))


@router.post('/register', response_model=AuthRegisterResponse)
def register(payload: RegisterRequest, request: Request, db: DbSession):
    return auth_service.register_with_code(db, payload.mobile, payload.code, payload.password, _client_ip(request), _user_agent(request))


@router.get('/me', response_model=AuthMeResponse)
def me(db: DbSession, user: User = Depends(get_current_user)):
    return auth_service.get_me(user, db)


@router.post('/profile', response_model=AuthProfileResponse)
def update_profile(payload: ProfileUpdateRequest, db: DbSession, user: User = Depends(get_current_user)):
    return {'ok': True, 'user': auth_service.update_profile(db, user, payload.name, payload.avatarUrl)}


@router.post('/profile/avatar', response_model=AvatarUploadResponse)
async def update_profile_avatar(db: DbSession, file: UploadFile = File(...), user: User = Depends(get_current_user)):
    content = await file.read()
    return auth_service.save_profile_avatar(db, user, file.filename or 'avatar', file.content_type or '', content)


@router.post('/password', response_model=AuthPasswordResponse)
def set_password(payload: SetPasswordRequest, db: DbSession, user: User = Depends(get_current_user)):
    return auth_service.set_password(db, user, payload.password)


@router.post('/logout', response_model=LogoutResponse)
def logout():
    return auth_service.logout()
