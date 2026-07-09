<template>
  <div class="space-y-6">
    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
      <article
        v-for="item in statItems"
        :key="item.label"
        class="rounded-lg border border-slate-200 bg-white p-4"
      >
        <p class="text-xs font-medium uppercase tracking-wide text-slate-500">{{ item.label }}</p>
        <p class="mt-2 text-2xl font-bold text-slate-950">{{ item.value }}</p>
        <p v-if="item.hint" class="mt-1 text-xs text-slate-500">{{ item.hint }}</p>
      </article>
    </section>

    <section class="rounded-lg border border-slate-200 bg-white">
      <div class="border-b border-slate-200 px-4">
        <div class="flex flex-wrap gap-2 py-3">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            type="button"
            class="rounded-lg px-3 py-2 text-sm font-medium transition"
            :class="tab.key === activeTab
              ? 'bg-slate-900 text-white'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'"
            @click="setActiveTab(tab.key)"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <div class="space-y-4 p-4">
        <div v-if="showKeywordFilter" class="max-w-sm">
          <label class="mb-2 block text-sm font-medium text-slate-700">关键词筛选</label>
          <input
            v-model.trim="keyword"
            type="text"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-900"
            placeholder="输入标题、手机号、用户姓名等"
          >
        </div>

        <div v-if="activeTab === 'overview'" class="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
          <div class="overflow-hidden rounded-lg border border-slate-200">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <tbody class="divide-y divide-slate-200 bg-white">
                <tr v-for="row in overviewRows" :key="row.label">
                  <th class="w-48 bg-slate-50 px-4 py-3 text-left font-medium text-slate-600">{{ row.label }}</th>
                  <td class="px-4 py-3 text-slate-950">{{ row.value }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <h2 class="text-base font-semibold text-slate-950">运营提示</h2>
            <dl class="mt-4 space-y-3 text-sm text-slate-600">
              <div class="flex items-center justify-between gap-4">
                <dt>高风险任务占比</dt>
                <dd class="font-semibold text-slate-950">{{ highRiskRateLabel }}</dd>
              </div>
              <div class="flex items-center justify-between gap-4">
                <dt>待复核任务</dt>
                <dd class="font-semibold text-slate-950">{{ props.overview.pendingReviews }}</dd>
              </div>
              <div class="flex items-center justify-between gap-4">
                <dt>未读消息</dt>
                <dd class="font-semibold text-slate-950">{{ props.overview.unreadNotifications }}</dd>
              </div>
            </dl>
          </div>
        </div>

        <div v-else-if="activeTab === 'users'" class="overflow-x-auto rounded-lg border border-slate-200">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-slate-600">
              <tr>
                <th class="px-4 py-3 text-left font-medium">用户</th>
                <th class="px-4 py-3 text-left font-medium">手机号</th>
                <th class="px-4 py-3 text-left font-medium">角色</th>
                <th class="px-4 py-3 text-left font-medium">注册时间</th>
                <th class="px-4 py-3 text-left font-medium">最近登录</th>
                <th class="px-4 py-3 text-right font-medium">登录次数</th>
                <th class="px-4 py-3 text-right font-medium">检测任务</th>
                <th class="px-4 py-3 text-right font-medium">报告</th>
                <th class="px-4 py-3 text-right font-medium">服务需求</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="row in filteredUsers" :key="row.id">
                <td class="px-4 py-3 font-medium text-slate-950">{{ row.name }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.mobile }}</td>
                <td class="px-4 py-3 text-slate-600">{{ roleLabel(row.role) }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.createdAt }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.lastLoginAt || '-' }}</td>
                <td class="px-4 py-3 text-right text-slate-950">{{ row.loginCount }}</td>
                <td class="px-4 py-3 text-right text-slate-950">{{ row.jobCount }}</td>
                <td class="px-4 py-3 text-right text-slate-950">{{ row.reportCount }}</td>
                <td class="px-4 py-3 text-right text-slate-950">{{ row.serviceRequestCount }}</td>
              </tr>
              <tr v-if="!filteredUsers.length">
                <td colspan="9" class="px-4 py-8 text-center text-slate-500">暂无匹配用户</td>
              </tr>
            </tbody>
          </table>
        </div>

        <AdminTaskTable v-else-if="activeTab === 'jobs'" :jobs="props.jobs" />

        <div v-else-if="activeTab === 'loginRecords'" class="overflow-x-auto rounded-lg border border-slate-200">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-slate-600">
              <tr>
                <th class="px-4 py-3 text-left font-medium">用户</th>
                <th class="px-4 py-3 text-left font-medium">手机号</th>
                <th class="px-4 py-3 text-left font-medium">角色</th>
                <th class="px-4 py-3 text-left font-medium">登录方式</th>
                <th class="px-4 py-3 text-left font-medium">IP</th>
                <th class="px-4 py-3 text-left font-medium">浏览器 / 设备</th>
                <th class="px-4 py-3 text-left font-medium">登录时间</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="row in filteredLoginRecords" :key="row.id">
                <td class="px-4 py-3 font-medium text-slate-950">{{ row.name }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.mobile }}</td>
                <td class="px-4 py-3 text-slate-600">{{ roleLabel(row.role) }}</td>
                <td class="px-4 py-3 text-slate-600">{{ loginMethodLabel(row.loginMethod) }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.ipAddress || '-' }}</td>
                <td class="max-w-xs truncate px-4 py-3 text-slate-600" :title="row.userAgent">{{ row.userAgent || '-' }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.createdAt }}</td>
              </tr>
              <tr v-if="!filteredLoginRecords.length">
                <td colspan="7" class="px-4 py-8 text-center text-slate-500">暂无匹配登录记录</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="activeTab === 'reports'" class="overflow-x-auto rounded-lg border border-slate-200">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-slate-600">
              <tr>
                <th class="px-4 py-3 text-left font-medium">报告标题</th>
                <th class="px-4 py-3 text-left font-medium">类型</th>
                <th class="px-4 py-3 text-left font-medium">用户</th>
                <th class="px-4 py-3 text-left font-medium">风险等级</th>
                <th class="px-4 py-3 text-left font-medium">风险分值</th>
                <th class="px-4 py-3 text-left font-medium">生成时间</th>
                <th class="px-4 py-3 text-left font-medium">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="row in filteredReports" :key="row.id">
                <td class="px-4 py-3 font-medium text-slate-950">{{ row.title }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.typeLabel }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.ownerName }} / {{ row.ownerMobile }}</td>
                <td class="px-4 py-3">
                  <span class="rounded-md px-2 py-1 text-xs font-semibold" :style="riskBadgeStyle(row.riskLevel)">
                    {{ getRiskMeta(row.riskLevel).label }}
                  </span>
                </td>
                <td class="px-4 py-3 text-slate-600">{{ row.riskScore ?? '-' }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.generatedAt }}</td>
                <td class="px-4 py-3">
                  <RouterLink class="text-sm font-medium text-slate-900 underline-offset-2 hover:underline" :to="`/reports/${row.linkId}`">
                    查看报告
                  </RouterLink>
                </td>
              </tr>
              <tr v-if="!filteredReports.length">
                <td colspan="7" class="px-4 py-8 text-center text-slate-500">暂无匹配报告</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-else-if="activeTab === 'serviceRequests'"
          class="overflow-x-auto rounded-lg border border-slate-200"
        >
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-slate-600">
              <tr>
                <th class="px-4 py-3 text-left font-medium">需求标题</th>
                <th class="px-4 py-3 text-left font-medium">类型</th>
                <th class="px-4 py-3 text-left font-medium">平台</th>
                <th class="px-4 py-3 text-left font-medium">状态</th>
                <th class="px-4 py-3 text-left font-medium">联系人</th>
                <th class="px-4 py-3 text-left font-medium">用户</th>
                <th class="px-4 py-3 text-left font-medium">创建时间</th>
                <th class="px-4 py-3 text-left font-medium">报告</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="row in filteredServiceRequests" :key="row.id">
                <td class="px-4 py-3 font-medium text-slate-950">{{ row.title }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.typeLabel }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.platform }}</td>
                <td class="px-4 py-3 text-slate-600">{{ serviceStatusLabel(row.status) }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.contact }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.ownerName }} / {{ row.ownerMobile }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.createdAt }}</td>
                <td class="px-4 py-3">
                  <RouterLink class="text-sm font-medium text-slate-900 underline-offset-2 hover:underline" :to="`/reports/${row.linkId}`">
                    查看报告
                  </RouterLink>
                </td>
              </tr>
              <tr v-if="!filteredServiceRequests.length">
                <td colspan="8" class="px-4 py-8 text-center text-slate-500">暂无匹配服务需求</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-else-if="activeTab === 'notifications'"
          class="overflow-x-auto rounded-lg border border-slate-200"
        >
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-slate-600">
              <tr>
                <th class="px-4 py-3 text-left font-medium">标题</th>
                <th class="px-4 py-3 text-left font-medium">内容</th>
                <th class="px-4 py-3 text-left font-medium">类型</th>
                <th class="px-4 py-3 text-left font-medium">状态</th>
                <th class="px-4 py-3 text-left font-medium">用户</th>
                <th class="px-4 py-3 text-left font-medium">创建时间</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="row in filteredNotifications" :key="row.id">
                <td class="px-4 py-3 font-medium text-slate-950">{{ row.title }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.content }}</td>
                <td class="px-4 py-3 text-slate-600">{{ notificationTypeLabel(row.type) }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.isRead ? '已读' : '未读' }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.ownerName }} / {{ row.ownerMobile }}</td>
                <td class="px-4 py-3 text-slate-600">{{ row.createdAt }}</td>
              </tr>
              <tr v-if="!filteredNotifications.length">
                <td colspan="6" class="px-4 py-8 text-center text-slate-500">暂无匹配消息</td>
              </tr>
            </tbody>
          </table>
        </div>

        <ModelConfigPanel v-else />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AdminTaskTable from '@/components/admin/AdminTaskTable.vue'
