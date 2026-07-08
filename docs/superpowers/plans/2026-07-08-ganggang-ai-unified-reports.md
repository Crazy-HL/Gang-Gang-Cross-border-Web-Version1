# Ganggang AI Unified Reports Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Brand all model-facing results as 港港跨境AI, include platform appeal and TRO settlement reports in the user's report center, render all report types on a unified report detail page, and show the homepage QR code when users click contact actions.

**Architecture:** Add a unified report DTO in the backend service layer that adapts existing `reports` rows and `service_requests.details_json.adviceReport` into one response shape. Keep the current database tables intact. Update the frontend report list/detail components to render by `reportType`, and add a reusable QR contact modal.

**Tech Stack:** FastAPI, SQLAlchemy, MySQL/SQLite-compatible ORM models, Vue 3, Vite, TypeScript, Tailwind CSS, Python `unittest`.

## Global Constraints

- User-visible AI identity must be “港港跨境AI”.
- User-visible result copy must not label output as GPT, model return, or large-model return.
- If submitted user text asks what model/system it is, the generated report must answer as 港港跨境AI.
- Platform appeal and TRO reports remain persisted in `service_requests.details_json.adviceReport`.
- `/api/reports` and `/api/reports/{id}` must include all three report types for the current user only.
- The contact action in report pages opens `/wechat-qrcode-cropped.jpg` in a modal.
- Service reports do not need PDF download in this implementation.

---

### Task 1: Backend Unified Report DTO and Service Report Listing

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/repositories/service_request_repository.py`
- Modify: `backend/app/services/report_service.py`
- Test: `backend/tests/test_unified_reports.py`

**Interfaces:**
- Produces: `report_service.list_user_reports(db: Session, user) -> list[dict]` returns `reportType`, `typeLabel`, `sourceLabel`, and service report fields.
- Produces: `report_service.get_user_report(db: Session, report_id: str, user) -> dict | None` supports service request IDs.

- [ ] **Step 1: Write failing backend tests**

Create `backend/tests/test_unified_reports.py` with tests that build lightweight in-memory objects and assert:

```python
def test_service_request_report_maps_to_unified_report():
    item = make_service_request("APL-1", "appeal", {"adviceReport": model_report})
    report = report_service.service_request_report_to_dict(item)
    assert report["id"] == "APL-1"
    assert report["reportType"] == "appeal"
    assert report["typeLabel"] == "平台申诉"
    assert report["sourceLabel"] == "港港跨境AI"
    assert report["sections"] == model_report["sections"]

def test_fallback_source_label_is_ganggang_basic_assessment():
    item = make_service_request("TRO-1", "tro_settlement", {"adviceReport": fallback_report})
    report = report_service.service_request_report_to_dict(item)
    assert report["sourceLabel"] == "港港跨境基础评估"

def test_service_request_without_advice_report_is_skipped():
    item = make_service_request("APL-2", "appeal", {})
    assert report_service.service_request_report_to_dict(item) is None
```

- [ ] **Step 2: Run tests and verify failure**

Run: `cd backend && .venv/bin/python -m unittest tests.test_unified_reports -v`

Expected: FAIL because `service_request_report_to_dict` does not exist.

- [ ] **Step 3: Implement unified service report mapping**

In `backend/app/services/report_service.py`, add:

```python
SERVICE_REPORT_LABELS = {
    "appeal": {"reportType": "appeal", "typeLabel": "平台申诉"},
    "tro_settlement": {"reportType": "tro_settlement", "typeLabel": "TRO 和解"},
}

def _source_label(source: str | None) -> str:
    return "港港跨境AI" if source == "model" else "港港跨境基础评估"

