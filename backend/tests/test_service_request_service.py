import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.models import ServiceRequestCreate
from app.services import service_request_service


def _payload():
    return ServiceRequestCreate(
        requestType='appeal',
        platform='亚马逊',
        contact='13800138000',
        issueType='商品下架',
        storeName='测试店铺',
        reference='ASIN-TEST-001',
        description='收到商品下架通知，疑似图片版权投诉。',
        fileNames=['notice.png'],
    )


class _Response:
    def __init__(self, body):
        self._body = body
        self.text = json.dumps(body, ensure_ascii=False)

    def raise_for_status(self):
        return None

    def json(self):
        return self._body


class ServiceRequestModelTests(unittest.TestCase):
    def test_model_report_falls_back_to_openai_compatible_route_for_existing_model_config(self):
        config = SimpleNamespace(
            provider='anthropic',
            model_name='claude-3-5-sonnet-latest',
            api_key='sk-test',
            base_url='https://api.example.test/v1',
            temperature=0.2,
            max_tokens=2048,
            enabled=True,
        )
        calls = []

        class Client:
            def __init__(self, timeout):
                self.timeout = timeout

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def post(self, url, headers, **kwargs):
                calls.append(url)
                if url.endswith('/messages'):
                    raise RuntimeError('anthropic route unavailable')
                return _Response({
                    'choices': [{
                        'message': {
                            'content': json.dumps({
                                'title': 'AI 申诉建议',
                                'summary': '模型已根据 ASIN-TEST-001 生成建议。',
                                'riskLevel': 'medium',
                                'sections': [{'title': '申诉重点', 'items': ['补充平台通知。', '说明图片来源。']}],
                                'nextActions': ['整理通知截图。'],
                                'contactHint': '如需人工申诉/和解协助，可联系港港跨境，并保留工单号。',
                            }, ensure_ascii=False)
                        }
                    }]
                })

        with patch.object(service_request_service.model_config_repository, 'get_model_config', return_value=config), patch.object(service_request_service.httpx, 'Client', Client):
            report = service_request_service._model_report(object(), _payload(), 'APL-TEST')

        self.assertEqual(calls, ['https://api.example.test/v1/messages', 'https://api.example.test/v1/chat/completions'])
        self.assertEqual(report['source'], 'model')
        self.assertEqual(report['title'], 'AI 申诉建议')

    def test_siliconflow_deepseek_config_uses_openai_compatible_route_first(self):
        config = SimpleNamespace(
            provider='anthropic',
            model_name='deepseek-ai/DeepSeek-R1',
            api_key='sk-test',
            base_url='https://api.siliconflow.cn/v1',
            temperature=0.2,
            max_tokens=2048,
            enabled=True,
        )

        self.assertEqual(service_request_service._preferred_provider_order(config)[0], 'openai')

    def test_service_prompt_brands_identity_as_ganggang_ai(self):
        prompt = service_request_service._format_prompt(_payload(), 'APL-TEST')

        self.assertIn('港港跨境AI', prompt)
        self.assertIn('你是什么模型', prompt)

    def test_custom_codex_config_uses_responses_api_payload(self):
        config = SimpleNamespace(
            provider='custom',
            model_name='gpt-5.5',
            api_key='sk-test',
            base_url='https://newapi.example.test/v1',
            temperature=0.2,
            max_tokens=2048,
            enabled=True,
        )
        calls = []

        class Client:
            def __init__(self, timeout):
                self.timeout = timeout

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def post(self, url, headers, **kwargs):
                calls.append({'url': url, 'headers': headers, 'json': kwargs['json']})
                return _Response({
                    'output_text': json.dumps({
                        'title': 'Responses API 申诉建议',
                        'summary': '模型已按 Responses API 生成建议。',
                        'riskLevel': 'medium',
                        'sections': [{'title': '申诉重点', 'items': ['补充平台通知。']}],
                        'nextActions': ['整理通知截图。'],
                        'contactHint': '如需人工申诉/和解协助，可联系港港跨境，并保留工单号。',
                    }, ensure_ascii=False)
                })

        with patch.object(service_request_service.model_config_repository, 'get_model_config', return_value=config), patch.object(service_request_service.httpx, 'Client', Client):
            report = service_request_service._model_report(object(), _payload(), 'APL-TEST')

        self.assertEqual(calls[0]['url'], 'https://newapi.example.test/v1/responses')
        self.assertEqual(calls[0]['headers']['authorization'], 'Bearer sk-test')
        self.assertEqual(calls[0]['json']['model'], 'gpt-5.5')
        self.assertEqual(calls[0]['json']['reasoning'], {'effort': 'high'})
        self.assertEqual(calls[0]['json']['store'], False)
        self.assertIn('input', calls[0]['json'])
        self.assertEqual(report['source'], 'model')
        self.assertEqual(report['title'], 'Responses API 申诉建议')

    def test_fallback_report_marks_source(self):
        report = service_request_service._fallback_report(_payload(), 'APL-TEST')

        self.assertEqual(report['source'], 'fallback')


if __name__ == '__main__':
    unittest.main()
