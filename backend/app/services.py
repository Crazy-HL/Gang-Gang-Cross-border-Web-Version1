from datetime import datetime
import re

from app.mock_data import admin_stats, categories, markets, mock_jobs, mock_reports
from app.models import DetectionFormInput


def get_risk_level_by_score(score: int):
    if score >= 75:
        return 'high'
    if score >= 45:
        return 'medium'
    return 'low'


def get_options():
    return {'categories': categories, 'markets': markets}


def create_job(input_data: DetectionFormInput):
    safe_brand = re.sub(r'[^a-z0-9]+', '-', input_data.brand.strip().lower())
    safe_brand = safe_brand.strip('-')
    return {'jobId': f"mock-{safe_brand or 'draft'}", 'input': input_data.model_dump()}


def upload_job_file(job_id: str, filename: str):
    return {'jobId': job_id, 'fileUrl': f'/uploads/{filename}'}


def run_job(job_id: str):
    return {'jobId': job_id, 'status': 'queued'}


def get_jobs():
    return mock_jobs


def get_reports():
    return mock_reports


def get_job_results(job_id: str):
    report = next((item for item in mock_reports if item['jobId'] == job_id), None)
    if report:
        return report
    if job_id.startswith('mock-'):
        return build_mock_report(job_id)
    return None


def get_report(report_id: str):
    report = next((item for item in mock_reports if item['jobId'] == report_id or item['id'] == report_id), None)
    if report:
        return report
    if report_id.startswith('mock-'):
        return build_mock_report(report_id)
    return None


def send_code(mobile: str):
    return {'ok': bool(re.fullmatch(r'1\d{10}', mobile))}


def login_with_code(mobile: str, code: str):
    return {'token': f'mock-token-{mobile}', 'user': {'id': 1, 'name': '张三'}, 'ok': len(code) >= 4}


def register_with_code(mobile: str, code: str):
    return {'ok': bool(re.fullmatch(r'1\d{10}', mobile)) and len(code) >= 4}


def get_admin_jobs():
    return {'stats': admin_stats, 'jobs': mock_jobs}


def build_mock_report(job_id: str):
    score = 62
    brand = re.sub(r'-+', ' ', re.sub(r'^mock-', '', job_id)).upper() or 'DRAFT BRAND'
    return {
        'id': f'r-{job_id}',
        'jobId': job_id,
        'title': f'{brand} 知识产权风险预检报告',
        'generatedAt': datetime.now().isoformat(timespec='minutes').replace('T', ' '),
        'riskLevel': get_risk_level_by_score(score),
        'riskScore': score,
        'summary': '这是基于 FastAPI 后端 mock 服务生成的预检报告，用于演示提交后的任务流转。真实结果需要接入后端检测服务后返回。',
        'categoryScores': [
            {'type': 'trademark', 'label': '商标', 'score': 64, 'hits': 1},
            {'type': 'design', 'label': '外观', 'score': 58, 'hits': 1},
            {'type': 'copyright', 'label': '版权', 'score': 45, 'hits': 0},
        ],
        'evidence': [
            {'id': f'ev-{job_id}', 'category': 'trademark', 'matched': brand, 'source': 'Mock IP Index', 'similarity': 0.64, 'description': '本地演示任务命中一条中等相似度商标线索，建议接入真实接口后重新检测。', 'imageUrl': '/evidence/activewear.svg'},
        ],
        'suggestions': ['接入真实后端后重新运行检测。', '保留商品图片、链接和品牌使用证据。', '中高风险任务提交人工复核。'],
    }