def service_request_report_to_dict(item: ServiceRequest) -> dict | None:
    details = json.loads(item.details_json or "{}")
    advice = details.get("adviceReport")
    if not isinstance(advice, dict):
        return None
    meta = SERVICE_REPORT_LABELS.get(item.request_type)
    if not meta:
        return None
    return {
        "id": item.id,
        "jobId": item.id,
        "reportType": meta["reportType"],
        "typeLabel": meta["typeLabel"],
        "title": advice.get("title") or item.title,
        "generatedAt": format_datetime(item.created_at),
        "riskLevel": advice.get("riskLevel") or "medium",
        "riskScore": None,
        "summary": advice.get("summary") or "",
        "sections": advice.get("sections") or [],
        "nextActions": advice.get("nextActions") or [],
        "categoryScores": [],
        "evidence": [],
        "suggestions": advice.get("nextActions") or [],
        "reviewStatus": "none",
        "reviewNote": "",
        "sourceLabel": _source_label(advice.get("source")),
    }
```

- [ ] **Step 4: Merge service reports into user reports**

Update `list_user_reports` to append mapped service request reports for `user.id`, sort by `generatedAt` descending, and skip service requests without `adviceReport`.

- [ ] **Step 5: Support service report detail lookup**

Update `get_user_report` to return the existing detection report first, otherwise load a service request with matching ID and `owner_id == user.id`, then return `service_request_report_to_dict(item)`.

- [ ] **Step 6: Run backend tests**

Run: `cd backend && .venv/bin/python -m unittest tests.test_unified_reports tests.test_service_request_service -v`

Expected: PASS.

### Task 2: 港港跨境AI Prompt and Source Copy

**Files:**
- Modify: `backend/app/services/service_request_service.py`
- Modify: `backend/app/services/report_service.py`
- Modify: `frontend/src/views/AppealView.vue`
- Modify: `frontend/src/views/TroSettlementView.vue`
- Modify: `frontend/src/components/dashboard/ServiceRequestTable.vue`
- Test: `backend/tests/test_service_request_service.py`

**Interfaces:**
- Produces: Prompt strings that explicitly require “港港跨境AI” identity.
- Produces: User-visible source labels “港港跨境AI” and “港港跨境基础评估”.

- [ ] **Step 1: Add failing prompt identity test**

In `backend/tests/test_service_request_service.py`, add:

```python
def test_service_prompt_brands_identity_as_ganggang_ai(self):
    prompt = service_request_service._format_prompt(_payload(), "APL-TEST")
    self.assertIn("港港跨境AI", prompt)
    self.assertIn("你是什么模型", prompt)
