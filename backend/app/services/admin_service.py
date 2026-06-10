from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import User
from app.repositories import admin_repository


def get_admin_jobs(db: Session, user: User):
    if user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return admin_repository.get_admin_jobs(db)
