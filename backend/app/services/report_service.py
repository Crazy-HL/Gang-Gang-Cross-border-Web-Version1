from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.base import Job, Report
from app.repositories import report_repository


def _risk_level(score: int) -> str:
    if score >= 75:
        return 'high'
    if score >= 45:
        return 'medium'
    return 'low'


def _demo_score(job: Job) -> int:
    base = 45 + (len(job.brand) * 7 + len(job.market) * 3) % 45
    return min(base, 92)


def _demo_report_payload(job: Job):
    score = _demo_score(job)
    risk_level = _risk_level(score)
    brand = job.brand.upper() or 'DRAFT BRAND'
    image_url = job.files[0].file_url if job.files else '/evidence/activewear.svg'
    return {
        'id': f'r-{job.id}',
        'jobId': job.id,
        'title': f'{brand} 知识产权风险预检报告',
        'riskLevel': risk_level,
        'riskScore': score,
        'summary': f'{brand} 在 {job.market} 市场的 {job.category} 类目存在{risk_level}级知识产权风险，当前报告为数据库演示结果，后续可接入真实检测引擎。',
        'categoryScores': [
            {'type': 'trademark', 'label': '商标', 'score': min(score + 5, 100), 'hits': 2 if score >= 60 else 1},
            {'type': 'design', 'label': '外观', 'score': max(score - 8, 0), 'hits': 1},
            {'type': 'copyright', 'label': '版权', 'score': max(score - 18, 0), 'hits': 0 if score < 75 else 1},
        ],
        'evidence': [
            {
                'id': f'ev-{job.id}',
                'category': job.type,
                'matched': brand,
                'source': 'Demo IP Index',
                'similarity': round(score / 100, 2),
                'description': '演示报告基于任务品牌、类目和市场生成，用于验证任务、报告和数据库链路。',
                'imageUrl': image_url,
            }
        ],
        'suggestions': ['接入真实检测引擎后重新运行检测。', '保留商品图片、链接和品牌使用证据。', '中高风险任务建议提交人工复核。'],
    }


def ensure_demo_report_for_job(db: Session, job: Job) -> Report:
    existing = report_repository.get_report(db, job.id)
    if existing:
        return existing
    return report_repository.create_report(db, _demo_report_payload(job))


def get_user_job_results(db: Session, job: Job):
    report = report_repository.get_report(db, job.id)
    return report_repository.report_to_dict(report) if report else None


def get_user_report(db: Session, report_id: str, user):
    report = report_repository.get_report(db, report_id)
    if not report or not report.job or report.job.owner_id != user.id:
        return None
    return report_repository.report_to_dict(report)


def list_user_reports(db: Session, user):
    query = (
        select(Report)
        .join(Report.job)
        .options(selectinload(Report.category_scores), selectinload(Report.evidence), selectinload(Report.job))
        .where(Job.owner_id == user.id)
        .order_by(Report.generated_at.desc())
    )
    return [report_repository.report_to_dict(report) for report in db.scalars(query).all()]
