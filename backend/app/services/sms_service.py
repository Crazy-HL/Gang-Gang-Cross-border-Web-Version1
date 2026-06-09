import json

from alibabacloud_dysmsapi20170525.client import Client as DysmsapiClient
from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

from app.core.config import get_settings

settings = get_settings()


def _create_client() -> DysmsapiClient:
    config = open_api_models.Config(
        access_key_id=settings.alibaba_cloud_access_key_id,
        access_key_secret=settings.alibaba_cloud_access_key_secret,
    )
    config.endpoint = settings.sms_endpoint
    return DysmsapiClient(config)


def send_verification_sms(mobile: str, code: str) -> None:
    client = _create_client()
    request = dysmsapi_models.SendSmsRequest(
        phone_numbers=mobile,
        sign_name=settings.sms_sign_name,
        template_code=settings.sms_template_code,
        template_param=json.dumps({'code': code}, ensure_ascii=False),
    )
    try:
        response = client.send_sms_with_options(request, util_models.RuntimeOptions())
        print('[sms] aliyun response:', json.dumps(response.to_map(), ensure_ascii=False, default=str))
    except Exception as error:
        print('[sms] aliyun error:', getattr(error, 'message', str(error)))
        error_data = getattr(error, 'data', None)
        if error_data:
            print('[sms] aliyun error data:', json.dumps(error_data, ensure_ascii=False, default=str))
        raise
