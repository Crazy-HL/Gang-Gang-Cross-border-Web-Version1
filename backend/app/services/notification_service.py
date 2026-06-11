from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.base import User
from app.repositories import notification_repository


def list_notifications(db: Session, user: User):
    return {
        'unreadCount': notification_repository.count_unread_notifications(db, user.id),
        'notifications': notification_repository.list_user_notifications(db, user.id),
    }


def get_unread_count(db: Session, user: User):
    return {'unreadCount': notification_repository.count_unread_notifications(db, user.id)}


def mark_read(db: Session, user: User, notification_id: int):
    if not notification_repository.mark_notification_read(db, user.id, notification_id):
        raise HTTPException(status_code=404, detail='Notification not found')
    return {'ok': True}


def create_review_notification(db: Session, user_id: int, job_title: str, review_status: str, review_note: str):
    if review_status == 'approved':
        title = '人工复核已通过'
        content = f'你的任务「{job_title}」已通过人工复核。'
    else:
        title = '人工复核已驳回'
        content = f'你的任务「{job_title}」未通过人工复核。'
    if review_note:
        content = f'{content} 备注：{review_note}'
    return notification_repository.create_notification(db, user_id, title, content, 'review')
