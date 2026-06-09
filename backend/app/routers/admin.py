from fastapi import APIRouter

from app import services

router = APIRouter(prefix='/api/admin', tags=['admin'])


@router.get('/jobs')
def read_admin_jobs():
    return services.get_admin_jobs()
