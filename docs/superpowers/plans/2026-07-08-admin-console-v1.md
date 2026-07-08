# Admin Console v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an admin-only operational console that shows core business tables and blocks normal users from seeing or accessing admin pages and APIs.

**Architecture:** Extend the existing FastAPI `/api/admin` module with admin-only read endpoints for overview, users, reports, service requests, and notifications. Update Vue routing and header navigation to enforce admin visibility, then replace the current small admin dashboard with a tabbed table console that consumes the new APIs while preserving job review and model config editing.

**Tech Stack:** FastAPI, SQLAlchemy, unittest, Vue 3, Vue Router, Vite, TypeScript, Tailwind CSS.

## Global Constraints

- 只有管理员账号可以看到“后台”导航入口。
- 普通用户手动访问 `/admin` 时不能进入后台。
- 后端所有管理员数据接口继续使用管理员权限校验。
- v1 不做数据删除功能。
- v1 不开放普通管理员直接修改用户角色。
- 与大模型相关的用户可见文案统一写为“港港跨境AI”。
- 前端隐藏入口只用于体验，真正权限必须以后端 403 为准。

---

## File Structure

- Modify `backend/app/repositories/admin_repository.py`: owns admin list queries and table row serialization.
- Modify `backend/app/services/admin_service.py`: applies `ensure_admin` and exposes admin service functions.
- Modify `backend/app/routers/admin.py`: registers new admin endpoints.
- Create `backend/tests/test_admin_service.py`: verifies admin access control and list response shapes with an in-memory SQLite database.
- Modify `frontend/src/types/domain.ts`: adds admin row and response types.
- Modify `frontend/src/api/client.ts`: adds API client functions for new admin endpoints.
- Modify `frontend/src/router.ts`: adds `requiresAdmin` route metadata and redirect behavior.
- Modify `frontend/src/components/site/SiteHeader.vue`: filters the admin navigation item by role.
- Modify `frontend/src/views/AdminView.vue`: loads admin data and renders console states.
- Modify `frontend/src/components/admin/AdminDashboard.vue`: becomes a tabbed operational console.
- Modify `frontend/src/components/admin/AdminTaskTable.vue`: keeps review behavior and fits the new dashboard layout.

---

### Task 1: Backend Admin Tables API

**Files:**
- Modify: `backend/app/repositories/admin_repository.py`
- Modify: `backend/app/services/admin_service.py`
- Modify: `backend/app/routers/admin.py`
- Create: `backend/tests/test_admin_service.py`

**Interfaces:**
- Consumes: SQLAlchemy models `User`, `Job`, `Report`, `ServiceRequest`, `Notification`.
- Produces:
  - `admin_repository.get_admin_overview(db: Session) -> dict`
  - `admin_repository.list_admin_users(db: Session, limit: int = 100) -> list[dict]`
  - `admin_repository.list_admin_reports(db: Session, limit: int = 100) -> list[dict]`
  - `admin_repository.list_admin_service_requests(db: Session, limit: int = 100) -> list[dict]`
  - `admin_repository.list_admin_notifications(db: Session, limit: int = 100) -> list[dict]`
  - `admin_service.get_admin_overview(db: Session, user: User) -> dict`
  - `admin_service.get_admin_users(db: Session, user: User) -> list[dict]`
  - `admin_service.get_admin_reports(db: Session, user: User) -> list[dict]`
  - `admin_service.get_admin_service_requests(db: Session, user: User) -> list[dict]`
  - `admin_service.get_admin_notifications(db: Session, user: User) -> list[dict]`

- [ ] **Step 1: Write failing backend tests**

Create `backend/tests/test_admin_service.py`:

