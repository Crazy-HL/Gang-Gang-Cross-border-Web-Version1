import unittest
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import hash_password, verify_password
from app.db.base import Base, User
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


if __name__ == '__main__':
    unittest.main()
