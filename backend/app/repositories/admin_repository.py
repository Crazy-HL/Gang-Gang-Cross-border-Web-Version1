from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.base import Job, Notification, Report, ServiceRequest, User
from app.repositories.job_repository import get_job, job_to_dict, list_jobs, update_job_review
from app.repositories.utils import format_datetime
from app.services.report_service import service_request_report_to_dict


def _type_label(value: str):
    return {
        'ip_detection': '侵权检测',
        'appeal': '平台申诉',
        'tro_settlement': 'TRO 和解',
    }.get(value, value)


def get_admin_overview(db: Session):
    total_jobs = db.scalar(select(func.count()).select_from(Job)) or 0
    total_users = db.scalar(select(func.count()).select_from(User)) or 0
    total_reports = (db.scalar(select(func.count()).select_from(Report)) or 0) + len(_list_service_report_rows(db, limit=None))
    total_service_requests = db.scalar(select(func.count()).select_from(ServiceRequest)) or 0
    unread_notifications = db.scalar(
        select(func.count()).select_from(Notification).where(Notification.is_read.is_(False))
    ) or 0
    pending_reviews = db.scalar(select(func.count()).select_from(Job).where(Job.review_status == 'pending')) or 0
    completed_jobs = db.scalar(select(func.count()).select_from(Job).where(Job.status == 'done')) or 0
    high_risk_jobs = db.scalar(select(func.count()).select_from(Job).where(Job.risk_level == 'high')) or 0
    return {
        'totalJobs': total_jobs,
        'totalUsers': total_users,
        'completedJobs': completed_jobs,
        'highRiskRate': high_risk_jobs / total_jobs if total_jobs else 0,
        'totalReports': total_reports,
        'totalServiceRequests': total_service_requests,
        'unreadNotifications': unread_notifications,
        'pendingReviews': pending_reviews,
    }


def list_admin_users(db: Session, limit: int = 100) -> list[dict]:
    users = db.scalars(select(User).order_by(User.created_at.desc()).limit(limit)).all()
    rows = []
    for user in users:
        rows.append({
            'id': user.id,
            'mobile': user.mobile,
            'name': user.name,
            'role': user.role,
            'createdAt': format_datetime(user.created_at),
            'jobCount': len(user.jobs),
            'serviceRequestCount': len(user.service_requests),
        })
    return rows


def list_admin_reports(db: Session, limit: int = 100) -> list[dict]:
    rows = _list_ip_report_rows(db, limit) + _list_service_report_rows(db, limit)
    return sorted(rows, key=lambda item: item['generatedAt'], reverse=True)[:limit]


def list_admin_service_requests(db: Session, limit: int = 100) -> list[dict]:
    query = (
        select(ServiceRequest)
        .options(selectinload(ServiceRequest.owner))
        .order_by(ServiceRequest.created_at.desc())
        .limit(limit)
    )
    rows = []
    for item in db.scalars(query).all():
        rows.append({
            'id': item.id,
            'requestType': item.request_type,
            'typeLabel': _type_label(item.request_type),
            'title': item.title,
            'platform': item.platform,
            'status': item.status,
            'contact': item.contact,
            'ownerName': item.owner.name if item.owner else '未绑定用户',
            'ownerMobile': item.owner.mobile if item.owner else '',
            'createdAt': format_datetime(item.created_at),
            'linkId': item.id,
        })
    return rows


def _list_ip_report_rows(db: Session, limit: int = 100) -> list[dict]:
    query = (
        select(Report)
        .options(selectinload(Report.job).selectinload(Job.owner))
        .order_by(Report.generated_at.desc())
        .limit(limit)
    )
    rows = []
    for report in db.scalars(query).all():
        owner = report.job.owner if report.job else None
        rows.append({
            'id': report.id,
            'reportType': 'ip_detection',
            'typeLabel': _type_label('ip_detection'),
            'title': report.title,
            'ownerName': owner.name if owner else '未绑定用户',
            'ownerMobile': owner.mobile if owner else '',
            'riskLevel': report.risk_level,
            'riskScore': report.risk_score,
            'generatedAt': format_datetime(report.generated_at),
            'linkId': report.id,
        })
    return rows


def _list_service_report_rows(db: Session, limit: int | None = 100) -> list[dict]:
    query = (
        select(ServiceRequest)
        .options(selectinload(ServiceRequest.owner))
        .order_by(ServiceRequest.created_at.desc())
    )
    if limit is not None:
        query = query.limit(limit)
    rows = []
    for item in db.scalars(query).all():
        report = service_request_report_to_dict(item)
        if not report:
            continue
        rows.append({
            'id': report['id'],
            'reportType': report['reportType'],
            'typeLabel': report['typeLabel'],
            'title': report['title'],
            'ownerName': item.owner.name if item.owner else '未绑定用户',
            'ownerMobile': item.owner.mobile if item.owner else '',
            'riskLevel': report['riskLevel'],
            'riskScore': report['riskScore'],
            'generatedAt': report['generatedAt'],
            'linkId': item.id,
        })
    return rows


def list_admin_notifications(db: Session, limit: int = 100) -> list[dict]:
    query = (
        select(Notification)
        .options(selectinload(Notification.user))
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    rows = []
    for item in db.scalars(query).all():
        rows.append({
            'id': item.id,
            'title': item.title,
            'content': item.content,
            'type': item.type,
            'isRead': item.is_read,
            'ownerName': item.user.name if item.user else '未绑定用户',
            'ownerMobile': item.user.mobile if item.user else '',
            'createdAt': format_datetime(item.created_at),
        })
    return rows


def get_admin_stats(db: Session):
    return get_admin_overview(db)


def get_admin_jobs(db: Session):
    return {'stats': get_admin_overview(db), 'jobs': list_jobs(db)}


def update_admin_job_review(db: Session, job_id: str, status: str, note: str):
    job = update_job_review(db, job_id, status, note)
    return job_to_dict(job) if job else None


def get_admin_job(db: Session, job_id: str):
    return get_job(db, job_id)
