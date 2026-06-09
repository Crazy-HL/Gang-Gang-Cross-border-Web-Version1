from fastapi import APIRouter

from app import services
from app.models import AuthRequest, MobileRequest

router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/code')
def send_code(payload: MobileRequest):
    return services.send_code(payload.mobile)


@router.post('/login')
def login(payload: AuthRequest):
    return services.login_with_code(payload.mobile, payload.code)


@router.post('/register')
def register(payload: AuthRequest):
    return services.register_with_code(payload.mobile, payload.code)
