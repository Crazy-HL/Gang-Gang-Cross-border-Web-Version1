# 后端接口协作开发文档

本项目采用前后端分离架构：

```text
frontend/   Vue + Vite + TypeScript + Tailwind CSS
backend/    Python + FastAPI
```

协作目标：**前端保持不变，后端开发者只需要按本文档完善接口功能。**

前端统一通过：

```text
frontend/src/api/client.ts
```

调用后端接口。

后端入口：

```text
backend/app/main.py
```

接口文档地址：

```text
http://localhost:8000/docs
```

---

## 一、当前后端目录结构

```text
backend/
├─ API_CONTRACT.md                 # 后端接口协作开发文档
├─ requirements.txt                # Python 依赖
└─ app/
   ├─ main.py                      # FastAPI 入口，注册所有 router
   ├─ models.py                    # Pydantic 数据模型，前后端字段必须保持一致
   ├─ mock_data.py                 # 当前 mock 数据，后续逐步替换
   ├─ routers/                     # 已接入 FastAPI 的接口路由
   │  ├─ __init__.py
   │  ├─ auth.py                   # 认证接口：短信验证码、密码登录、验证码登录、注册、当前用户
   │  ├─ jobs.py                   # 任务接口：创建、上传、运行、结果、PDF
   │  ├─ reports.py                # 报告接口：报告列表、报告详情
   │  ├─ admin.py                  # 管理后台接口
   │  └─ options.py                # 表单选项接口
   ├─ services/                    # 业务逻辑层
   │  ├─ __init__.py
   │  ├─ auth_service.py           # 认证、短信验证码、密码登录、注册逻辑
   │  ├─ sms_service.py            # 阿里云短信发送逻辑
   │  ├─ job_service.py            # 预留：任务创建、任务列表、任务运行逻辑
   │  ├─ report_service.py         # 预留：报告查询、检测结果生成逻辑
   │  ├─ admin_service.py          # 预留：管理后台统计、管理员任务逻辑
   │  └─ file_service.py           # 预留：文件上传、文件存储逻辑
   ├─ repositories/                # 数据库访问层
   │  ├─ __init__.py
   │  ├─ user_repository.py        # 用户表数据库操作
   │  ├─ verification_code_repository.py # 验证码表数据库操作
   │  ├─ job_repository.py         # 任务表数据库操作
   │  ├─ report_repository.py      # 报告表数据库操作
   │  └─ admin_repository.py       # 后台统计、管理员查询
   ├─ db/                          # 数据库相关文件
   │  ├─ __init__.py
   │  ├─ session.py                # SQLAlchemy 连接、Session、MySQL 连接池配置
   │  ├─ init_db.py                # 建表和轻量字段补齐
   │  └─ base.py                   # ORM Base、用户/验证码/任务/报告模型
   └─ core/                        # 核心配置与安全能力
      ├─ __init__.py
      ├─ config.py                 # 环境变量、数据库、短信配置项
      └─ security.py               # token、密码哈希、当前用户校验
```

---

## 二、协作规则

### 1. 前端不改

后端开发时默认不要修改：

```text
frontend/
```

前端已经按照当前接口格式写好。只要后端接口路径、请求格式、返回字段不变，前端页面和样式就能保持不变。

---

### 2. 接口路径不要改

前端当前固定调用以下接口：

```text
GET  /api/options
POST /api/auth/code
POST /api/auth/login
POST /api/auth/login/code
POST /api/auth/register
GET  /api/auth/me
POST /api/auth/logout
GET  /api/jobs
POST /api/jobs
POST /api/jobs/{job_id}/upload
POST /api/jobs/{job_id}/run
GET  /api/jobs/{job_id}/results
GET  /api/jobs/{job_id}/status
GET  /api/reports
GET  /api/reports/{report_id}
GET  /api/jobs/{job_id}/report/pdf
GET  /api/notifications
GET  /api/notifications/unread-count
POST /api/notifications/{notification_id}/read
GET  /api/admin/jobs
GET  /api/admin/model-config
PUT  /api/admin/model-config
```

可以新增接口，但不要删除或改名已有接口。

---

### 3. 返回字段不要改名

