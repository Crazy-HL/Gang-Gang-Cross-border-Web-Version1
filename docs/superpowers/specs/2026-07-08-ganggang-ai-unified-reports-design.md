# 港港跨境AI与统一报告页设计

## 背景

当前系统已经有三类报告来源：

- 知识产权检测报告：存储在 `reports` 表，通过 `/api/reports` 和 `/api/reports/:id` 展示。
- 平台申诉报告：生成后存储在 `service_requests.details_json.adviceReport`。
- TRO 和解报告：生成后存储在 `service_requests.details_json.adviceReport`。

用户希望所有返回结果统一呈现为“港港跨境AI”，平台申诉和 TRO 和解报告也进入“我的报告”和报告详情页，并且报告里的“联系我们”点击后弹出首页二维码。

## 目标

1. 所有用户可见结果不出现 “GPT”“模型返回”“大模型返回”等底层模型称呼。
2. 如果用户输入中询问“你是什么模型/你是谁/是不是 GPT”，报告内容必须以“港港跨境AI”作为身份回答。
3. 平台申诉和 TRO 和解报告保存到数据库，并出现在“我的报告”列表。
4. 三类报告点击后进入统一报告详情页，但用不同颜色和标签区分类型。
5. 报告详情页的“联系我们”按钮弹出首页同款二维码，而不是跳转电话链接。

## 推荐架构

采用“统一报告层”，不重构现有 `reports` 表。

原因：

- `reports.job_id` 当前是检测任务外键且唯一，强行把服务报告塞进该表会影响现有检测任务、PDF、报告详情和任务关系。
- 平台申诉/TRO 报告已经保存在 `service_requests.details_json.adviceReport`，满足数据库持久化要求。
- 通过后端服务层合并三类报告，可以以较小改动支持统一列表与统一详情。

## 后端设计

新增统一报告 DTO，返回字段覆盖三类报告：

- `id`: 统一报告 ID。检测报告继续用现有 `report.id` 或 `jobId`；服务报告使用服务工单 ID。
- `reportType`: `ip_detection` / `appeal` / `tro_settlement`。
- `typeLabel`: “知识产权检测” / “平台申诉” / “TRO 和解”。
- `title`
- `generatedAt`
- `riskLevel`
- `riskScore`: 服务报告没有分数时可为空。
- `summary`
- `sections`: 服务报告使用原 `sections`；检测报告可为空。
- `nextActions`: 服务报告使用原 `nextActions`；检测报告可映射自 `suggestions`。
- `categoryScores`
- `evidence`
- `suggestions`
- `reviewStatus`
- `reviewNote`
- `sourceLabel`: 用户可见来源，只允许“港港跨境AI”或“港港跨境基础评估”。

API 行为：

- `GET /api/reports`：合并当前用户的检测报告和服务工单报告，按生成/提交时间倒序返回。
- `GET /api/reports/{id}`：先查检测报告；查不到再查当前用户服务工单报告。
- 已有检测报告行为保持兼容。
- 服务报告必须校验 `owner_id`，不能跨用户读取。

品牌身份规则：

- 后端提示词中加入身份约束：对用户可见输出只能称为“港港跨境AI”。
- 如果用户材料中包含“你是什么模型”“是不是 GPT”“你是谁”等提问，报告摘要或建议中只能回答“我是港港跨境AI，为跨境电商业务提供初步分析建议”。
- 前端来源标签将 `source=model` 显示为“港港跨境AI”，将 `source=fallback` 显示为“港港跨境基础评估”。

## 前端设计

报告列表：

- “我的报告”列表展示三类报告。
- 每张卡片显示类型标签和对应颜色：
  - 知识产权检测：蓝色。
  - 平台申诉：金橙色。
  - TRO 和解：红橙色。
- “查看报告”统一跳转 `/reports/:id`。
- 检测报告保留“下载 PDF”；服务报告暂不显示 PDF 下载，避免空 PDF 或格式不完整。

统一详情页：

- 复用现有 `/reports/:id` 路由。
- 根据 `reportType` 切换标题区标签、颜色和正文布局。
- 检测报告继续展示风险摘要、官方命中、分项分数、建议和复核操作。
- 平台申诉/TRO 报告展示：
  - 报告标题和摘要。
  - 风险等级。
  - 分组建议 `sections`。
  - 下一步行动 `nextActions`。
  - “需要服务支持”模块。

二维码弹窗：

- 新增可复用 `ContactQrModal` 组件。
- 使用首页已有资产 `/wechat-qrcode-cropped.jpg`。
- 报告详情页服务支持按钮文案为“联系港港跨境”。
- 点击后打开弹窗，显示二维码和简短提示。
- 弹窗支持关闭按钮、点击遮罩关闭、Esc 关闭。

## 数据流

平台申诉/TRO 提交后：

1. 前端提交服务工单。
2. 后端生成 adviceReport。
3. 后端保存 service request，并把 adviceReport 写入 `details_json`。
4. 创建成功响应中返回 adviceReport，页面即时展示。
5. 用户进入“我的报告”时，`GET /api/reports` 合并读取该 adviceReport。
6. 用户点击查看后，`GET /api/reports/{serviceRequestId}` 返回统一报告详情。

## 错误处理

- 如果服务工单存在但没有 adviceReport，不进入“我的报告”。
- 如果 adviceReport JSON 解析失败，该工单在报告列表中跳过，并记录后端日志。
- 如果用户访问不属于自己的服务报告，返回 404。
- 如果联系二维码图片加载失败，弹窗仍显示联系提示文案。

## 测试计划

后端：

- 单元测试 `GET /api/reports` 的合并逻辑：检测报告、平台申诉、TRO 都能返回。
- 单元测试服务报告详情读取：当前用户可读，其他用户不可读。
- 单元测试来源标签：`model` 映射为“港港跨境AI”，`fallback` 映射为“港港跨境基础评估”。
- 单元测试身份 prompt：包含“港港跨境AI”，不包含“GPT”作为用户可见身份。

前端：

- 构建检查 `npm run build`。
- 手动验证“我的报告”出现三类卡片。
- 手动验证三类报告详情页颜色和标签不同。
- 手动验证“联系港港跨境”弹出二维码。

## 非目标

- 本次不做服务报告 PDF 下载。
- 本次不迁移历史检测报告表结构。
- 本次不做二维码后台可配置化，继续使用现有首页二维码资产。