import ModelConfigPanel from '@/components/admin/ModelConfigPanel.vue'
import type {
  AdminNotificationRow,
  AdminLoginRecordRow,
  AdminOverview,
  AdminReportRow,
  AdminServiceRequestRow,
  AdminUserRow,
  DetectionJob,
  RiskLevel,
  ServiceRequestStatus,
  UserRole,
} from '@/types/domain'
import { getRiskMeta } from '@/utils/risk'

const props = defineProps<{
  overview: AdminOverview
  jobs: DetectionJob[]
  users: AdminUserRow[]
  reports: AdminReportRow[]
  serviceRequests: AdminServiceRequestRow[]
  notifications: AdminNotificationRow[]
  loginRecords: AdminLoginRecordRow[]
}>()

const tabs = [
  { key: 'overview', label: '概览' },
  { key: 'users', label: '用户' },
  { key: 'jobs', label: '检测任务' },
  { key: 'loginRecords', label: '登录记录' },
  { key: 'reports', label: '报告' },
  { key: 'serviceRequests', label: '服务需求' },
  { key: 'notifications', label: '消息' },
  { key: 'modelConfig', label: '港港跨境AI配置' },
] as const

type TabKey = (typeof tabs)[number]['key']

const activeTab = ref<TabKey>('overview')
const keyword = ref('')

