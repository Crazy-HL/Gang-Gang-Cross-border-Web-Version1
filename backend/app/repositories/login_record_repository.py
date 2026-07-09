from sqlalchemy.orm import Session

from app.db.base import LoginRecord, User


def create_login_record(db: Session, user: User, login_method: str, ip_address: str = '', user_agent: str = '') -> LoginRecord:
    record = LoginRecord(
        user_id=user.id,
        login_method=login_method,
        ip_address=ip_address[:64],
        user_agent=user_agent[:1000],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
