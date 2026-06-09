<template><SiteHeader /><main class="mx-auto max-w-6xl px-5 py-12 print:max-w-none lg:px-8"><ReportViewer v-if="report" :report="report" mode="report" /><div v-else class="rounded-3xl border border-white/10 bg-panel/75 p-8 text-center text-slate-400">报告加载中或不存在</div></main><SiteFooter /></template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import ReportViewer from '@/components/results/ReportViewer.vue'
import { getReport } from '@/api/client'
import type { DetectionReport } from '@/types/domain'
const route = useRoute()
const report = ref<DetectionReport | null>(null)
onMounted(async () => { report.value = await getReport(String(route.params.id)) })
</script>
