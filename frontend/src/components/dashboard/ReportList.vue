<template>
  <section class="grid gap-4 md:grid-cols-2">
    <article v-for="report in reports" :key="report.id" class="rounded-3xl border border-slate-200/80 bg-white/80 p-6">
      <div class="flex items-start justify-between gap-4">
        <div>
          <h3 class="text-lg font-bold text-slate-950">{{ report.title }}</h3>
          <p class="mt-2 text-sm text-slate-500">生成时间：{{ report.generatedAt }}</p>
        </div>
        <span class="rounded-full px-3 py-1 text-xs font-bold" :style="riskStyle(report.riskLevel)">
          {{ getRiskMeta(report.riskLevel).label }}
        </span>
      </div>
      <div class="mt-5 flex flex-col gap-3 sm:flex-row">
        <RouterLink :to="`/reports/${report.jobId}`" class="rounded-full bg-gold px-4 py-2 text-center text-sm font-bold text-white">
          查看报告
        </RouterLink>
        <button
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
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { downloadReportPdf } from '@/api/client'
import { getRiskMeta } from '@/utils/risk'
import type { DetectionReport, RiskLevel } from '@/types/domain'

defineProps<{ reports: DetectionReport[] }>()

const downloadingId = ref('')
const messageJobId = ref('')
const message = ref('')

function riskStyle(level: RiskLevel) {
  const meta = getRiskMeta(level)
  return { color: meta.color, background: meta.backgroundColor }
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
