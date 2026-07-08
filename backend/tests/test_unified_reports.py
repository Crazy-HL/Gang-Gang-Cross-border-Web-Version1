import json
import unittest
from datetime import datetime
from types import SimpleNamespace

from app.services import report_service


def make_service_request(request_id: str, request_type: str, details: dict):
    return SimpleNamespace(
        id=request_id,
        request_type=request_type,
        title='测试服务报告',
        created_at=datetime(2026, 7, 8, 10, 30, 0),
        details_json=json.dumps(details, ensure_ascii=False),
    )


class UnifiedReportTests(unittest.TestCase):
    def test_service_request_report_maps_to_unified_report(self):
        model_report = {
            'title': '亚马逊申诉建议报告',
            'summary': '港港跨境AI 已生成申诉建议。',
            'riskLevel': 'medium',
            'sections': [{'title': '申诉重点', 'items': ['补充平台通知']}],
            'nextActions': ['整理通知截图'],
            'contactHint': '联系港港跨境',
            'source': 'model',
        }
        item = make_service_request('APL-1', 'appeal', {'adviceReport': model_report})

        report = report_service.service_request_report_to_dict(item)

        self.assertEqual(report['id'], 'APL-1')
        self.assertEqual(report['reportType'], 'appeal')
        self.assertEqual(report['typeLabel'], '平台申诉')
        self.assertEqual(report['sourceLabel'], '港港跨境AI')
        self.assertEqual(report['sections'], model_report['sections'])
        self.assertEqual(report['nextActions'], model_report['nextActions'])

    def test_fallback_source_label_is_ganggang_basic_assessment(self):
        fallback_report = {
            'title': 'TRO 初步评估报告',
            'summary': '基础评估。',
            'riskLevel': 'high',
            'sections': [{'title': '当前风险', 'items': ['资金已冻结']}],
            'nextActions': ['整理案件号'],
            'source': 'fallback',
        }
        item = make_service_request('TRO-1', 'tro_settlement', {'adviceReport': fallback_report})

        report = report_service.service_request_report_to_dict(item)

        self.assertEqual(report['reportType'], 'tro_settlement')
        self.assertEqual(report['typeLabel'], 'TRO 和解')
        self.assertEqual(report['sourceLabel'], '港港跨境基础评估')

    def test_service_request_without_advice_report_is_skipped(self):
        item = make_service_request('APL-2', 'appeal', {})

        self.assertIsNone(report_service.service_request_report_to_dict(item))


if __name__ == '__main__':
    unittest.main()