前端依赖 camelCase 字段，例如：

```json
{
  "createdAt": "2026-06-09 10:00",
  "riskLevel": "high",
  "riskScore": 85,
  "ownerName": "张三"
}
```

不要改成：

```json
{
  "created_at": "2026-06-09 10:00",
  "risk_level": "high",
  "risk_score": 85,
  "owner_name": "张三"
}
```

后端内部数据库字段可以使用 snake_case，但接口返回给前端时必须保持当前 camelCase。

---

### 4. 可以增加字段，但不要删字段

允许新增字段，例如：

```json
{
  "id": "1001",
  "title": "检测任务",
  "status": "done",
  "createdAt": "2026-06-09 10:00",
  "extraField": "新增字段"
}
```

但不能删除前端已经使用的字段。

---

### 5. 当前 mock service 暂时不要直接删

当前可运行逻辑已经拆分到：

```text
backend/app/services/auth_service.py
backend/app/services/job_service.py
backend/app/services/report_service.py
backend/app/services/admin_service.py
backend/app/services/file_service.py
```

旧的 `backend/app/services.py` 已移除，后续合作者应继续在 `services/` 包目录内完善对应模块。

---

## 三、推荐后端分工

### 1. 认证模块负责人

负责文件：

```text
backend/app/routers/auth.py
backend/app/services/auth_service.py
backend/app/repositories/user_repository.py
backend/app/core/security.py
```

负责接口：

```text
POST /api/auth/code
POST /api/auth/login
POST /api/auth/login/code
POST /api/auth/register
GET  /api/auth/me
POST /api/auth/logout
```

当前状态：已接入 MySQL、阿里云短信、验证码持久化、密码哈希、Bearer token。

后续可继续完善：

- 发送频率限制
- token 黑名单或刷新 token
- 找回密码/重置密码
- 管理员权限策略

---

### 2. 任务模块负责人

负责文件：

```text
backend/app/routers/jobs.py
backend/app/services/job_service.py
backend/app/repositories/job_repository.py
```

负责接口：

```text
GET  /api/jobs
POST /api/jobs
POST /api/jobs/{job_id}/run
GET  /api/jobs/{job_id}/results
```

需要完善：

- 创建真实任务记录
- 查询用户任务列表
- 任务状态流转
- 任务进入检测队列
- 查询任务检测结果

建议后续新增接口：

```text
GET    /api/jobs/{job_id}/status
DELETE /api/jobs/{job_id}
POST   /api/jobs/{job_id}/review
```

---

### 3. 文件上传模块负责人

负责文件：

```text
backend/app/routers/jobs.py
backend/app/services/file_service.py
backend/app/repositories/job_repository.py
```

负责接口：

```text
POST /api/jobs/{job_id}/upload
```

需要完善：

- 保存上传文件
- 校验文件类型
- 校验文件大小
- 返回真实文件 URL
- 把文件 URL 绑定到任务

建议限制：

```text
允许 jpg/jpeg/png
最大 8MB
```

---

### 4. 报告模块负责人

负责文件：

```text
backend/app/routers/reports.py
backend/app/routers/jobs.py
backend/app/services/report_service.py
backend/app/repositories/report_repository.py
```

负责接口：

```text
GET /api/reports
GET /api/reports/{report_id}
GET /api/jobs/{job_id}/results
GET /api/jobs/{job_id}/report/pdf
```

需要完善：

- 查询真实报告列表
- 查询真实报告详情
- 生成真实检测结果
- 生成真实 PDF
- 支持中文字体和图片证据

---

### 5. 管理后台模块负责人

负责文件：

```text
backend/app/routers/admin.py
backend/app/services/admin_service.py
backend/app/repositories/admin_repository.py
```

负责接口：

```text
GET /api/admin/jobs
```

需要完善：

- 管理员权限校验
- 真实统计数据
- 管理员任务列表
- 搜索、筛选、分页
- 人工复核状态

建议后续新增接口：

```text
GET   /api/admin/users
PATCH /api/admin/jobs/{job_id}
POST  /api/admin/jobs/{job_id}/review
```

---

### 6. 数据库模块负责人

