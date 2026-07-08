from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.db.base import User
from app.db.session import DbSession
from app.models import ServiceRequestCreate, ServiceRequestCreateResponse, ServiceRequestItem
from app.services import service_request_service

router = APIRouter(prefix='/api/service-requests', tags=['service-requests'])


@router.get('', response_model=list[ServiceRequestItem])
def read_service_requests(db: DbSession, user: User = Depends(get_current_user)):
    return service_request_service.list_user_service_requests(db, user)


@router.post('', response_model=ServiceRequestCreateResponse)
def create_service_request(payload: ServiceRequestCreate, db: DbSession, user: User = Depends(get_current_user)):
    result = service_request_service.create_user_service_request(db, payload, user)
    if not result['ok']:
        raise HTTPException(status_code=400, detail=result['error'])
    return {'ok': True, 'request': result['request'], 'adviceReport': result['adviceReport']}
