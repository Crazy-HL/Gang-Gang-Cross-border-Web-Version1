import re
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.base import Job, User
from app.models import DetectionFormInput
from app.repositories import job_repository
from app.services import report_service


def _safe_slug(value: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', value.strip().lower())
    return slug.strip('-') or 'draft'


def _generate_job_id(input_data: DetectionFormInput) -> str:
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return f'job-{timestamp}-{_safe_slug(input_data.brand)}'


def list_user_jobs(db: Session, user: User):
    return job_repository.list_jobs(db, owner_id=user.id)


def list_all_jobs(db: Session):
    return job_repository.list_jobs(db)


def create_user_job(db: Session, input_data: DetectionFormInput, user: User):
    job = job_repository.create_job(db, _generate_job_id(input_data), input_data, owner_id=user.id)
    return {'jobId': job.id, 'input': input_data.model_dump()}


def get_user_job(db: Session, job_id: str, user: User) -> Job | None:
    job = job_repository.get_job(db, job_id)
    if not job or job.owner_id != user.id:
        return None
    return job


def run_user_job(db: Session, job_id: str, user: User):
    job = get_user_job(db, job_id, user)
    if not job:
        return None
    report = report_service.ensure_demo_report_for_job(db, job)
    job.status = 'done'
    job.risk_level = report.risk_level
    job.risk_score = report.risk_score
    db.commit()
    return {'jobId': job_id, 'status': 'queued'}


def request_review(db: Session, job_id: str, user: User, note: str = ''):
    job = get_user_job(db, job_id, user)
    if not job:
        return None
    updated = job_repository.update_job_review(db, job.id, 'pending', note.strip())
    return {'ok': True, 'jobId': updated.id, 'reviewStatus': updated.review_status}