负责文件：

```text
backend/app/db/session.py
backend/app/db/base.py
backend/app/repositories/*.py
```

当前数据库：MySQL。

配置位置：

```text
backend/.env
GANGGANG_DATABASE_URL=mysql+pymysql://用户名:密码@主机:3306/数据库名?charset=utf8mb4
```

已实现：

- SQLAlchemy 连接池
- `users` 用户表
- `verification_codes` 验证码表
- `jobs` 任务表
- `job_files` 文件表
- `reports` 报告表
- `category_scores` 分项评分表
- `evidence` 证据表
- `init_db.py` 自动建表和轻量字段补齐

建议后续增加：

```text
Alembic
```

用于正式的数据库迁移版本管理。

---

## 四、核心数据结构

数据结构定义位置：

```text
backend/app/models.py
frontend/src/types/domain.ts
```

前后端字段需要保持一致。

---

## 1. DetectionFormInput：检测任务创建参数

```json
{
  "detectionType": "trademark",
  "brand": "ACTIVEWEAR",
  "category": "shoes",
  "market": "US",
  "productLink": "https://example.com/product",
  "title": "商品标题或卖点文案",
  "hasFile": true,
  "file": {
    "name": "product.png",
    "type": "image/png",
    "size": 102400
  }
}
```

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| detectionType | string | `trademark`、`design`、`copyright` |
| brand | string | 品牌名 |
| category | string | 商品类目 |
| market | string | 目标市场 |
| productLink | string | 商品链接 |
| title | string | 商品标题或描述 |
| hasFile | boolean | 是否上传文件 |
| file | object/null | 文件信息 |

---

## 2. DetectionJob：检测任务

```json
{
  "id": "1001",
  "type": "trademark",
  "title": "ACTIVEWEAR 轻量运动鞋风险检测",
  "brand": "ACTIVEWEAR",
  "category": "shoes",
  "market": "US",
  "status": "done",
  "riskLevel": "high",
  "riskScore": 85,
  "createdAt": "2026-06-01 10:20",
  "ownerName": "张三",
  "fileUrl": "/uploads/1001/product.png",
  "reviewStatus": "none",
  "reviewNote": ""
}
```

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 任务 ID |
| type | string | 检测类型 |
| title | string | 任务标题 |
| brand | string | 品牌名 |
| category | string | 商品类目 |
| market | string | 目标市场 |
| status | string | `queued`、`processing`、`done`、`failed` |
| riskLevel | string | `high`、`medium`、`low`、`pending` |
| riskScore | number/null | 风险分数 |
| createdAt | string | 创建时间 |
| ownerName | string | 用户名 |
| fileUrl | string | 第一张上传文件 URL，没有则为空字符串 |
| reviewStatus | string | `none`、`pending`、`approved`、`rejected` |
| reviewNote | string | 人工复核备注 |

---

## 3. DetectionReport：检测报告

```json
{
  "id": "r-1001",
  "jobId": "1001",
  "title": "ACTIVEWEAR 轻量运动鞋知识产权风险报告",
  "generatedAt": "2026-06-01 10:26",
  "riskLevel": "high",
  "riskScore": 85,
  "summary": "检测摘要文本",
  "categoryScores": [
    {
      "type": "trademark",
      "label": "商标",
      "score": 89,
      "hits": 3
    }
  ],
  "evidence": [
    {
      "id": "ev-1",
      "category": "trademark",
      "matched": "ACTIVEWEAR",
      "source": "USPTO",
      "similarity": 0.89,
      "description": "证据说明",
      "imageUrl": "/evidence/activewear.svg"
    }
  ],
  "suggestions": [
    "处理建议 1",
    "处理建议 2"
  ]
}
```

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 报告 ID |
| jobId | string | 对应任务 ID |
| title | string | 报告标题 |
| generatedAt | string | 报告生成时间 |
| riskLevel | string | 风险等级 |
| riskScore | number | 风险分数 |
| summary | string | 摘要 |
| categoryScores | array | 分项风险评分 |
| evidence | array | 命中证据 |
| suggestions | array | 处理建议 |

---

## 4. AdminStats：后台统计