const statItems = computed(() => [
  { label: '总用户数', value: props.overview.totalUsers },
  { label: '检测任务数', value: props.overview.totalJobs },
  { label: '报告数', value: props.overview.totalReports },
  { label: '服务需求数', value: props.overview.totalServiceRequests },
  { label: '未读消息', value: props.overview.unreadNotifications },
  { label: '待复核任务', value: props.overview.pendingReviews, hint: `已完成 ${props.overview.completedJobs}` },
])

const highRiskRateLabel = computed(() => `${Math.round(props.overview.highRiskRate * 100)}%`)

const overviewRows = computed(() => [
  { label: '总用户数', value: props.overview.totalUsers },
  { label: '检测任务数', value: props.overview.totalJobs },
  { label: '已完成任务', value: props.overview.completedJobs },
  { label: '报告数', value: props.overview.totalReports },
  { label: '服务需求数', value: props.overview.totalServiceRequests },
  { label: '未读消息', value: props.overview.unreadNotifications },
  { label: '待复核任务', value: props.overview.pendingReviews },
  { label: '高风险任务占比', value: highRiskRateLabel.value },
])

const showKeywordFilter = computed(() => activeTab.value !== 'overview' && activeTab.value !== 'modelConfig' && activeTab.value !== 'jobs')

function includesKeyword(values: Array<string | number | null | undefined>) {
  const text = values.filter(Boolean).join(' ').toLowerCase()
  return text.includes(keyword.value.toLowerCase())
}

const filteredUsers = computed(() =>
  props.users.filter((row) =>
    includesKeyword([row.name, row.mobile, row.role, row.createdAt, row.lastLoginAt]),
  ),
)

const filteredReports = computed(() =>
  props.reports.filter((row) =>
    includesKeyword([row.title, row.typeLabel, row.ownerName, row.ownerMobile, row.generatedAt]),
  ),
)

const filteredLoginRecords = computed(() =>
  props.loginRecords.filter((row) =>
    includesKeyword([
      row.name,
      row.mobile,
      row.role,
      row.loginMethod,
      row.ipAddress,
      row.userAgent,
      row.createdAt,
    ]),
  ),
)

const filteredServiceRequests = computed(() =>
  props.serviceRequests.filter((row) =>
    includesKeyword([
      row.title,
      row.typeLabel,
      row.platform,
      row.status,
      row.contact,
      row.ownerName,
      row.ownerMobile,
      row.createdAt,
    ]),
  ),
)

const filteredNotifications = computed(() =>
  props.notifications.filter((row) =>
    includesKeyword([
      row.title,
      row.content,
      row.type,
      row.ownerName,
      row.ownerMobile,
      row.createdAt,
      row.isRead ? '已读' : '未读',
    ]),
  ),
)

function setActiveTab(tab: TabKey) {
  activeTab.value = tab
  keyword.value = ''
}

function roleLabel(role: UserRole) {
  return role === 'admin' ? '管理员' : '用户'
}

function loginMethodLabel(method: string) {
  return {
    password: '密码登录',
    sms_code: '验证码登录',
    register: '注册登录',
  }[method] ?? method
}

function serviceStatusLabel(status: ServiceRequestStatus) {
  return {
    pending: '待处理',
    reviewing: '审核中',
    waiting_user: '待用户补充',
    processing: '处理中',
    done: '已完成',
  }[status]
}

function notificationTypeLabel(type: string) {
  return {
    review: '复核提醒',
    report: '报告提醒',
    service_request: '服务需求',
  }[type] ?? type
}

function riskBadgeStyle(level: RiskLevel) {
  const meta = getRiskMeta(level)
  return {
    color: meta.color,
    backgroundColor: meta.backgroundColor,
  }
}
</script>
