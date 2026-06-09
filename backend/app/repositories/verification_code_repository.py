from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import VerificationCode


def create_verification_code(db: Session, mobile: str, code: str, expires_at: datetime) -> VerificationCode:
    item = VerificationCode(mobile=mobile, code=code, expires_at=expires_at)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_latest_valid_code(db: Session, mobile: str) -> VerificationCode | None:
    now = datetime.now(timezone.utc)
    query = (
        select(VerificationCode)
        .where(VerificationCode.mobile == mobile, VerificationCode.used_at.is_(None), VerificationCode.expires_at >= now)
        .order_by(VerificationCode.created_at.desc(), VerificationCode.id.desc())
    )
    return db.scalar(query)


def mark_code_used(db: Session, verification_code: VerificationCode) -> VerificationCode:
    verification_code.used_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(verification_code)
    return verification_code
