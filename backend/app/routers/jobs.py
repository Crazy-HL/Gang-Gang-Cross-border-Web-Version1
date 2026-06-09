from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app import services
from app.models import DetectionFormInput

router = APIRouter(prefix='/api/jobs', tags=['jobs'])


@router.get('')
def read_jobs():
    return services.get_jobs()


@router.post('')
def create_job(payload: DetectionFormInput):
    return services.create_job(payload)


@router.post('/{job_id}/upload')
async def upload_job_file(job_id: str, file: UploadFile = File(...)):
    return services.upload_job_file(job_id, file.filename or 'upload.bin')


@router.post('/{job_id}/run')
def run_job(job_id: str):
    return services.run_job(job_id)


@router.get('/{job_id}/results')
def read_job_results(job_id: str):
    report = services.get_job_results(job_id)
    if not report:
        raise HTTPException(status_code=404, detail='Report not found')
    return report


@router.get('/{job_id}/report/pdf')
def download_report_pdf(job_id: str):
    body = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 76 >>
stream
BT /F1 16 Tf 72 720 Td (Gang Gang Cross-border IP Report {job_id}) Tj ET
endstream
endobj
trailer
<< /Root 1 0 R /Size 5 >>
%%EOF"""
    return Response(content=body, media_type='application/pdf', headers={'content-disposition': f'attachment; filename="ip-report-{job_id}.pdf"'})
