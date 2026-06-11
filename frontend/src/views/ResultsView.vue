<template><SiteHeader /><main class="mx-auto max-w-7xl px-5 py-12 lg:px-8"><div class="space-y-8"><JobStatusCard :job="jobStatus" /><ReportViewer v-if="report" :report="report" /><div v-else class="rounded-3xl border border-white/10 bg-panel/75 p-8 text-center text-slate-400">{{ loadingText }}</div></div></main><SiteFooter /></template>
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import JobStatusCard from '@/components/results/JobStatusCard.vue'
import ReportViewer from '@/components/results/ReportViewer.vue'
import { getJobResults, getJobStatus } from '@/api/client'
import type { DetectionJob, DetectionReport } from '@/types/domain'
const route = useRoute()
const report = ref<DetectionReport | null>(null)
const jobStatus = ref<DetectionJob | null>(null)
let timer: number | undefined
const loadingText = computed(() => jobStatus.value?.status === 'failed' ? '报告生成失败，请重新提交任务' : '报告生成中，请稍候')
async function loadData() {
  const id = String(route.params.id)
  jobStatus.value = await getJobStatus(id)
  if (jobStatus.value.status === 'done') {
    try {
      report.value = await getJobResults(id)
    } catch {
      report.value = null
    }
  }
  if (report.value || jobStatus.value.status === 'failed') window.clearInterval(timer)
}
onMounted(() => { loadData(); timer = window.setInterval(loadData, 2500) })
onUnmounted(() => window.clearInterval(timer))
</script>
