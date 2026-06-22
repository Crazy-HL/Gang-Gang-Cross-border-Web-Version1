<template><SiteHeader /><main class="mx-auto max-w-7xl px-5 py-12 lg:px-8"><div class="space-y-8"><ReportViewer v-if="report" :report="report" /><ReportProgressCard v-else :job="jobStatus" /></div></main><SiteFooter /></template>
<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import ReportViewer from '@/components/results/ReportViewer.vue'
import ReportProgressCard from '@/components/results/ReportProgressCard.vue'
import { getJobResults, getJobStatus } from '@/api/client'
import type { DetectionJob, DetectionReport } from '@/types/domain'
const route = useRoute()
const report = ref<DetectionReport | null>(null)
const jobStatus = ref<DetectionJob | null>(null)
let timer: number | undefined
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
