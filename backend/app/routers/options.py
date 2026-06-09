from fastapi import APIRouter

from app import services

router = APIRouter(prefix='/api/options', tags=['options'])


@router.get('')
def read_options():
    return services.get_options()
