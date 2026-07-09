<template>
  <div class="grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_360px]">
    <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div class="border-b border-slate-200 px-4 py-3">
        <label class="block text-sm font-medium text-slate-700">
          搜索管理员任务
          <input
            v-model.trim="keyword"
            class="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-900"
            placeholder="输入任务标题、任务ID、用户姓名或手机号"
          >
        </label>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-slate-600">
            <tr>
              <th class="px-4 py-3 text-left font-medium">任务标题</th>
              <th class="px-4 py-3 text-left font-medium">用户</th>
              <th class="px-4 py-3 text-left font-medium">市场 / 品类</th>
              <th class="px-4 py-3 text-left font-medium">风险等级</th>
              <th class="px-4 py-3 text-left font-medium">复核状态</th>
              <th class="px-4 py-3 text-left font-medium">创建时间</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 bg-white">
            <tr
              v-for="job in filteredJobs"
              :key="job.id"
              class="cursor-pointer transition hover:bg-slate-50"
              :class="selectedId === job.id ? 'bg-slate-50' : ''"
              @click="selectedId = job.id"
            >
              <td class="px-4 py-3">
                <div class="font-medium text-slate-950">{{ job.title }}</div>
                <div class="mt-1 text-xs text-slate-500">任务 {{ job.id }}</div>
              </td>
              <td class="px-4 py-3 text-slate-600">{{ job.ownerName }} / {{ job.ownerMobile || '-' }}</td>
              <td class="px-4 py-3 text-slate-600">{{ job.market }} / {{ job.category }}</td>
              <td class="px-4 py-3">
                <span
                  class="rounded-md px-2 py-1 text-xs font-semibold"
                  :style="riskBadgeStyle(job.riskLevel)"
                >
                  {{ getRiskMeta(job.riskLevel).label }}
                </span>
              </td>
              <td class="px-4 py-3 text-slate-600">{{ reviewLabels[job.reviewStatus ?? 'none'] }}</td>
              <td class="px-4 py-3 text-slate-600">{{ job.createdAt }}</td>
            </tr>
            <tr v-if="!filteredJobs.length">
              <td colspan="6" class="px-4 py-8 text-center text-slate-500">暂无匹配任务</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <aside class="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <h2 class="text-base font-semibold text-slate-950">任务详情</h2>

      <div v-if="selectedJob" class="mt-4 space-y-4 text-sm text-slate-600">
        <dl class="grid gap-3">
          <div class="grid gap-1">
            <dt class="text-xs font-medium uppercase tracking-wide text-slate-500">任务标题</dt>
            <dd class="font-medium text-slate-950">{{ selectedJob.title }}</dd>
          </div>
          <div class="grid gap-1">
            <dt class="text-xs font-medium uppercase tracking-wide text-slate-500">任务信息</dt>
            <dd>任务ID：{{ selectedJob.id }}</dd>
            <dd>用户：{{ selectedJob.ownerName }} / {{ selectedJob.ownerMobile || '-' }}</dd>
            <dd>品牌：{{ selectedJob.brand }}</dd>
            <dd>市场：{{ selectedJob.market }}</dd>
          </div>
          <div class="grid gap-1">
            <dt class="text-xs font-medium uppercase tracking-wide text-slate-500">复核状态</dt>
            <dd>{{ reviewLabels[selectedJob.reviewStatus ?? 'none'] }}</dd>
            <dd v-if="selectedJob.reviewNote">备注：{{ selectedJob.reviewNote }}</dd>
          </div>
        </dl>

        <img
          v-if="selectedJob.fileUrl"
          :src="assetUrl(selectedJob.fileUrl)"
          :alt="selectedJob.title"
          class="h-40 w-full rounded-lg border border-slate-200 bg-white object-cover"
        >
        <div
          v-else
          class="grid h-40 place-items-center rounded-lg border border-dashed border-slate-300 bg-white text-slate-500"
        >
          暂无原始文件
        </div>

        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <label class="block text-sm font-medium text-slate-700">
            复核处理备注
            <textarea
              v-model="adminNote"
              rows="4"
              class="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-900"
              placeholder="填写复核处理意见"
            />
          </label>

          <div class="mt-4 flex flex-col gap-2">
            <button
              type="button"
              :disabled="submitting"
              class="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
              @click="handleReview('approved')"
            >
              通过复核
            </button>
            <button
              type="button"
              :disabled="submitting"
              class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 disabled:opacity-60"
              @click="handleReview('rejected')"
            >
              驳回复核
            </button>
          </div>

          <p v-if="message" class="mt-3 text-sm text-slate-700">{{ message }}</p>
        </div>
      </div>

      <div v-else class="mt-4 rounded-lg border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">
        请选择左侧任务查看详情。
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { updateAdminJobReview } from '@/api/client'
import { getRiskMeta } from '@/utils/risk'
import type { DetectionJob, ReviewStatus, RiskLevel } from '@/types/domain'

const props = defineProps<{ jobs: DetectionJob[] }>()

const localJobs = ref([...props.jobs])
const keyword = ref('')
const selectedId = ref(props.jobs[0]?.id ?? '')
const adminNote = ref('')
const message = ref('')
const submitting = ref(false)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const reviewLabels: Record<ReviewStatus, string> = { none: '未申请', pending: '待人工复核', approved: '已通过复核', rejected: '已驳回复核' }
const selectedJob = computed(() => localJobs.value.find((job) => job.id === selectedId.value) ?? localJobs.value[0])
const filteredJobs = computed(() => localJobs.value.filter((job) => `${job.ownerName} ${job.ownerMobile} ${job.title} ${job.id}`.toLowerCase().includes(keyword.value.toLowerCase())))
function assetUrl(path: string) { return path.startsWith('http') ? path : `${API_BASE_URL}${path}` }
function riskBadgeStyle(level: RiskLevel) {
  const meta = getRiskMeta(level)
  return { color: meta.color, backgroundColor: meta.backgroundColor }
}
async function handleReview(status: 'approved' | 'rejected') { if (!selectedJob.value || submitting.value) return; submitting.value = true; message.value = ''; try { const updated = await updateAdminJobReview(selectedJob.value.id, status, adminNote.value); localJobs.value = localJobs.value.map((job) => job.id === updated.id ? updated : job); message.value = status === 'approved' ? '已通过复核' : '已驳回复核' } catch { message.value = '处理失败，请稍后重试' } finally { submitting.value = false } }

watch(
  () => props.jobs,
  (jobs) => {
    localJobs.value = [...jobs]
    if (!jobs.some((job) => job.id === selectedId.value)) {
      selectedId.value = jobs[0]?.id ?? ''
    }
  },
  { deep: true },
)
</script>