```json
{
  "totalJobs": 1286,
  "totalUsers": 342,
  "completedJobs": 1038,
  "highRiskRate": 0.31
}
```

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| totalJobs | number | 总任务数 |
| totalUsers | number | 总用户数 |
| completedJobs | number | 已完成任务数 |
| highRiskRate | number | 高风险占比，0 到 1 |

---

# 五、接口列表

---

## 1. 健康检查

### `GET /health`

负责文件：

```text
backend/app/main.py
```

当前状态：已可用。

返回：

```json
{
  "ok": true
}
```

可选完善：增加版本号、数据库连接状态。

---

## 2. 获取检测选项

### `GET /api/options`

负责文件：

```text
backend/app/routers/options.py
backend/app/services/__init__.py
```

后续可迁移到：

```text
backend/app/services/job_service.py
```

当前状态：mock 可用。

返回：

```json
{
  "categories": [
    { "value": "apparel", "label": "服装配饰" },
    { "value": "shoes", "label": "鞋类箱包" },
    { "value": "home", "label": "家居用品" },
    { "value": "electronics", "label": "消费电子" }
  ],
  "markets": [
    { "value": "US", "label": "美国" },
    { "value": "EU", "label": "欧洲" },
    { "value": "JP", "label": "日本" },
    { "value": "UK", "label": "英国" }
  ]
}
```

前端依赖字段：

```text
categories[].value
categories[].label
markets[].value
markets[].label
```

---

# 六、认证接口

---

## 3. 发送验证码

### `POST /api/auth/code`

负责文件：

```text
backend/app/routers/auth.py
backend/app/services/auth_service.py
backend/app/repositories/user_repository.py
```

当前状态：已可用。验证码会保存到 MySQL 的 `verification_codes` 表；开启 `GANGGANG_SMS_ENABLED=true` 后会调用阿里云短信。

请求：

```json
{
  "mobile": "13800000000"
}
```

返回：

```json
{
  "ok": true
}
```

需要继续完善：

- 发送频率限制
- 图形验证码或风控策略
- 生产环境日志脱敏

前端依赖字段：

```text
ok
```

---

## 4. 登录

### `POST /api/auth/login`

负责文件：

```text
backend/app/routers/auth.py
backend/app/services/auth_service.py
backend/app/repositories/user_repository.py
backend/app/core/security.py
```

当前状态：已可用。默认使用手机号 + 密码登录。

请求：

```json
{
  "mobile": "13800000000",
  "password": "123456"
}
```

返回：

```json
{
  "ok": true,
  "token": "access-token",
  "user": {
    "id": 1,
    "mobile": "13800000000",
    "name": "用户0000",
    "role": "user"
  }
}
```

密码存储：后端只保存 `password_hash`，不保存明文密码。

前端依赖字段：

```text
ok
token
user.id
user.mobile
user.name
user.role
```

可新增字段：

```json
{
  "tokenType": "Bearer",
  "expiresIn": 86400,
  "user": {
    "mobile": "13800000000",
    "role": "user"
  }
}
```

---

## 4.1 验证码登录

### `POST /api/auth/login/code`

负责文件：

```text
backend/app/routers/auth.py
backend/app/services/auth_service.py
backend/app/repositories/verification_code_repository.py
backend/app/core/security.py
```

当前状态：已可用，作为密码登录的备用方式。

请求：

```json
{
  "mobile": "13800000000",
  "code": "123456"
}
```

返回：

```json
{
  "ok": true,
  "token": "access-token",
  "user": {
    "id": 1,
    "mobile": "13800000000",
    "name": "用户0000",
    "role": "user"
  }
}
```

---

## 5. 注册

### `POST /api/auth/register`

负责文件：

```text
backend/app/routers/auth.py
backend/app/services/auth_service.py
backend/app/repositories/user_repository.py
```

当前状态：已可用。注册使用手机号 + 短信验证码 + 密码，用户写入 MySQL `users` 表。

请求：

```json
{
  "mobile": "13800000000",
  "code": "123456",
  "password": "123456"
}
```

返回：

