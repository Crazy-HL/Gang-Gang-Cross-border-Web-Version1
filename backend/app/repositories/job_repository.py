from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.base import Job, JobFile
from app.models import DetectionFormInput
from app.repositories.utils import format_datetime


def job_to_dict(job: Job):
    return {
        'id': job.id,
        'type': job.type,
        'title': job.title,
        'brand': job.brand,
        'category': job.category,
        'market': job.market,
        'status': job.status,
        'riskLevel': job.risk_level,
        'riskScore': job.risk_score,
        'createdAt': format_datetime(job.created_at),
        'ownerName': job.owner.name if job.owner else '张三',
        'reviewStatus': job.review_status,
        'reviewNote': job.review_note,
        'fileUrl': job.files[0].file_url if job.files else '',
    }


def list_jobs(db: Session, owner_id: int | None = None):
    query = select(Job).options(selectinload(Job.owner), selectinload(Job.files)).order_by(Job.created_at.desc())
    if owner_id is not None:
        query = query.where(Job.owner_id == owner_id)
    return [job_to_dict(job) for job in db.scalars(query).all()]


def get_job(db: Session, job_id: str) -> Job | None:
    return db.scalar(select(Job).options(selectinload(Job.owner), selectinload(Job.files)).where(Job.id == job_id))


def create_job(db: Session, job_id: str, input_data: DetectionFormInput, owner_id: int | None = None) -> Job:
    title = input_data.title.strip() or input_data.productLink.strip() or '自动知识产权风险检测'
    job = Job(
        id=job_id,
        owner_id=owner_id,
        type=input_data.detectionType or 'trademark',
        title=title,
        brand=input_data.brand.strip() or '待识别品牌',
        category=input_data.category.strip() or 'auto',
        market=input_data.market.strip() or 'global',
        product_link=input_data.productLink.strip(),
        status='queued',
        risk_level='pending',
        risk_score=None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def create_job_file(db: Session, job_id: str, filename: str, content_type: str, size: int, file_url: str) -> JobFile:
    file = JobFile(job_id=job_id, filename=filename, content_type=content_type, size=size, file_url=file_url)
    db.add(file)
    db.commit()
    db.refresh(file)
    return file


def update_job_status(db: Session, job_id: str, status: str) -> Job | None:
    job = get_job(db, job_id)
    if not job:
        return None
    job.status = status
    db.commit()
    db.refresh(job)
    return job


def update_job_review(db: Session, job_id: str, status: str, note: str = '') -> Job | None:
    job = get_job(db, job_id)
    if not job:
        return None
    job.review_status = status
    job.review_note = note
    db.commit()
    db.refresh(job)
    return job
