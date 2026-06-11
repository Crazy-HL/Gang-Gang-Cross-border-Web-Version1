from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import Notification
from app.repositories.utils import format_datetime


def notification_to_dict(notification: Notification):
    return {
        'id': notification.id,
        'title': notification.title,
        'content': notification.content,
        'type': notification.type,
        'isRead': notification.is_read,
        'createdAt': format_datetime(notification.created_at),
    }


def create_notification(db: Session, user_id: int, title: str, content: str, type_: str = 'system'):
    notification = Notification(user_id=user_id, title=title, content=content, type=type_)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_user_notifications(db: Session, user_id: int):
    query = select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
    return [notification_to_dict(notification) for notification in db.scalars(query).all()]


def count_unread_notifications(db: Session, user_id: int):
    return db.scalar(select(func.count()).select_from(Notification).where(Notification.user_id == user_id, Notification.is_read == False)) or 0


def mark_notification_read(db: Session, user_id: int, notification_id: int):
    notification = db.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id))
    if not notification:
        return False
    notification.is_read = True
    db.commit()
    return True