```json
{
  "ok": true,
  "userId": 1,
  "token": "access-token",
  "user": {
    "id": 1,
    "mobile": "13800000000",
    "name": "用户0000",
    "role": "user"
  }
}
```

需要继续完善：

- 密码强度策略
- 重复注册提示
- 找回密码/重置密码
- 用户资料初始化

前端依赖字段：

```text
ok
```

---

# 七、任务接口

---

## 6. 获取任务列表

### `GET /api/jobs`

负责文件：

```text
backend/app/routers/jobs.py
backend/app/services/job_service.py
backend/app/repositories/job_repository.py
```

当前状态：mock。

返回：

```json
[
  {
    "id": "1001",
    "type": "trademark",
    "title": "ACTIVEWEAR 轻量运动鞋风险检测",
    "brand": "ACTIVEWEAR",
    "category": "shoes",
    "market": "US",
    "status": "done",
    "riskLevel": "high",
    "riskScore": 85,
    "createdAt": "2026-06-01 10:20",
    "ownerName": "张三"
  }
]
```

需要完善：

- 根据当前登录用户查询任务
- 接数据库
- 支持分页、搜索、筛选

前端当前期望直接返回数组 `DetectionJob[]`，暂时不要改成分页对象。

---

## 7. 创建检测任务

### `POST /api/jobs`

负责文件：

```text
backend/app/routers/jobs.py
backend/app/services/job_service.py
backend/app/repositories/job_repository.py
```

当前状态：mock，只生成任务 ID。

请求：

```json
{
  "detectionType": "trademark",
  "brand": "NORTHBIRD",
  "category": "apparel",
  "market": "UK",
  "productLink": "https://example.com/product",
  "title": "商品标题",
  "hasFile": false,
  "file": null
}
```

返回：

```json
{
  "jobId": "mock-northbird",
  "input": {
    "detectionType": "trademark",
    "brand": "NORTHBIRD",
    "category": "apparel",
    "market": "UK",
    "productLink": "https://example.com/product",
    "title": "商品标题",
    "hasFile": false,
    "file": null
  }
}
```

需要完善：

- 创建数据库任务记录
- 绑定当前用户
- 初始化任务状态
- 返回真实任务 ID

前端依赖字段：

```text
jobId
input
```

---

## 8. 上传任务文件

### `POST /api/jobs/{job_id}/upload`

负责文件：

```text
backend/app/routers/jobs.py
backend/app/services/file_service.py
backend/app/repositories/job_repository.py
```

当前状态：已可用。文件保存到 `backend/uploads/{job_id}/`，数据库记录写入 `job_files`，返回可通过 `/uploads/...` 访问的文件 URL。

请求类型：

```text
multipart/form-data
```

字段：

```text
file
```

返回：

```json
{
  "jobId": "job-20260610123000-northbird",
  "fileUrl": "/uploads/job-20260610123000-northbird/20260610123000123456-product.png"
}
```

文件限制：

```text
允许 jpg/jpeg/png
最大 8MB
```

后续可继续完善：

- 接入对象存储 OSS/S3
- 生成缩略图
- 文件病毒扫描
- 定期清理孤儿文件

前端依赖字段：

```text
jobId
fileUrl
```

---

## 9. 启动检测任务

### `POST /api/jobs/{job_id}/run`

负责文件：

```text
backend/app/routers/jobs.py
backend/app/services/job_service.py
backend/app/repositories/job_repository.py
```

当前状态：占位，只返回 queued。

返回：

```json
{
  "jobId": "mock-northbird",
  "status": "queued"
}
```

需要完善：

- 检查任务是否存在
- 检查任务是否属于当前用户
- 检查资料是否完整
- 推送任务到检测队列
- 更新任务状态

前端依赖字段：

```text
jobId
status
```

---

## 10. 获取任务检测结果

### `GET /api/jobs/{job_id}/results`

负责文件：

```text
backend/app/routers/jobs.py
backend/app/services/report_service.py
backend/app/repositories/report_repository.py
```

当前状态：mock。

返回：

