import json

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.base import ServiceRequest
from app.models import ServiceRequestCreate
from app.repositories.utils import format_datetime


def _details_from_payload(payload: ServiceRequestCreate, advice_report: dict | None = None):
    details = {
        'issueType': payload.issueType.strip(),
        'caseStatus': payload.caseStatus.strip(),
        'storeName': payload.storeName.strip(),
        'frozenAmount': payload.frozenAmount.strip(),
        'caseNumber': payload.caseNumber.strip(),
        'claimant': payload.claimant.strip(),
        'fileNames': [name.strip() for name in payload.fileNames if name.strip()],
    }
    if advice_report:
        details['adviceReport'] = advice_report
    return details


def service_request_to_dict(item: ServiceRequest):
    details = json.loads(item.details_json or '{}')
    return {
        'id': item.id,
        'requestType': item.request_type,
        'title': item.title,
        'platform': item.platform,
        'status': item.status,
        'contact': item.contact,
        'reference': item.reference,
        'description': item.description,
        'issueType': details.get('issueType', ''),
        'caseStatus': details.get('caseStatus', ''),
        'storeName': details.get('storeName', ''),
        'frozenAmount': details.get('frozenAmount', ''),
        'caseNumber': details.get('caseNumber', ''),
        'claimant': details.get('claimant', ''),
        'fileNames': details.get('fileNames', []),
        'adviceReport': details.get('adviceReport'),
        'createdAt': format_datetime(item.created_at),
    }


def create_service_request(db: Session, request_id: str, owner_id: int, payload: ServiceRequestCreate, advice_report: dict | None = None) -> ServiceRequest:
    details = _details_from_payload(payload, advice_report)
    title = payload.title.strip()
    if not title:
        title = details['issueType'] or details['caseStatus'] or '服务工单'
    item = ServiceRequest(
        id=request_id,
        owner_id=owner_id,
        request_type=payload.requestType,
        title=title,
        platform=payload.platform.strip(),
        status='pending',
        contact=payload.contact.strip(),
        reference=payload.reference.strip(),
        description=payload.description.strip(),
        details_json=json.dumps(details, ensure_ascii=False, separators=(',', ':')),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_service_requests(db: Session, owner_id: int):
    query = (
        select(ServiceRequest)
        .options(selectinload(ServiceRequest.owner))
        .where(ServiceRequest.owner_id == owner_id)
        .order_by(ServiceRequest.created_at.desc())
    )
    return [service_request_to_dict(item) for item in db.scalars(query).all()]
