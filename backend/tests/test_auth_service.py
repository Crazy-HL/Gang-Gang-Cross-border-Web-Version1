import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import hash_password, verify_password
from app.db.base import Base, LoginRecord, User
from app.repositories.verification_code_repository import create_verification_code
from app.services import auth_service


class AuthServiceAccountRuleTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db: Session = self.SessionLocal()
        self.admin = User(
            mobile='admin',
            name='Admin',
            password_hash=hash_password('ggkj123'),
            role='admin',
        )
        self.user = User(
            mobile='13800138000',
            name='普通用户',
            password_hash=hash_password('user123'),
            role='user',
        )
        self.staff = User(
            mobile='staff',
            name='Staff',
            password_hash=hash_password('staff123'),
            role='user',
        )
        self.db.add_all([self.admin, self.user, self.staff])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def _create_code(self, account: str, code: str = '123456'):
        create_verification_code(
            self.db,
            account,
            code,
            datetime.now(timezone.utc) + timedelta(minutes=5),
        )

    def test_admin_can_use_password_login(self):
        result = auth_service.login_with_password(self.db, 'admin', 'ggkj123')

        self.assertTrue(result['ok'])
        self.assertEqual(result['user']['mobile'], 'admin')
        self.assertEqual(result['user']['role'], 'admin')

    def test_password_login_rejects_other_non_phone_accounts(self):
        result = auth_service.login_with_password(self.db, 'staff', 'staff123')

        self.assertFalse(result['ok'])
        self.assertEqual(result['token'], '')
        self.assertIsNone(result['user'])

    def test_password_login_prompts_code_login_when_password_missing(self):
        self.user.password_hash = ''
        self.db.commit()

        result = auth_service.login_with_password(self.db, '13800138000', 'anything')

        self.assertFalse(result['ok'])
        self.assertEqual(result['reason'], 'password_not_set')

    def test_send_code_requires_phone_number(self):
        result = auth_service.send_code(self.db, 'admin')

        self.assertFalse(result['ok'])
        self.assertIsNone(result['debugCode'])

    def test_admin_cannot_use_code_login_even_with_valid_code(self):
        self._create_code('admin')

        result = auth_service.login_with_code(self.db, 'admin', '123456')

        self.assertFalse(result['ok'])
        self.assertEqual(result['token'], '')
        self.assertIsNone(result['user'])

    def test_register_requires_phone_number_and_preserves_admin_password(self):
        self._create_code('admin')

        result = auth_service.register_with_code(self.db, 'admin', '123456', 'changed123')

        self.assertFalse(result['ok'])
        self.assertIsNone(result['userId'])
        self.db.refresh(self.admin)
        self.assertTrue(verify_password('ggkj123', self.admin.password_hash))

    def test_register_existing_user_without_password_prompts_code_login(self):
        self.user.password_hash = ''
        self.db.commit()
        self._create_code('13800138000')

        result = auth_service.register_with_code(self.db, '13800138000', '123456', 'newpass123')

        self.assertFalse(result['ok'])
        self.assertEqual(result['reason'], 'password_not_set')
        self.assertEqual(result['token'], '')
        self.db.refresh(self.user)
        self.assertEqual(self.user.password_hash, '')

    def test_register_existing_user_with_password_is_rejected(self):
        self._create_code('13800138000')

        result = auth_service.register_with_code(self.db, '13800138000', '123456', 'newpass123')

        self.assertFalse(result['ok'])
        self.assertEqual(result['reason'], 'already_registered')
        self.db.refresh(self.user)
        self.assertTrue(verify_password('user123', self.user.password_hash))

    def test_set_password_updates_logged_in_user_password(self):
        self.user.password_hash = ''
        self.db.commit()

        result = auth_service.set_password(self.db, self.user, 'newpass123')

        self.assertTrue(result['ok'])
        self.db.refresh(self.user)
        self.assertTrue(verify_password('newpass123', self.user.password_hash))

    def test_wechat_phone_login_creates_user_and_token(self):
        original_fetcher = auth_service.fetch_wechat_phone_number
        auth_service.fetch_wechat_phone_number = lambda phone_code: '13900139000'
        try:
            result = auth_service.login_with_wechat_phone(
                self.db,
                'phone-code',
                'wx-login-code',
                '127.0.0.1',
                'UnitTest/1.0',
            )
        finally:
            auth_service.fetch_wechat_phone_number = original_fetcher

        self.assertTrue(result['ok'])
        self.assertTrue(result['token'])
        self.assertEqual(result['user']['mobile'], '13900139000')
        self.assertEqual(result['user']['role'], 'user')
        self.assertEqual(result['user']['name'], '用户9000')

        record = self.db.execute(select(LoginRecord).where(LoginRecord.user_id == result['user']['id'])).scalar_one()
        self.assertEqual(record.login_method, 'wechat_phone')
        self.assertEqual(record.ip_address, '127.0.0.1')
        self.assertEqual(record.user_agent, 'UnitTest/1.0')

    def test_wechat_phone_login_reuses_existing_user(self):
        original_fetcher = auth_service.fetch_wechat_phone_number
        auth_service.fetch_wechat_phone_number = lambda phone_code: '13800138000'
        try:
            result = auth_service.login_with_wechat_phone(self.db, 'phone-code', '')
        finally:
            auth_service.fetch_wechat_phone_number = original_fetcher

        self.assertTrue(result['ok'])
        self.assertEqual(result['user']['id'], self.user.id)
        self.assertEqual(result['user']['mobile'], self.user.mobile)

    def test_code_login_requires_password_setup_when_user_has_no_password(self):
        self.user.password_hash = ''
        self.db.commit()
        self._create_code('13800138000')

        result = auth_service.login_with_code(self.db, '13800138000', '123456')

        self.assertTrue(result['ok'])
        self.assertTrue(result['needsPasswordSetup'])

    def test_code_login_skips_password_setup_when_user_has_password(self):
        self._create_code('13800138000')

        result = auth_service.login_with_code(self.db, '13800138000', '123456')

        self.assertTrue(result['ok'])
        self.assertFalse(result['needsPasswordSetup'])

    def test_wechat_phone_login_stores_mini_openid_and_unionid(self):
        original_phone_fetcher = auth_service.fetch_wechat_phone_number
        original_session_fetcher = auth_service.fetch_wechat_mini_session
        auth_service.fetch_wechat_phone_number = lambda phone_code: '13800138000'
        auth_service.fetch_wechat_mini_session = lambda login_code: {
            'openid': 'mini-openid-001',
            'unionid': 'unionid-001',
        }
        try:
            result = auth_service.login_with_wechat_phone(self.db, 'phone-code', 'login-code')
        finally:
            auth_service.fetch_wechat_phone_number = original_phone_fetcher
            auth_service.fetch_wechat_mini_session = original_session_fetcher

        self.assertTrue(result['ok'])
        self.db.refresh(self.user)
        self.assertEqual(self.user.wechat_mini_openid, 'mini-openid-001')
        self.assertEqual(self.user.wechat_unionid, 'unionid-001')

    def test_wechat_web_login_reuses_mini_user_by_unionid(self):
        self.user.wechat_unionid = 'unionid-001'
        self.user.wechat_mini_openid = 'mini-openid-001'
        self.db.commit()
        original_fetcher = auth_service.fetch_wechat_web_user
        auth_service.fetch_wechat_web_user = lambda code: {
            'openid': 'web-openid-001',
            'unionid': 'unionid-001',
            'nickname': '网页微信用户',
            'headimgurl': 'https://example.com/avatar.jpg',
        }
        try:
            result = auth_service.login_with_wechat_web(self.db, 'web-code', '127.0.0.1', 'UnitTest/1.0')
        finally:
            auth_service.fetch_wechat_web_user = original_fetcher

        self.assertTrue(result['ok'])
        self.assertEqual(result['user']['id'], self.user.id)
        self.assertEqual(result['user']['mobile'], '13800138000')
        self.db.refresh(self.user)
        self.assertEqual(self.user.wechat_web_openid, 'web-openid-001')
        self.assertEqual(self.user.name, '网页微信用户')
        self.assertEqual(self.user.avatar_url, 'https://example.com/avatar.jpg')

        record = self.db.execute(select(LoginRecord).where(LoginRecord.user_id == self.user.id).order_by(LoginRecord.id.desc())).scalars().first()
        self.assertEqual(record.login_method, 'wechat_web')
        self.assertEqual(record.ip_address, '127.0.0.1')

    def test_wechat_web_login_creates_web_user_without_unionid_match(self):
        original_fetcher = auth_service.fetch_wechat_web_user
        auth_service.fetch_wechat_web_user = lambda code: {
            'openid': 'web-openid-002',
            'unionid': '',
            'nickname': '扫码用户',
            'headimgurl': 'https://example.com/web-avatar.jpg',
        }
        try:
            result = auth_service.login_with_wechat_web(self.db, 'web-code')
        finally:
            auth_service.fetch_wechat_web_user = original_fetcher

        self.assertTrue(result['ok'])
        self.assertTrue(result['user']['mobile'].startswith('wx_web_'))
        self.assertEqual(result['user']['name'], '扫码用户')

    def test_build_wechat_web_login_url_uses_qrconnect(self):
        original_appid = auth_service.settings.wechat_web_appid
        auth_service.settings.wechat_web_appid = 'web-appid'
        try:
            url = auth_service.build_wechat_web_login_url('https://example.com/auth?wechat=1', 'state-001')
        finally:
            auth_service.settings.wechat_web_appid = original_appid

        self.assertIn('https://open.weixin.qq.com/connect/qrconnect', url)
        self.assertIn('appid=web-appid', url)
        self.assertIn('scope=snsapi_login', url)
        self.assertIn('state=state-001', url)
        self.assertIn('redirect_uri=https%3A%2F%2Fexample.com%2Fauth%3Fwechat%3D1', url)

    def test_wechat_phone_login_rejects_invalid_phone_code(self):
        original_fetcher = auth_service.fetch_wechat_phone_number
        auth_service.fetch_wechat_phone_number = lambda phone_code: ''
        try:
            result = auth_service.login_with_wechat_phone(self.db, 'bad-code', '')
        finally:
            auth_service.fetch_wechat_phone_number = original_fetcher

        self.assertFalse(result['ok'])
        self.assertEqual(result['token'], '')
        self.assertIsNone(result['user'])

    def test_get_me_includes_wechat_avatar_url(self):
        self.user.avatar_url = '/uploads/avatars/user-1.png'

        payload = auth_service.get_me(self.user, self.db)

        self.assertEqual(payload['avatarUrl'], '/uploads/avatars/user-1.png')

    def test_update_profile_persists_wechat_name_and_avatar(self):
        result = auth_service.update_profile(
            self.db,
            self.user,
            '微信昵称',
            '/uploads/avatars/user-1.png',
        )

        self.assertEqual(result['name'], '微信昵称')
        self.assertEqual(result['avatarUrl'], '/uploads/avatars/user-1.png')
        self.db.refresh(self.user)
        self.assertEqual(self.user.name, '微信昵称')
        self.assertEqual(self.user.avatar_url, '/uploads/avatars/user-1.png')

    def test_save_profile_avatar_persists_file_and_user_url(self):
        original_root = auth_service.AVATAR_UPLOAD_ROOT
        with TemporaryDirectory() as tmp_dir:
            auth_service.AVATAR_UPLOAD_ROOT = Path(tmp_dir)
            try:
                result = auth_service.save_profile_avatar(
                    self.db,
                    self.user,
                    'avatar.png',
                    'image/png',
                    b'avatar-bytes',
                )
            finally:
                auth_service.AVATAR_UPLOAD_ROOT = original_root

            self.assertTrue(result['avatarUrl'].startswith('/uploads/avatars/'))
            stored_file = Path(tmp_dir) / result['avatarUrl'].rsplit('/', 1)[-1]
            self.assertEqual(stored_file.read_bytes(), b'avatar-bytes')
            self.db.refresh(self.user)
            self.assertEqual(self.user.avatar_url, result['avatarUrl'])


if __name__ == '__main__':
    unittest.main()
