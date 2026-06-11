from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import User
from app.repositories import admin_repository, model_config_repository
from app.services import notification_service


def ensure_admin(user: User):
    if user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')


def get_admin_jobs(db: Session, user: User):
    ensure_admin(user)
    return admin_repository.get_admin_jobs(db)


def update_job_review(db: Session, user: User, job_id: str, review_status: str, review_note: str):
    ensure_admin(user)
    note = review_note.strip()
    job = admin_repository.get_admin_job(db, job_id)
    result = admin_repository.update_admin_job_review(db, job_id, review_status, note)
    if not result:
        raise HTTPException(status_code=404, detail='Job not found')
    if job and job.owner_id:
        notification_service.create_review_notification(db, job.owner_id, job.title, review_status, note)
    return result


def get_model_config(db: Session, user: User):
    ensure_admin(user)
    config = model_config_repository.get_model_config(db)
    return {'config': model_config_repository.model_config_to_dict(config) if config else None}


def update_model_config(db: Session, user: User, provider: str, model_name: str, api_key: str, base_url: str, temperature: float, max_tokens: int, enabled: bool):
    ensure_admin(user)
    config = model_config_repository.upsert_model_config(db, provider, model_name, api_key, base_url, temperature, max_tokens, enabled)
    return {'config': model_config_repository.model_config_to_dict(config)}