```

- [ ] **Step 2: Run test and verify failure**

Run: `cd backend && .venv/bin/python -m unittest tests.test_service_request_service -v`

Expected: FAIL until prompt includes the new identity rule.

- [ ] **Step 3: Update prompts**

Update service and detection report prompts with a rule:

```text
- 对用户可见身份统一称为“港港跨境AI”。如果用户询问你是什么模型、你是谁、是不是 GPT，只能回答“我是港港跨境AI，为跨境电商业务提供初步分析建议”。
```

- [ ] **Step 4: Update frontend copy**

Replace source labels:

```ts
const sourceLabels = { model: '港港跨境AI', fallback: '港港跨境基础评估' }
```

Replace visible “大模型分析可能需要约 1 分钟” with:

```text
港港跨境AI 分析可能需要约 1 分钟
```

- [ ] **Step 5: Run tests**

Run: `cd backend && .venv/bin/python -m unittest tests.test_service_request_service -v`

Expected: PASS.

### Task 3: Frontend Unified Report Types

**Files:**
- Modify: `frontend/src/types/domain.ts`
- Modify: `frontend/src/components/dashboard/ReportList.vue`
- Modify: `frontend/src/components/results/ReportViewer.vue`
- Modify: `frontend/src/views/ReportsView.vue`
- Create: `frontend/src/components/results/ServiceReportViewer.vue`

**Interfaces:**
- Consumes: unified report fields from Task 1.
- Produces: report list cards and details that branch by `reportType`.

- [ ] **Step 1: Extend TypeScript report types**

In `domain.ts`, extend `DetectionReport` with optional service fields:

```ts
export type UnifiedReportType = 'ip_detection' | 'appeal' | 'tro_settlement'
export interface DetectionReport {
  reportType?: UnifiedReportType
  typeLabel?: string
  sourceLabel?: string
  sections?: AdviceReportSection[]
  nextActions?: string[]
}
```

- [ ] **Step 2: Update report list cards**

In `ReportList.vue`, add a report type badge and route by `report.id`:

```vue
<span :class="typeClass(report.reportType)">{{ report.typeLabel ?? '知识产权检测' }}</span>
<RouterLink :to="`/reports/${report.id}`">查看报告</RouterLink>
<button v-if="(report.reportType ?? 'ip_detection') === 'ip_detection'">下载PDF</button>
```

- [ ] **Step 3: Create service report detail component**

Create `ServiceReportViewer.vue` that renders title, `sourceLabel`, summary, risk badge, `sections`, `nextActions`, and a contact slot/button.

- [ ] **Step 4: Branch in ReportViewer**

In `ReportViewer.vue`, if `report.reportType` is `appeal` or `tro_settlement`, render `ServiceReportViewer`; otherwise render existing detection layout.

- [ ] **Step 5: Build frontend**

Run: `cd frontend && npm run build`

Expected: PASS.

### Task 4: Contact QR Modal

**Files:**
- Create: `frontend/src/components/common/ContactQrModal.vue`
- Modify: `frontend/src/components/results/ReportViewer.vue`
- Modify: `frontend/src/components/results/ServiceReportViewer.vue`
- Modify: `frontend/src/views/AppealView.vue`
- Modify: `frontend/src/views/TroSettlementView.vue`

**Interfaces:**
- Produces: `ContactQrModal` with props `open: boolean` and emit `close`.

- [ ] **Step 1: Create reusable modal**

Create `ContactQrModal.vue`:

```vue
<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-50 grid place-items-center bg-slate-950/55 px-5" @click.self="$emit('close')">
      <div class="w-full max-w-sm rounded-[2rem] bg-white p-6 shadow-2xl">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm font-black text-blue-700">联系港港跨境</p>
            <h2 class="mt-2 text-xl font-black text-slate-950">扫码添加顾问</h2>
          </div>
          <button type="button" class="rounded-full border border-slate-200 px-3 py-1 text-sm font-bold" @click="$emit('close')">关闭</button>
        </div>
        <div class="mt-5 grid place-items-center rounded-2xl border border-blue-100 bg-blue-50 p-4">
          <img src="/wechat-qrcode-cropped.jpg" alt="港港跨境微信二维码" class="aspect-square w-56 rounded-2xl bg-white object-contain" />
        </div>
        <p class="mt-4 text-sm leading-6 text-slate-600">请备注报告编号，方便顾问快速定位你的资料。</p>
      </div>
    </div>
  </Teleport>
</template>
```

- [ ] **Step 2: Wire modal into report detail**

Use `ref(false)` in report detail and open it from the contact button.

- [ ] **Step 3: Replace service page contact links**

In `AppealView.vue` and `TroSettlementView.vue`, replace `tel:` anchors with buttons that open `ContactQrModal`.

- [ ] **Step 4: Build frontend**

Run: `cd frontend && npm run build`

Expected: PASS.

### Task 5: Final Verification

**Files:**
- Verify all touched files.

- [ ] **Step 1: Run backend unit tests**

Run: `cd backend && .venv/bin/python -m unittest tests.test_service_request_service tests.test_unified_reports -v`

Expected: PASS.

- [ ] **Step 2: Run backend compile check**

Run: `cd backend && .venv/bin/python -m compileall app tests`

Expected: completes with no errors.

- [ ] **Step 3: Run frontend build**

Run: `cd frontend && npm run build`

Expected: PASS.

- [ ] **Step 4: Verify app servers**

Run:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN || true
lsof -nP -iTCP:5173 -sTCP:LISTEN || true
```

Expected: backend and frontend ports are listening, or restart them with the existing dev commands.