```python
import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base, Job, Notification, Report, ServiceRequest, User
from app.services import admin_service


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
            details_json=json.dumps({'adviceReport': {'title': '建议报告'}}, ensure_ascii=False),
        )
        self.notification = Notification(
            user_id=self.normal.id,
            title='报告已生成',
            content='港港跨境AI 已生成报告',
            type='report',
            is_read=False,
        )
        self.db.add_all([self.job, self.report, self.service_request, self.notification])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_normal_user_cannot_read_admin_overview(self):
        with self.assertRaises(Exception) as ctx:
            admin_service.get_admin_overview(self.db, self.normal)

        self.assertEqual(ctx.exception.status_code, 403)

    def test_admin_overview_counts_core_tables(self):
        overview = admin_service.get_admin_overview(self.db, self.admin)

        self.assertEqual(overview['totalUsers'], 2)
        self.assertEqual(overview['totalJobs'], 1)
        self.assertEqual(overview['totalReports'], 1)
        self.assertEqual(overview['totalServiceRequests'], 1)
        self.assertEqual(overview['unreadNotifications'], 1)
        self.assertEqual(overview['pendingReviews'], 1)

    def test_admin_lists_include_owner_and_labels(self):
        users = admin_service.get_admin_users(self.db, self.admin)
        reports = admin_service.get_admin_reports(self.db, self.admin)
        service_requests = admin_service.get_admin_service_requests(self.db, self.admin)
        notifications = admin_service.get_admin_notifications(self.db, self.admin)

        admin_row = next(row for row in users if row['mobile'] == '18182363760')
        self.assertEqual(admin_row['role'], 'admin')
        self.assertEqual(reports[0]['ownerName'], '普通用户')
        self.assertEqual(reports[0]['reportType'], 'ip_detection')
        self.assertEqual(reports[0]['typeLabel'], '侵权检测')
        self.assertEqual(service_requests[0]['typeLabel'], '平台申诉')
        self.assertEqual(service_requests[0]['ownerMobile'], '13800138000')
        self.assertEqual(notifications[0]['ownerName'], '普通用户')


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
backend/.venv/bin/python -m unittest backend.tests.test_admin_service -v
```

Expected: fail with missing functions such as `get_admin_overview`.

- [ ] **Step 3: Implement repository queries**

Update `backend/app/repositories/admin_repository.py` to import `Notification`, `Report`, `ServiceRequest`, `format_datetime`, and `selectinload`, then add:

```python
from app.db.base import Job, Notification, Report, ServiceRequest, User
from app.repositories.utils import format_datetime


def _type_label(value: str):
    return {
        'ip_detection': '侵权检测',
        'appeal': '平台申诉',
        'tro_settlement': 'TRO 和解',
    }.get(value, value)


def get_admin_overview(db: Session):
    total_jobs = db.scalar(select(func.count()).select_from(Job)) or 0
    total_users = db.scalar(select(func.count()).select_from(User)) or 0
    total_reports = db.scalar(select(func.count()).select_from(Report)) or 0
    total_service_requests = db.scalar(select(func.count()).select_from(ServiceRequest)) or 0
    unread_notifications = db.scalar(select(func.count()).select_from(Notification).where(Notification.is_read.is_(False))) or 0
    pending_reviews = db.scalar(select(func.count()).select_from(Job).where(Job.review_status == 'pending')) or 0
    completed_jobs = db.scalar(select(func.count()).select_from(Job).where(Job.status == 'done')) or 0
    high_risk_jobs = db.scalar(select(func.count()).select_from(Job).where(Job.risk_level == 'high')) or 0
    return {
        'totalJobs': total_jobs,
        'totalUsers': total_users,
        'completedJobs': completed_jobs,
        'highRiskRate': high_risk_jobs / total_jobs if total_jobs else 0,
        'totalReports': total_reports,
        'totalServiceRequests': total_service_requests,
        'unreadNotifications': unread_notifications,
        'pendingReviews': pending_reviews,
    }


def list_admin_users(db: Session, limit: int = 100):
    users = db.scalars(select(User).order_by(User.created_at.desc()).limit(limit)).all()
    rows = []
    for user in users:
        rows.append({
            'id': user.id,
            'mobile': user.mobile,
            'name': user.name,
            'role': user.role,
            'createdAt': format_datetime(user.created_at),
            'jobCount': len(user.jobs),
            'serviceRequestCount': len(user.service_requests),
        })
    return rows


def list_admin_reports(db: Session, limit: int = 100):
    query = (
        select(Report)
        .options(selectinload(Report.job).selectinload(Job.owner))
        .order_by(Report.generated_at.desc())
        .limit(limit)
    )
    rows = []
    for report in db.scalars(query).all():
        owner = report.job.owner if report.job else None
        rows.append({
            'id': report.id,
            'reportType': 'ip_detection',
            'typeLabel': _type_label('ip_detection'),
            'title': report.title,
            'ownerName': owner.name if owner else '未绑定用户',
            'ownerMobile': owner.mobile if owner else '',
            'riskLevel': report.risk_level,
            'riskScore': report.risk_score,
            'generatedAt': format_datetime(report.generated_at),
            'linkId': report.id,
        })
    return rows


def list_admin_service_requests(db: Session, limit: int = 100):
    query = (
        select(ServiceRequest)
        .options(selectinload(ServiceRequest.owner))
        .order_by(ServiceRequest.created_at.desc())
        .limit(limit)
    )
    rows = []
    for item in db.scalars(query).all():
        rows.append({
            'id': item.id,
            'requestType': item.request_type,
            'typeLabel': _type_label(item.request_type),
            'title': item.title,
            'platform': item.platform,
            'status': item.status,
            'contact': item.contact,
            'ownerName': item.owner.name if item.owner else '未绑定用户',
            'ownerMobile': item.owner.mobile if item.owner else '',
            'createdAt': format_datetime(item.created_at),
            'linkId': item.id,
        })
    return rows


def list_admin_notifications(db: Session, limit: int = 100):
    query = (
        select(Notification)
        .options(selectinload(Notification.user))
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    rows = []
    for item in db.scalars(query).all():
        rows.append({
            'id': item.id,
            'title': item.title,
            'content': item.content,
            'type': item.type,
            'isRead': item.is_read,
            'ownerName': item.user.name if item.user else '未绑定用户',
            'ownerMobile': item.user.mobile if item.user else '',
            'createdAt': format_datetime(item.created_at),
        })
    return rows
```

