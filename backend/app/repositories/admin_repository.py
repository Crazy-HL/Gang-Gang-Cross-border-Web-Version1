from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import Job, User
from app.repositories.job_repository import get_job, job_to_dict, list_jobs, update_job_review


def get_admin_stats(db: Session):
    total_jobs = db.scalar(select(func.count()).select_from(Job)) or 0
    total_users = db.scalar(select(func.count()).select_from(User)) or 0
    completed_jobs = db.scalar(select(func.count()).select_from(Job).where(Job.status == 'done')) or 0
    high_risk_jobs = db.scalar(select(func.count()).select_from(Job).where(Job.risk_level == 'high')) or 0
    return {
        'totalJobs': total_jobs,
        'totalUsers': total_users,
        'completedJobs': completed_jobs,
        'highRiskRate': high_risk_jobs / total_jobs if total_jobs else 0,
    }


def get_admin_jobs(db: Session):
    return {'stats': get_admin_stats(db), 'jobs': list_jobs(db)}


def update_admin_job_review(db: Session, job_id: str, status: str, note: str):
    job = update_job_review(db, job_id, status, note)
    return job_to_dict(job) if job else None


def get_admin_job(db: Session, job_id: str):
    return get_job(db, job_id)
