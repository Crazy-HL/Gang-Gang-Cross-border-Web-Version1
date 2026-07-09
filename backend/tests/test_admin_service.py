import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import AdminAccount, Base, Job, Notification, Report, ServiceRequest, User
from app.services import admin_service, auth_service, report_service


class AdminServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db: Session = self.SessionLocal()
        self.admin = User(mobile='18182363760', name='管理员', password_hash='x', role='admin')
        self.normal = User(mobile='13800138000', name='普通用户', password_hash='x', role='user')
        self.db.add_all([self.admin, self.normal])
        self.db.commit()
        self.db.refresh(self.admin)
        self.db.refresh(self.normal)
        self.job = Job(
            id='JOB-ADMIN-1',
            owner_id=self.normal.id,
            type='copyright',
            title='测试商品',
            brand='测试品牌',
            category='家居',
            market='amazon',
            status='done',
            risk_level='high',
            risk_score=88,
            review_status='pending',
        )
        self.report = Report(
            id='RPT-ADMIN-1',
            job_id='JOB-ADMIN-1',
            title='侵权检测报告',
            risk_level='high',
            risk_score=88,
            summary='测试摘要',
            suggestions_json=json.dumps(['联系港港跨境'], ensure_ascii=False),
        )
        self.service_request = ServiceRequest(
            id='APL-ADMIN-1',
            owner_id=self.normal.id,
            request_type='appeal',
            title='亚马逊申诉',
            platform='亚马逊',
            status='pending',
            contact='13800138000',
            reference='ASIN-TEST',
            description='测试服务需求',
            details_json=json.dumps({
                'adviceReport': {
                    'title': '申诉建议报告',
                    'summary': '建议先补充授权材料',
                    'riskLevel': 'medium',
                    'sections': [{'title': '优先动作', 'items': ['准备发票']}],
                    'nextActions': ['联系平台客服'],
                    'source': 'model',
                }
            }, ensure_ascii=False),
        )
        self.tro_service_request = ServiceRequest(
            id='TRO-ADMIN-1',
            owner_id=self.normal.id,
            request_type='tro_settlement',
            title='TRO 和解咨询',
            platform='Shopify',
            status='processing',
            contact='13800138000',
            reference='CASE-TEST',
            description='测试 TRO 服务需求',
            details_json=json.dumps({
                'adviceReport': {
                    'title': 'TRO 和解建议报告',
                    'summary': '建议先核对冻结金额',
                    'riskLevel': 'low',
                    'sections': [{'title': '基础核查', 'items': ['确认案号']}],
                    'nextActions': ['准备和解预算'],
                    'source': 'fallback',
                }
            }, ensure_ascii=False),
        )
        self.notification = Notification(
            user_id=self.normal.id,
            title='报告已生成',
            content='港港跨境AI 已生成报告',
            type='report',
            is_read=False,
        )
        self.db.add_all([self.job, self.report, self.service_request, self.tro_service_request, self.notification])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_normal_user_cannot_read_admin_overview(self):
        with self.assertRaises(Exception) as ctx:
            admin_service.get_admin_overview(self.db, self.normal)

        self.assertEqual(ctx.exception.status_code, 403)

    def test_active_admin_table_record_grants_admin_access(self):
        self.normal.role = 'user'
        self.db.add(AdminAccount(user_id=self.normal.id, enabled=True))
        self.db.commit()

        overview = admin_service.get_admin_overview(self.db, self.normal)
        users = admin_service.get_admin_users(self.db, self.normal)
        user_row = next(row for row in users if row['id'] == self.normal.id)

        self.assertEqual(overview['totalUsers'], 2)
        self.assertEqual(user_row['role'], 'admin')

    def test_active_admin_table_record_returns_admin_role_to_frontend(self):
        self.normal.role = 'user'
        self.db.add(AdminAccount(user_id=self.normal.id, enabled=True))
        self.db.commit()

        payload = auth_service.get_me(self.normal, self.db)

        self.assertEqual(payload['role'], 'admin')

    def test_admin_overview_counts_core_tables(self):
        overview = admin_service.get_admin_overview(self.db, self.admin)

        self.assertEqual(overview['totalUsers'], 2)
        self.assertEqual(overview['totalJobs'], 1)
        self.assertEqual(overview['totalReports'], 3)
        self.assertEqual(overview['totalServiceRequests'], 2)
        self.assertEqual(overview['unreadNotifications'], 1)
        self.assertEqual(overview['pendingReviews'], 1)

    def test_admin_can_read_other_users_ip_report(self):
        report = report_service.get_user_report(self.db, self.report.id, self.admin)

        self.assertIsNotNone(report)
        self.assertEqual(report['id'], 'RPT-ADMIN-1')
        self.assertEqual(report['title'], '侵权检测报告')
        self.assertEqual(report['reportType'], 'ip_detection')

    def test_admin_can_read_other_users_service_advice_report(self):
        report = report_service.get_user_report(self.db, self.service_request.id, self.admin)

        self.assertIsNotNone(report)
        self.assertEqual(report['id'], 'APL-ADMIN-1')
        self.assertEqual(report['title'], '申诉建议报告')
        self.assertEqual(report['reportType'], 'appeal')
        self.assertEqual(report['typeLabel'], '平台申诉')

    def test_admin_lists_include_owner_labels_and_service_advice_rows(self):
        users = admin_service.get_admin_users(self.db, self.admin)
        reports = admin_service.get_admin_reports(self.db, self.admin)
        service_requests = admin_service.get_admin_service_requests(self.db, self.admin)
        notifications = admin_service.get_admin_notifications(self.db, self.admin)

        admin_row = next(row for row in users if row['mobile'] == '18182363760')
        ip_row = next(row for row in reports if row['id'] == 'RPT-ADMIN-1')
        appeal_row = next(row for row in reports if row['id'] == 'APL-ADMIN-1')
        tro_row = next(row for row in reports if row['id'] == 'TRO-ADMIN-1')
        appeal_request_row = next(row for row in service_requests if row['id'] == 'APL-ADMIN-1')

        self.assertEqual(admin_row['role'], 'admin')
        normal_row = next(row for row in users if row['mobile'] == '13800138000')
        self.assertEqual(normal_row['reportCount'], 1)
        self.assertEqual(normal_row['loginCount'], 0)
        self.assertEqual(normal_row['lastLoginAt'], '')
        self.assertEqual(ip_row['ownerName'], '普通用户')
        self.assertEqual(ip_row['reportType'], 'ip_detection')
        self.assertEqual(ip_row['typeLabel'], '侵权检测')
        self.assertEqual(ip_row['linkId'], 'RPT-ADMIN-1')
        self.assertEqual(appeal_row['reportType'], 'appeal')
        self.assertEqual(appeal_row['typeLabel'], '平台申诉')
        self.assertEqual(appeal_row['riskLevel'], 'medium')
        self.assertIsNone(appeal_row['riskScore'])
        self.assertEqual(appeal_row['ownerMobile'], '13800138000')
        self.assertEqual(appeal_row['linkId'], 'APL-ADMIN-1')
        self.assertEqual(tro_row['reportType'], 'tro_settlement')
        self.assertEqual(tro_row['typeLabel'], 'TRO 和解')
        self.assertEqual(tro_row['riskLevel'], 'low')
        self.assertEqual(tro_row['ownerName'], '普通用户')
        self.assertEqual(tro_row['linkId'], 'TRO-ADMIN-1')
        self.assertEqual(appeal_request_row['typeLabel'], '平台申诉')
        self.assertEqual(appeal_request_row['ownerMobile'], '13800138000')
        self.assertEqual(notifications[0]['ownerName'], '普通用户')

    def test_login_with_password_records_successful_login(self):
        self.normal.password_hash = auth_service.hash_password('secret123')
        self.db.commit()

        auth_service.login_with_password(self.db, self.normal.mobile, 'secret123', '127.0.0.1', 'UnitTest/1.0')
        records = admin_service.get_admin_login_records(self.db, self.admin)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['mobile'], '13800138000')
        self.assertEqual(records[0]['name'], '普通用户')
        self.assertEqual(records[0]['loginMethod'], 'password')
        self.assertEqual(records[0]['ipAddress'], '127.0.0.1')
        self.assertEqual(records[0]['userAgent'], 'UnitTest/1.0')
        self.assertTrue(records[0]['createdAt'])

    def test_normal_user_cannot_read_admin_login_records(self):
        with self.assertRaises(Exception) as ctx:
            admin_service.get_admin_login_records(self.db, self.normal)

        self.assertEqual(ctx.exception.status_code, 403)


if __name__ == '__main__':
    unittest.main()
