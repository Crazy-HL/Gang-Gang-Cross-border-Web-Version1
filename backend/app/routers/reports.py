from fastapi import APIRouter, HTTPException

from app import services

router = APIRouter(prefix='/api/reports', tags=['reports'])


@router.get('')
def read_reports():
    return services.get_reports()


@router.get('/{report_id}')
def read_report(report_id: str):
    report = services.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail='Report not found')
    return report
