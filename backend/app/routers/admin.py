from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.db.base import User
from app.db.session import DbSession
from app.services import admin_service

router = APIRouter(prefix='/api/admin', tags=['admin'])


@router.get('/jobs')
def read_admin_jobs(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_jobs(db, user)
