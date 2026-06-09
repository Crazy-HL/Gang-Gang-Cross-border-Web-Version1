from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.db.base import User
from app.db.session import DbSession
from app.models import AuthLoginResponse, AuthMeResponse, AuthRegisterResponse, AuthCodeResponse, CodeLoginRequest, LogoutResponse, MobileRequest, PasswordLoginRequest, RegisterRequest
from app.services import auth_service

router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/code', response_model=AuthCodeResponse)
def send_code(payload: MobileRequest, db: DbSession):
    return auth_service.send_code(db, payload.mobile)


@router.post('/login', response_model=AuthLoginResponse)
def login(payload: PasswordLoginRequest, db: DbSession):
    return auth_service.login_with_password(db, payload.mobile, payload.password)


@router.post('/login/code', response_model=AuthLoginResponse)
def login_code(payload: CodeLoginRequest, db: DbSession):
    return auth_service.login_with_code(db, payload.mobile, payload.code)


@router.post('/register', response_model=AuthRegisterResponse)
def register(payload: RegisterRequest, db: DbSession):
    return auth_service.register_with_code(db, payload.mobile, payload.code, payload.password)


@router.get('/me', response_model=AuthMeResponse)
def me(user: User = Depends(get_current_user)):
    return auth_service.get_me(user)


@router.post('/logout', response_model=LogoutResponse)
def logout():
    return auth_service.logout()
