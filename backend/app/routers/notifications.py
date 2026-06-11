from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.db.base import User
from app.db.session import DbSession
from app.models import MarkNotificationReadResponse, NotificationListResponse, UnreadCountResponse
from app.services import notification_service

router = APIRouter(prefix='/api/notifications', tags=['notifications'])


@router.get('', response_model=NotificationListResponse)
def read_notifications(db: DbSession, user: User = Depends(get_current_user)):
    return notification_service.list_notifications(db, user)


@router.get('/unread-count', response_model=UnreadCountResponse)
def read_unread_count(db: DbSession, user: User = Depends(get_current_user)):
    return notification_service.get_unread_count(db, user)


@router.post('/{notification_id}/read', response_model=MarkNotificationReadResponse)
def mark_notification_read(notification_id: int, db: DbSession, user: User = Depends(get_current_user)):
    return notification_service.mark_read(db, user, notification_id)