```json
{
  "id": "r-1001",
  "jobId": "1001",
  "title": "ACTIVEWEAR 轻量运动鞋知识产权风险报告",
  "generatedAt": "2026-06-01 10:26",
  "riskLevel": "high",
  "riskScore": 85,
  "summary": "检测摘要文本",
  "categoryScores": [],
  "evidence": [],
  "suggestions": []
}
```

404 返回：

```json
{
  "detail": "Report not found"
}
```

需要完善：

- 根据真实任务 ID 查询报告
- 返回真实风险评分
- 返回真实证据和建议
- 权限校验

前端当前期望返回完整 `DetectionReport`。

---

# 八、报告接口

---

## 11. 获取报告列表

### `GET /api/reports`

负责文件：

```text
backend/app/routers/reports.py
backend/app/services/report_service.py
backend/app/repositories/report_repository.py
```

当前状态：mock。

返回：

```json
[
  {
    "id": "r-1001",
    "jobId": "1001",
    "title": "ACTIVEWEAR 轻量运动鞋知识产权风险报告",
    "generatedAt": "2026-06-01 10:26",
    "riskLevel": "high",
    "riskScore": 85,
    "summary": "检测摘要文本",
    "categoryScores": [],
    "evidence": [],
    "suggestions": []
  }
]
```

需要完善：

- 根据当前用户查询报告
- 支持分页、搜索、风险等级筛选

前端当前期望直接返回数组 `DetectionReport[]`。

---

## 12. 获取报告详情

### `GET /api/reports/{report_id}`

负责文件：

```text
backend/app/routers/reports.py
backend/app/services/report_service.py
backend/app/repositories/report_repository.py
```

当前状态：mock。

返回：

```json
{
  "id": "r-1001",
  "jobId": "1001",
  "title": "ACTIVEWEAR 轻量运动鞋知识产权风险报告",
  "generatedAt": "2026-06-01 10:26",
  "riskLevel": "high",
  "riskScore": 85,
  "summary": "检测摘要文本",
  "categoryScores": [],
  "evidence": [],
  "suggestions": []
}
```

需要完善：

- 根据数据库报告 ID 查询
- 校验查看权限
- 返回真实报告内容

---

## 13. 下载 PDF 报告

### `GET /api/jobs/{job_id}/report/pdf`

负责文件：

```text
backend/app/routers/jobs.py
backend/app/services/report_service.py
backend/app/repositories/report_repository.py
```

当前状态：占位 PDF。

返回类型：

```text
application/pdf
```

Header：

```text
content-disposition: attachment; filename="ip-report-{job_id}.pdf"
```

需要完善：

- 查询真实报告数据
- 生成真实 PDF
- 支持中文字体
- 嵌入证据图片
- 权限校验

建议方案：

```text
ReportLab
WeasyPrint
Playwright HTML to PDF
```

---

# 九、管理后台接口

---

## 14. 管理后台统计和任务列表

### `GET /api/admin/jobs`

负责文件：

```text
backend/app/routers/admin.py
backend/app/services/admin_service.py
backend/app/repositories/admin_repository.py
```

当前状态：已可用。需要管理员角色，返回真实统计数据和真实任务列表。

返回：

```json
{
  "stats": {
    "totalJobs": 1286,
    "totalUsers": 342,
    "completedJobs": 1038,
    "highRiskRate": 0.31
  },
  "jobs": [
    {
      "id": "1001",
      "type": "trademark",
      "title": "ACTIVEWEAR 轻量运动鞋风险检测",
      "brand": "ACTIVEWEAR",
      "category": "shoes",
      "market": "US",
      "status": "done",
      "riskLevel": "high",
      "riskScore": 85,
      "createdAt": "2026-06-01 10:20",
      "ownerName": "张三",
      "reviewStatus": "pending",
      "reviewNote": "请人工复核该任务风险"
    }
  ]
}
```

后续可继续完善：

- 搜索、筛选、分页
- 管理员用户列表
- 复核处理历史

前端依赖字段：

```text
stats
jobs
```

## 14.1 管理员处理人工复核

### `PATCH /api/admin/jobs/{job_id}/review`

负责文件：

```text
backend/app/routers/admin.py
backend/app/services/admin_service.py
backend/app/repositories/admin_repository.py
```

当前状态：已可用。只有管理员角色可以调用。

