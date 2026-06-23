from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.core.security import get_current_user
from app.db.base import User
from app.db.session import DbSession
from app.models import DetectionFormInput, ReviewRequest
from app.services import file_service, job_service, report_service
from app.services.pdf_service import build_report_pdf

router = APIRouter(prefix='/api/jobs', tags=['jobs'])


@router.get('')
def read_jobs(db: DbSession, user: User = Depends(get_current_user)):
    return job_service.list_user_jobs(db, user)


@router.post('')
def create_job(payload: DetectionFormInput, db: DbSession, user: User = Depends(get_current_user)):
    return job_service.create_user_job(db, payload, user)


@router.post('/{job_id}/upload')
async def upload_job_file(job_id: str, db: DbSession, file: UploadFile = File(...), user: User = Depends(get_current_user)):
    job = job_service.get_user_job(db, job_id, user)
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    return await file_service.attach_upload(db, job, file)


@router.post('/{job_id}/run')
def run_job(job_id: str, background_tasks: BackgroundTasks, db: DbSession, user: User = Depends(get_current_user)):
    result = job_service.run_user_job(db, job_id, user)
    if not result:
        raise HTTPException(status_code=404, detail='Job not found')
    background_tasks.add_task(job_service.process_user_job, job_id, user.id)
    return result


@router.post('/{job_id}/review')
def request_job_review(job_id: str, payload: ReviewRequest, db: DbSession, user: User = Depends(get_current_user)):
    result = job_service.request_review(db, job_id, user, payload.note)
    if not result:
        raise HTTPException(status_code=404, detail='Job not found')
    return result


@router.get('/{job_id}/status')
def read_job_status(job_id: str, db: DbSession, user: User = Depends(get_current_user)):
    result = job_service.get_user_job_status(db, job_id, user)
    if not result:
        raise HTTPException(status_code=404, detail='Job not found')
    return result


@router.get('/{job_id}/results')
def read_job_results(job_id: str, db: DbSession, user: User = Depends(get_current_user)):
    job = job_service.get_user_job(db, job_id, user)
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    report = report_service.get_user_job_results(db, job)
    if not report:
        raise HTTPException(status_code=404, detail='Report not found')
    return report


@router.get('/{job_id}/report/pdf')
def download_report_pdf(job_id: str, db: DbSession, user: User = Depends(get_current_user)):
    job = job_service.get_user_job(db, job_id, user)
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    report = report_service.get_user_job_results(db, job)
    if not report:
        raise HTTPException(status_code=404, detail='Report not found')
    body = build_report_pdf(report)
    filename = f'ip-report-{job_id}.pdf'
    return Response(content=body, media_type='application/pdf', headers={'content-disposition': f'attachment; filename="{filename}"'})
