from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.db.base import User
from app.db.session import DbSession
from app.models import AdminReviewRequest, ModelConfigResponse, ModelConfigUpdateRequest
from app.services import admin_service

router = APIRouter(prefix='/api/admin', tags=['admin'])


@router.get('/overview')
def read_admin_overview(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_overview(db, user)


@router.get('/users')
def read_admin_users(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_users(db, user)


@router.get('/reports')
def read_admin_reports(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_reports(db, user)


@router.get('/service-requests')
def read_admin_service_requests(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_service_requests(db, user)


@router.get('/notifications')
def read_admin_notifications(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_notifications(db, user)


@router.get('/jobs')
def read_admin_jobs(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_jobs(db, user)


@router.patch('/jobs/{job_id}/review')
def update_job_review(job_id: str, payload: AdminReviewRequest, db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.update_job_review(db, user, job_id, payload.reviewStatus, payload.reviewNote)


@router.get('/model-config', response_model=ModelConfigResponse)
def read_model_config(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_model_config(db, user)


@router.put('/model-config', response_model=ModelConfigResponse)
def update_model_config(payload: ModelConfigUpdateRequest, db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.update_model_config(db, user, payload.provider, payload.modelName, payload.apiKey, payload.baseUrl, payload.temperature, payload.maxTokens, payload.enabled)
