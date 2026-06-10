import re
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.base import Job
from app.repositories import job_repository

ALLOWED_CONTENT_TYPES = {'image/jpeg': '.jpg', 'image/png': '.png'}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
UPLOAD_ROOT = Path(__file__).resolve().parents[2] / 'uploads'


def _safe_filename(filename: str) -> str:
    name = filename.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
    name = re.sub(r'[^A-Za-z0-9._-]+', '-', name).strip('.-')
    return name or 'upload.bin'


def _stored_filename(filename: str, content_type: str) -> str:
    safe_name = _safe_filename(filename)
    stem = safe_name.rsplit('.', 1)[0] or 'upload'
    suffix = ALLOWED_CONTENT_TYPES[content_type]
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return f'{timestamp}-{stem}{suffix}'


async def attach_upload(db: Session, job: Job, upload_file: UploadFile):
    if upload_file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail='Unsupported file type')
    content = await upload_file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail='File too large')
    if not content:
        raise HTTPException(status_code=400, detail='Empty file')

    stored_filename = _stored_filename(upload_file.filename or 'upload', upload_file.content_type)
    job_dir = UPLOAD_ROOT / job.id
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / stored_filename).write_bytes(content)

    file = job_repository.create_job_file(
        db,
        job_id=job.id,
        filename=stored_filename,
        content_type=upload_file.content_type,
        size=len(content),
        file_url=f'/uploads/{job.id}/{stored_filename}',
    )
    return {'jobId': job.id, 'fileUrl': file.file_url}