Also update `get_admin_stats` to return `get_admin_overview(db)` and `get_admin_jobs` to return `{'stats': get_admin_overview(db), 'jobs': list_jobs(db)}`.

- [ ] **Step 4: Implement service functions**

Add to `backend/app/services/admin_service.py`:

```python
def get_admin_overview(db: Session, user: User):
    ensure_admin(user)
    return admin_repository.get_admin_overview(db)


def get_admin_users(db: Session, user: User):
    ensure_admin(user)
    return admin_repository.list_admin_users(db)


def get_admin_reports(db: Session, user: User):
    ensure_admin(user)
    return admin_repository.list_admin_reports(db)


def get_admin_service_requests(db: Session, user: User):
    ensure_admin(user)
    return admin_repository.list_admin_service_requests(db)


def get_admin_notifications(db: Session, user: User):
    ensure_admin(user)
    return admin_repository.list_admin_notifications(db)
```

- [ ] **Step 5: Register routes**

Add to `backend/app/routers/admin.py`:

```python
@router.get('/overview')
def read_admin_overview(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_overview(db, user)


@router.get('/users')
def read_admin_users(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_users(db, user)


@router.get('/reports')
def read_admin_reports(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_reports(db, user)


@router.get('/service-requests')
def read_admin_service_requests(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_service_requests(db, user)


@router.get('/notifications')
def read_admin_notifications(db: DbSession, user: User = Depends(get_current_user)):
    return admin_service.get_admin_notifications(db, user)
```

- [ ] **Step 6: Run backend verification**

Run:

```bash
backend/.venv/bin/python -m unittest backend.tests.test_admin_service backend.tests.test_service_request_service backend.tests.test_unified_reports -v
backend/.venv/bin/python -m compileall backend/app
```

Expected: all tests pass and compileall reports no syntax errors.

- [ ] **Step 7: Commit backend API**

Run:

```bash
git add backend/app/repositories/admin_repository.py backend/app/services/admin_service.py backend/app/routers/admin.py backend/tests/test_admin_service.py
git commit -m "feat: add admin management table APIs"
```

---

### Task 2: Frontend Admin Access Control

**Files:**
- Modify: `frontend/src/router.ts`
- Modify: `frontend/src/components/site/SiteHeader.vue`

**Interfaces:**
- Consumes: `user` from `frontend/src/stores/auth.ts`, with `role: 'user' | 'admin'`.
- Produces: `/admin` route with `meta.requiresAuth = true` and `meta.requiresAdmin = true`; filtered navigation where `/admin` is visible only for admins.

- [ ] **Step 1: Add route guard behavior**

Update `frontend/src/router.ts` route metadata:

```ts
{ path: '/admin', component: AdminView, meta: { requiresAuth: true, requiresAdmin: true } }
```

Then replace the guard with:

```ts
router.beforeEach(async (to) => {
  if (to.path === '/auth' && isAuthenticated.value) return '/dashboard'
  if (!to.meta.requiresAuth) return true

  const currentUser = await loadCurrentUser()
  if (!currentUser) return `/auth?redirect=${encodeURIComponent(to.fullPath)}`
  if (to.meta.requiresAdmin && currentUser.role !== 'admin') return '/dashboard'

  return true
})
```

