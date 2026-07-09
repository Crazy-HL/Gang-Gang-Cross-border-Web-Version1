from fastapi import APIRouter, Depends, Request

from app.core.security import get_current_user
from app.db.base import User
from app.db.session import DbSession
from app.models import AuthLoginResponse, AuthMeResponse, AuthRegisterResponse, AuthCodeResponse, CodeLoginRequest, LogoutResponse, MobileRequest, PasswordLoginRequest, RegisterRequest
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


@router.post('/register', response_model=AuthRegisterResponse)
def register(payload: RegisterRequest, request: Request, db: DbSession):
    return auth_service.register_with_code(db, payload.mobile, payload.code, payload.password, _client_ip(request), _user_agent(request))


@router.get('/me', response_model=AuthMeResponse)
def me(db: DbSession, user: User = Depends(get_current_user)):
    return auth_service.get_me(user, db)


@router.post('/logout', response_model=LogoutResponse)
def logout():
    return auth_service.logout()
