from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.base import Job, User
from app.db.session import SessionLocal
from app.models import DetectionFormInput
from app.repositories import job_repository
from app.services import report_service

logger = logging.getLogger(__name__)


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


def get_user_job_status(db: Session, job_id: str, user: User):
    job = get_user_job(db, job_id, user)
    if not job:
        return None
    return job_repository.job_to_dict(job)


def run_user_job(db: Session, job_id: str, user: User):
    job = get_user_job(db, job_id, user)
    if not job:
        return None
    return {'jobId': job_id, 'status': 'queued'}


def process_user_job(job_id: str, user_id: int):
    db = SessionLocal()
    job = None
    try:
        job = job_repository.get_job(db, job_id)
        if not job or job.owner_id != user_id:
            print(f'[job] skip job_id={job_id} user_id={user_id}', flush=True)
            return
        print(f'[job] start job_id={job_id} provider={getattr(report_service.model_config_repository.get_model_config(db), "provider", None)}', flush=True)
        job.status = 'processing'
        db.commit()
        report = report_service.generate_report_for_job(db, job)
        print(f'[job] report generated job_id={job_id} report_id={report.id} risk_level={report.risk_level} risk_score={report.risk_score}', flush=True)
        job.status = 'done'
        job.risk_level = report.risk_level
        job.risk_score = report.risk_score
        db.commit()
        print(f'[job] done job_id={job_id}', flush=True)
    except Exception:
        logger.exception('process_user_job failed for job %s', job_id)
        print(f'[job] failed job_id={job_id}', flush=True)
        if job:
            job.status = 'failed'
            db.commit()
    finally:
        db.close()


def request_review(db: Session, job_id: str, user: User, note: str = ''):
    job = get_user_job(db, job_id, user)
    if not job:
        return None
    updated = job_repository.update_job_review(db, job.id, 'pending', note.strip())
    return {'ok': True, 'jobId': updated.id, 'reviewStatus': updated.review_status}