- [ ] **Step 2: Hide admin nav for normal users**

Update `frontend/src/components/site/SiteHeader.vue` script imports:

```ts
import { computed, onMounted, ref, watch } from 'vue'
```

Replace `navItems` with:

```ts
const baseNavItems = [
  { href: '/', label: '首页' },
  { href: '/detect', label: '检测上传' },
  { href: '/appeal', label: '平台申诉' },
  { href: '/tro-settlement', label: 'TRO 和解' },
  { href: '/dashboard', label: '用户中心' },
  { href: '/dashboard?tab=reports', label: '报告' }
]

const navItems = computed(() => {
  const items = [...baseNavItems]
  if (user.value?.role === 'admin') items.push({ href: '/admin', label: '后台' })
  return items
})
```

- [ ] **Step 3: Run frontend build**

Run:

```bash
cd frontend && npm run build
```

Expected: TypeScript and Vite build pass.

- [ ] **Step 4: Commit access control**

Run:

```bash
git add frontend/src/router.ts frontend/src/components/site/SiteHeader.vue
git commit -m "feat: restrict admin console access"
```

---

### Task 3: Frontend Admin Tables Console

**Files:**
- Modify: `frontend/src/types/domain.ts`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/views/AdminView.vue`
- Modify: `frontend/src/components/admin/AdminDashboard.vue`
- Modify: `frontend/src/components/admin/AdminTaskTable.vue`

**Interfaces:**
- Consumes:
  - `GET /api/admin/overview`
  - `GET /api/admin/users`
  - `GET /api/admin/jobs`
  - `GET /api/admin/reports`
  - `GET /api/admin/service-requests`
  - `GET /api/admin/notifications`
- Produces:
  - `AdminOverview`
  - `AdminUserRow`
  - `AdminReportRow`
  - `AdminServiceRequestRow`
  - `AdminNotificationRow`
  - `AdminDashboard` props containing all admin table rows.

- [ ] **Step 1: Add frontend types**

Append to `frontend/src/types/domain.ts`:

```ts
export interface AdminOverview extends AdminStats {
  totalReports: number
  totalServiceRequests: number
  unreadNotifications: number
  pendingReviews: number
}

export interface AdminUserRow {
  id: number
  mobile: string
  name: string
  role: UserRole
  createdAt: string
  jobCount: number
  serviceRequestCount: number
}

export interface AdminReportRow {
  id: string
  reportType: UnifiedReportType
  typeLabel: string
  title: string
  ownerName: string
  ownerMobile: string
  riskLevel: RiskLevel
  riskScore: number | null
  generatedAt: string
  linkId: string
}

export interface AdminServiceRequestRow {
  id: string
  requestType: ServiceRequestType
  typeLabel: string
  title: string
  platform: string
  status: ServiceRequestStatus
  contact: string
  ownerName: string
  ownerMobile: string
  createdAt: string
  linkId: string
}

export interface AdminNotificationRow {
  id: number
  title: string
  content: string
  type: string
  isRead: boolean
  ownerName: string
  ownerMobile: string
  createdAt: string
}
```

- [ ] **Step 2: Add API functions**

Update the type import in `frontend/src/api/client.ts` to include the new admin types, then add:

```ts
export function getAdminOverview() {
  return request<AdminOverview>('/api/admin/overview')
}

export function getAdminUsers() {
  return request<AdminUserRow[]>('/api/admin/users')
}

export function getAdminReports() {
  return request<AdminReportRow[]>('/api/admin/reports')
}

export function getAdminServiceRequests() {
  return request<AdminServiceRequestRow[]>('/api/admin/service-requests')
}

export function getAdminNotifications() {
  return request<AdminNotificationRow[]>('/api/admin/notifications')
}
```

- [ ] **Step 3: Load admin data in the view**

Replace `frontend/src/views/AdminView.vue` with a readable SFC that:

```ts
const overview = ref<AdminOverview | null>(null)
const jobs = ref<DetectionJob[]>([])
const users = ref<AdminUserRow[]>([])
const reports = ref<AdminReportRow[]>([])
const serviceRequests = ref<AdminServiceRequestRow[]>([])
const notifications = ref<AdminNotificationRow[]>([])
const loading = ref(true)
const error = ref('')

