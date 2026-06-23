import json

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.base import CategoryScore, Evidence, Report
from app.repositories.utils import format_datetime


def _truncate(value: str, limit: int) -> str:
    text = str(value or '')
    return text if len(text) <= limit else text[:limit]


def report_to_dict(report: Report):
    return {
        'id': report.id,
        'jobId': report.job_id,
        'title': report.title,
        'generatedAt': format_datetime(report.generated_at),
        'riskLevel': report.risk_level,
        'riskScore': report.risk_score,
        'summary': report.summary,
        'categoryScores': [
            {'type': item.type, 'label': item.label, 'score': item.score, 'hits': item.hits}
            for item in report.category_scores
        ],
        'evidence': [
            {'id': item.id, 'category': item.category, 'matched': item.matched, 'source': item.source, 'similarity': item.similarity, 'description': item.description, 'imageUrl': item.image_url}
            for item in report.evidence
        ],
        'suggestions': json.loads(report.suggestions_json or '[]'),
        'reviewStatus': report.job.review_status if report.job else 'none',
        'reviewNote': report.job.review_note if report.job else '',
    }


def list_reports(db: Session):
    query = select(Report).options(selectinload(Report.category_scores), selectinload(Report.evidence), selectinload(Report.job)).order_by(Report.generated_at.desc())
    return [report_to_dict(report) for report in db.scalars(query).all()]


def get_report(db: Session, report_id: str) -> Report | None:
    query = select(Report).options(selectinload(Report.category_scores), selectinload(Report.evidence), selectinload(Report.job)).where(or_(Report.id == report_id, Report.job_id == report_id))
    return db.scalar(query)


def create_report(db: Session, report_data: dict) -> Report:
    report = Report(
        id=_truncate(report_data['id'], 64),
        job_id=report_data['jobId'],
        title=_truncate(report_data['title'], 255),
        risk_level=report_data['riskLevel'],
        risk_score=report_data['riskScore'],
        summary=report_data['summary'],
        suggestions_json=json.dumps(report_data.get('suggestions', []), ensure_ascii=False),
    )
    try:
        db.add(report)
        for item in report_data.get('categoryScores', []):
            db.add(CategoryScore(report_id=report.id, type=_truncate(item['type'], 32), label=_truncate(item['label'], 80), score=item['score'], hits=item['hits']))
        for item in report_data.get('evidence', []):
            db.add(Evidence(report_id=report.id, id=_truncate(item['id'], 64), category=_truncate(item['category'], 32), matched=_truncate(item['matched'], 255), source=_truncate(item['source'], 120), similarity=item['similarity'], description=item['description'], image_url=item['imageUrl']))
        db.commit()
        db.refresh(report)
        return report
    except Exception:
        db.rollback()
        raise