请求：

```json
{
  "reviewStatus": "approved",
  "reviewNote": "管理员已确认风险可控"
}
```

`reviewStatus` 允许：

```text
approved
rejected
```

返回：更新后的 `DetectionJob`。

```json
{
  "id": "job-xxx",
  "reviewStatus": "approved",
  "reviewNote": "管理员已确认风险可控"
}
```

---

# 十、建议新增的预留接口

这些接口当前前端还没有调用，后端可以先创建或后续新增。

| 接口 | 作用 | 建议负责文件 |
|---|---|---|
| `GET /api/auth/me` | 获取当前登录用户 | `auth.py`, `auth_service.py` |
| `POST /api/auth/logout` | 退出登录 | `auth.py`, `auth_service.py` |
| `GET /api/jobs/{job_id}/status` | 获取检测进度 | `jobs.py`, `job_service.py` |
| `DELETE /api/jobs/{job_id}` | 删除任务 | `jobs.py`, `job_service.py` |
| `POST /api/jobs/{job_id}/review` | 申请人工复核 | `jobs.py`, `job_service.py` |
| `GET /api/notifications` | 获取用户通知列表 | `notifications.py`, `notification_service.py` |
| `GET /api/notifications/unread-count` | 获取未读通知数量 | `notifications.py`, `notification_service.py` |
| `POST /api/notifications/{notification_id}/read` | 标记通知已读 | `notifications.py`, `notification_service.py` |
| `GET /api/admin/users` | 管理员用户列表 | `admin.py`, `admin_service.py` |
| `GET /api/admin/model-config` | 获取大模型报告配置 | `admin.py`, `admin_service.py` |
| `PUT /api/admin/model-config` | 保存大模型报告配置 | `admin.py`, `admin_service.py` |
| `PATCH /api/admin/jobs/{job_id}/review` | 管理员处理人工复核 | `admin.py`, `admin_service.py` |

---

# 十一、接口完成状态总览

| 模块 | 接口 | 当前状态 | 是否需要完善 | 推荐负责人文件 |
|---|---|---|---|---|
| 健康检查 | `GET /health` | 可用 | 否 | `main.py` |
| 选项 | `GET /api/options` | mock 可用 | 可选 | `options.py` |
| 认证 | `POST /api/auth/code` | 已接入 MySQL + 阿里云短信 | 可选 | `auth_service.py`, `sms_service.py` |
| 认证 | `POST /api/auth/login` | 密码登录可用 | 可选 | `auth_service.py`, `security.py` |
| 认证 | `POST /api/auth/login/code` | 验证码登录可用 | 可选 | `auth_service.py`, `security.py` |
| 认证 | `POST /api/auth/register` | 手机号 + 验证码 + 密码注册可用 | 可选 | `auth_service.py` |
| 认证 | `GET /api/auth/me` | Bearer token 当前用户可用 | 可选 | `auth.py`, `security.py` |
| 认证 | `POST /api/auth/logout` | 可用 | 可选 | `auth_service.py` |
| 任务 | `GET /api/jobs` | mock | 是 | `job_service.py` |
| 任务 | `POST /api/jobs` | mock | 是 | `job_service.py` |
| 文件 | `POST /api/jobs/{job_id}/upload` | 占位 | 是 | `file_service.py` |
| 任务 | `POST /api/jobs/{job_id}/run` | 占位 | 是 | `job_service.py` |
| 结果 | `GET /api/jobs/{job_id}/results` | 已接入 MySQL 报告和复核状态 | 可选 | `report_service.py` |
| 报告 | `GET /api/reports` | 已接入 MySQL 报告列表 | 可选 | `report_service.py` |
| 报告 | `GET /api/reports/{report_id}` | 已接入 MySQL 报告详情 | 可选 | `report_service.py` |
| PDF | `GET /api/jobs/{job_id}/report/pdf` | 占位 | 是 | `report_service.py` |
| 通知 | `GET /api/notifications` | 可用 | 可选 | `notifications.py`, `notification_service.py` |
| 通知 | `GET /api/notifications/unread-count` | 可用 | 可选 | `notifications.py`, `notification_service.py` |
| 通知 | `POST /api/notifications/{notification_id}/read` | 可用 | 可选 | `notifications.py`, `notification_service.py` |
| 管理后台 | `GET /api/admin/jobs` | 已接入 MySQL + 管理员权限 | 可选 | `admin_service.py` |
| 大模型配置 | `GET /api/admin/model-config` | 可用 | 可选 | `admin_service.py`, `model_config_repository.py` |
| 大模型配置 | `PUT /api/admin/model-config` | 可用 | 可选 | `admin_service.py`, `model_config_repository.py` |
| 报告生成 | `provider=openai/anthropic` | 已支持 OpenAI 兼容与 Anthropic Messages 协议 | 可选 | `report_service.py` |