async function loadAdminConsole() {
  loading.value = true
  error.value = ''
  try {
    const [overviewData, jobsData, usersData, reportsData, serviceRequestsData, notificationsData] = await Promise.all([
      getAdminOverview(),
      getAdminJobs(),
      getAdminUsers(),
      getAdminReports(),
      getAdminServiceRequests(),
      getAdminNotifications(),
    ])
    overview.value = overviewData
    jobs.value = jobsData.jobs
    users.value = usersData
    reports.value = reportsData
    serviceRequests.value = serviceRequestsData
    notifications.value = notificationsData
  } catch {
    error.value = '管理员后台数据加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
```

The template should render `AdminDashboard` only when `overview` exists, otherwise show loading or error with a retry button.

- [ ] **Step 4: Build the tabbed dashboard**

Replace `frontend/src/components/admin/AdminDashboard.vue` with a table-oriented component that defines:

```ts
const tabs = [
  { key: 'overview', label: '概览' },
  { key: 'users', label: '用户' },
  { key: 'jobs', label: '检测任务' },
  { key: 'reports', label: '报告' },
  { key: 'serviceRequests', label: '服务需求' },
  { key: 'notifications', label: '消息' },
  { key: 'modelConfig', label: '大模型配置' },
] as const

type TabKey = typeof tabs[number]['key']
const activeTab = ref<TabKey>('overview')
const keyword = ref('')
```

The component should:

- Render overview stat cards using `overview.totalUsers`, `overview.totalJobs`, `overview.totalReports`, `overview.totalServiceRequests`, `overview.unreadNotifications`, `overview.pendingReviews`.
- Render a keyword input for all table tabs.
- Render users, reports, service requests, and notifications in `<table>` elements.
- Render `AdminTaskTable` on the 检测任务 tab.
- Render `ModelConfigPanel` on the 大模型配置 tab.
- Use report links as `/reports/${row.linkId}`.
- Use service request report links as `/reports/${row.linkId}`.

- [ ] **Step 5: Keep task review layout compatible**

Adjust `frontend/src/components/admin/AdminTaskTable.vue` only if needed so it fits inside a tab without excessive nested card styling. Preserve:

```ts
async function handleReview(status: 'approved' | 'rejected') {
  if (!selectedJob.value || submitting.value) return
  submitting.value = true
  message.value = ''
  try {
    const updated = await updateAdminJobReview(selectedJob.value.id, status, adminNote.value)
    localJobs.value = localJobs.value.map((job) => job.id === updated.id ? updated : job)
    message.value = status === 'approved' ? '已通过复核' : '已驳回复核'
  } catch {
    message.value = '处理失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
```

- [ ] **Step 6: Run frontend verification**

Run:

```bash
cd frontend && npm run build
```

Expected: build passes with no TypeScript errors.

- [ ] **Step 7: Commit frontend console**

Run:

```bash
git add frontend/src/types/domain.ts frontend/src/api/client.ts frontend/src/views/AdminView.vue frontend/src/components/admin/AdminDashboard.vue frontend/src/components/admin/AdminTaskTable.vue
git commit -m "feat: add admin management console tables"
```

---

### Task 4: End-to-End Verification

**Files:**
- Read only unless a defect is found.

**Interfaces:**
- Consumes: implemented admin APIs and frontend console.
- Produces: verified local behavior and a concise final report.

- [ ] **Step 1: Run full backend checks**

Run:

```bash
backend/.venv/bin/python -m unittest discover backend/tests -v
backend/.venv/bin/python -m compileall backend/app
```

Expected: all tests pass and compileall succeeds.

- [ ] **Step 2: Run frontend build**

Run:

```bash
cd frontend && npm run build
```

Expected: Vite build succeeds.

- [ ] **Step 3: Start local servers**

Run backend:

```bash
cd backend && ../backend/.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Run frontend:

```bash
cd frontend && npm run dev -- --host 127.0.0.1 --port 5173
```

Expected: backend listens on `http://127.0.0.1:8000`, frontend listens on `http://127.0.0.1:5173`.

- [ ] **Step 4: Manual browser checks**

Verify:

- Normal user does not see “后台” in the header.
- Normal user opening `/admin` redirects to `/dashboard`.
- Admin user sees “后台”.
- Admin user can open `/admin` and switch through all tabs.
- Tables show empty states or real data without layout overlap.
- Task review still updates status.

- [ ] **Step 5: Final status**

Report:

- Files changed.
- Backend verification commands and results.
- Frontend verification commands and results.
- Local URL for testing.
- Any skipped manual check or known limitation.
