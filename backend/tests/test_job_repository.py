import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base, Job, User
from app.repositories import job_repository


class JobRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db: Session = self.SessionLocal()
        self.user = User(mobile='13800138000', name='普通用户', password_hash='x', role='user')
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_job_dict_includes_owner_mobile(self):
        job = Job(
            id='JOB-MOBILE-1',
            owner_id=self.user.id,
            type='trademark',
            title='测试商品',
            brand='测试品牌',
            category='家居',
            market='amazon',
            status='done',
            risk_level='medium',
            risk_score=60,
        )
        self.db.add(job)
        self.db.commit()

        row = job_repository.list_jobs(self.db, owner_id=self.user.id)[0]

        self.assertEqual(row['ownerMobile'], '13800138000')


if __name__ == '__main__':
    unittest.main()