---

# 十二、建议开发优先级

## 第一阶段：数据库基础

当前状态：已完成 MySQL 基础表、用户表、验证码表、认证 token 和密码哈希；任务、报告等业务表已有 ORM 模型，后续继续补真实业务写入逻辑。

已完成文件：

```text
backend/app/core/config.py        # 环境变量配置，默认 SQLite，可通过 .env 切换 MySQL
backend/app/db/session.py         # SQLAlchemy engine、Session、MySQL 连接池
backend/app/db/base.py            # ORM Base 和核心数据表模型
backend/app/db/init_db.py         # 启动时创建数据库表并补齐必要字段
backend/app/repositories/*.py     # 用户、验证码、任务、报告、后台基础查询方法
```

已创建数据表模型：

```text
users
verification_codes
notifications
model_configs
jobs
job_files
reports
category_scores
evidence
```

后续需要继续完善：

```text
Alembic 数据库迁移
真实任务/报告业务写入逻辑
更多索引和约束
生产环境密钥与数据库账号轮换
```

---

## 第二阶段：认证

负责人主要文件：

```text
backend/app/services/auth_service.py
backend/app/repositories/user_repository.py
backend/app/core/security.py
```

已完成：

```text
短信验证码发送
验证码 MySQL 持久化
手机号 + 密码注册
密码登录
验证码备用登录
Bearer token
当前用户接口
前端登录态恢复
```

后续可继续完善：

```text
发送频率限制
找回密码/重置密码
token 刷新或黑名单
管理员权限策略
```

---

## 第三阶段：任务和上传

负责人主要文件：

```text
backend/app/services/job_service.py
backend/app/services/file_service.py
backend/app/repositories/job_repository.py
```

需要完成：

```text
创建任务
上传文件
任务列表
任务运行
任务状态
```

---

## 第四阶段：检测结果和报告

负责人主要文件：

```text
backend/app/services/report_service.py
backend/app/repositories/report_repository.py
```

需要完成：

```text
检测结果
报告列表
报告详情
PDF 下载
```

---

## 第五阶段：管理后台

负责人主要文件：

```text
backend/app/services/admin_service.py
backend/app/repositories/admin_repository.py
```

需要完成：

```text
管理员权限
后台统计
任务管理
用户管理
人工复核
```

---

# 十三、本地运行方式

## 后端

```bash
cd D:\ganggangweb_v1\backend
python -m uvicorn app.main:app --reload --port 8000
```

访问接口文档：

```text
http://localhost:8000/docs
```

健康检查：

```text
http://localhost:8000/health
```

## 前端

```bash
cd D:\ganggangweb_v1\frontend
npm install
npm run dev
```

访问：

```text
http://localhost:5173
```

如果后端端口不是 8000：

```bash
set VITE_API_BASE_URL=http://localhost:8001
npm run dev
```

---

# 十四、给合作者的结论

1. 当前后端接口文件和协作文件已经预留好，认证模块已接入真实 MySQL、短信验证码、密码登录和 token。
2. `routers/` 负责接口入口。
3. `services/` 负责业务逻辑。
4. `repositories/` 负责数据库访问。
5. `db/` 负责数据库连接和 ORM 基础。
6. `core/` 负责配置、安全、token、密码哈希、权限。
7. 任务、报告、管理后台接口仍以 mock/占位为主，是下一阶段重点。
8. 后续只要接口路径和返回字段保持一致，前端不需要改。
