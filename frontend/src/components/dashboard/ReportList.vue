<template>
  <section class="space-y-5">
    <div class="rounded-[2rem] border border-slate-200/80 bg-panel/75 p-5">
      <div class="grid gap-4 lg:grid-cols-[1fr_180px_180px]">
        <label class="text-sm font-semibold text-slate-950">
          搜索报告
          <input v-model="keyword" aria-label="搜索报告" class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900" placeholder="输入报告标题或编号" />
        </label>
        <label class="text-sm font-semibold text-slate-950">
          报告类型
          <select v-model="reportType" class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900">
            <option value="all">全部</option>
            <option value="ip_detection">知识产权检测</option>
            <option value="appeal">平台申诉</option>
            <option value="tro_settlement">TRO 和解</option>
          </select>
        </label>
        <label class="text-sm font-semibold text-slate-950">
          风险等级
          <select v-model="riskLevel" class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900">
            <option value="all">全部</option>
            <option value="high">高风险</option>
            <option value="medium">中风险</option>
            <option value="low">低风险</option>
          </select>
        </label>
      </div>
    </div>

    <div class="grid gap-4 md:grid-cols-2">
    <article v-for="report in filteredReports" :key="report.id" class="rounded-3xl border border-slate-200/80 bg-white/80 p-6">
      <div class="flex items-start justify-between gap-4">
        <div class="min-w-0">
          <span class="inline-flex w-fit whitespace-nowrap rounded-full px-3 py-1 text-xs font-black" :class="typeClass(report.reportType)">
            {{ report.typeLabel ?? '知识产权检测' }}
          </span>
          <h3 class="mt-3 text-lg font-bold leading-7 text-slate-950">{{ report.title }}</h3>
          <p class="mt-2 text-sm text-slate-500">生成时间：{{ report.generatedAt }}</p>
        </div>
        <span class="inline-flex min-w-[4.5rem] shrink-0 justify-center whitespace-nowrap rounded-full px-3 py-1 text-xs font-bold" :style="riskStyle(report.riskLevel)">
          {{ getRiskMeta(report.riskLevel).label }}
        </span>
      </div>
      <div class="mt-5 flex flex-col gap-3 sm:flex-row">
        <RouterLink :to="`/reports/${report.id}`" class="rounded-full bg-gold px-4 py-2 text-center text-sm font-bold text-white">
          查看报告
        </RouterLink>
        <button
          v-if="(report.reportType ?? 'ip_detection') === 'ip_detection'"
          type="button"
          :disabled="downloadingId === report.jobId"
          class="rounded-full border border-slate-200 px-4 py-2 text-sm font-bold text-slate-950 transition hover:border-gold disabled:cursor-not-allowed disabled:opacity-60"
          @click="downloadPdf(report.jobId)"
        >
          {{ downloadingId === report.jobId ? '下载中...' : '下载PDF' }}
        </button>
      </div>
      <p v-if="message && messageJobId === report.jobId" class="mt-3 text-sm text-slate-600">{{ message }}</p>
    </article>
    </div>
    <p v-if="filteredReports.length === 0" class="rounded-[2rem] border border-slate-200/80 bg-white/80 py-10 text-center text-slate-500">暂无匹配报告</p>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { downloadReportPdf } from '@/api/client'
import { getRiskMeta } from '@/utils/risk'
import type { DetectionReport, RiskLevel, UnifiedReportType } from '@/types/domain'

const props = defineProps<{ reports: DetectionReport[] }>()

const keyword = ref('')
const reportType = ref<UnifiedReportType | 'all'>('all')
const riskLevel = ref<Exclude<RiskLevel, 'pending'> | 'all'>('all')
const downloadingId = ref('')
const messageJobId = ref('')
const message = ref('')

const filteredReports = computed(() => props.reports.filter((report) => {
  const normalizedType = report.reportType ?? 'ip_detection'
  const words = `${report.id} ${report.jobId} ${report.title} ${report.typeLabel ?? ''}`.toLowerCase()
  const keywordMatched = words.includes(keyword.value.trim().toLowerCase())
  const typeMatched = reportType.value === 'all' || normalizedType === reportType.value
  const riskMatched = riskLevel.value === 'all' || report.riskLevel === riskLevel.value
  return keywordMatched && typeMatched && riskMatched
}))

function riskStyle(level: RiskLevel) {
  const meta = getRiskMeta(level)
  return { color: meta.color, background: meta.backgroundColor }
}

function typeClass(type: UnifiedReportType = 'ip_detection') {
  if (type === 'appeal') return 'bg-amber-100 text-amber-800'
  if (type === 'tro_settlement') return 'bg-orange-100 text-orange-800'
  return 'bg-blue-50 text-blue-700'
}

async function downloadPdf(jobId: string) {
  if (downloadingId.value) return
  downloadingId.value = jobId
  messageJobId.value = jobId
  message.value = ''
  try {
    const { blob, filename } = await downloadReportPdf(jobId)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    message.value = 'PDF报告已开始下载'
  } catch {
    message.value = '下载失败，请稍后重试'
  } finally {
    downloadingId.value = ''
  }
}
</script>
