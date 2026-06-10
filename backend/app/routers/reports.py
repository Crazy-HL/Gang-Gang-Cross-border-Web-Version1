from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.db.base import User
from app.db.session import DbSession
from app.services import report_service

router = APIRouter(prefix='/api/reports', tags=['reports'])


@router.get('')
def read_reports(db: DbSession, user: User = Depends(get_current_user)):
    return report_service.list_user_reports(db, user)


@router.get('/{report_id}')
def read_report(report_id: str, db: DbSession, user: User = Depends(get_current_user)):
    report = report_service.get_user_report(db, report_id, user)
    if not report:
        raise HTTPException(status_code=404, detail='Report not found')
    return report
