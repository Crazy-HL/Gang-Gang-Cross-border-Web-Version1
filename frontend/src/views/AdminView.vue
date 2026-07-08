<template>
  <SiteHeader />
  <main class="mx-auto max-w-7xl px-5 py-10 lg:px-8">
    <div class="mb-8 flex items-end justify-between gap-4">
      <div>
        <p class="text-sm font-bold uppercase tracking-[0.35em] text-slate-700">Admin</p>
        <h1 class="mt-3 text-3xl font-black text-slate-950">运营管理后台</h1>
      </div>
      <button
        type="button"
        class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:text-slate-950"
        :disabled="loading"
        @click="loadAdminConsole"
      >
        {{ loading ? '刷新中' : '刷新数据' }}
      </button>
    </div>

    <div
      v-if="loading && !overview && !forbidden && !error"
      class="rounded-lg border border-slate-200 bg-white p-10 text-center text-sm text-slate-500"
    >
      正在加载管理员后台数据...
    </div>

    <div
      v-else-if="forbidden && !overview"
      class="rounded-lg border border-amber-200 bg-amber-50 p-10 text-center"
    >
      <p class="text-sm font-medium text-amber-800">{{ error }}</p>
      <p class="mt-2 text-sm text-amber-700">请使用管理员账号重新登录后再访问。</p>
    </div>

    <div
      v-else-if="error && !overview"
      class="rounded-lg border border-rose-200 bg-rose-50 p-10 text-center"
    >
      <p class="text-sm font-medium text-rose-700">{{ error }}</p>
      <button
        type="button"
        class="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
        @click="loadAdminConsole"
      >
        重试
      </button>
    </div>

    <div v-else-if="overview" class="space-y-4">
      <div
        v-if="warning"
        class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700"
      >
        {{ warning }}
      </div>
      <AdminDashboard
        :overview="overview"
        :jobs="jobs"
        :users="users"
        :reports="reports"
        :service-requests="serviceRequests"
        :notifications="notifications"
      />
    </div>
  </main>
  <SiteFooter />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import AdminDashboard from '@/components/admin/AdminDashboard.vue'
import {
  ApiError,
  getAdminJobs,
  getAdminNotifications,
  getAdminOverview,
  getAdminReports,
  getAdminServiceRequests,
  getAdminUsers,
} from '@/api/client'
import type {
  AdminNotificationRow,
  AdminOverview,
  AdminReportRow,
  AdminServiceRequestRow,
  AdminUserRow,
  DetectionJob,
} from '@/types/domain'

const overview = ref<AdminOverview | null>(null)
const jobs = ref<DetectionJob[]>([])
const users = ref<AdminUserRow[]>([])
const reports = ref<AdminReportRow[]>([])
const serviceRequests = ref<AdminServiceRequestRow[]>([])
const notifications = ref<AdminNotificationRow[]>([])
const loading = ref(true)
const error = ref('')
const warning = ref('')
const forbidden = ref(false)

function resetAdminData() {
  overview.value = null
  jobs.value = []
  users.value = []
  reports.value = []
  serviceRequests.value = []
  notifications.value = []
}

function isForbiddenReason(reason: unknown) {
  return reason instanceof ApiError && reason.status === 403
}

async function loadAdminConsole() {
  loading.value = true
  error.value = ''
  warning.value = ''
  forbidden.value = false
  try {
    const [overviewResult, jobsResult, usersResult, reportsResult, serviceRequestsResult, notificationsResult] =
      await Promise.allSettled([
        getAdminOverview(),
        getAdminJobs(),
        getAdminUsers(),
        getAdminReports(),
        getAdminServiceRequests(),
        getAdminNotifications(),
      ])

    const results = [overviewResult, jobsResult, usersResult, reportsResult, serviceRequestsResult, notificationsResult]
    if (results.some((result) => result.status === 'rejected' && isForbiddenReason(result.reason))) {
      resetAdminData()
      forbidden.value = true
      error.value = '当前账号没有管理员权限，无法查看后台数据'
      return
    }

    if (overviewResult.status === 'rejected') {
      resetAdminData()
      error.value = '管理员后台数据加载失败，请稍后重试'
      return
    }

    overview.value = overviewResult.value
    jobs.value = jobsResult.status === 'fulfilled' ? jobsResult.value.jobs : []
    users.value = usersResult.status === 'fulfilled' ? usersResult.value : []
    reports.value = reportsResult.status === 'fulfilled' ? reportsResult.value : []
    serviceRequests.value = serviceRequestsResult.status === 'fulfilled' ? serviceRequestsResult.value : []
    notifications.value = notificationsResult.status === 'fulfilled' ? notificationsResult.value : []

    if ([jobsResult, usersResult, reportsResult, serviceRequestsResult, notificationsResult].some((result) => result.status === 'rejected')) {
      warning.value = '部分后台数据加载失败，已展示可用内容。'
    }
  } catch {
    resetAdminData()
    error.value = '管理员后台数据加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadAdminConsole()
})
</script>
