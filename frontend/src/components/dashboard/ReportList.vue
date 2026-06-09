<template><section class="grid gap-4 md:grid-cols-2"><article v-for="report in reports" :key="report.id" class="rounded-3xl border border-white/10 bg-white/[0.04] p-6"><div class="flex items-start justify-between gap-4"><div><h3 class="text-lg font-bold text-white">{{ report.title }}</h3><p class="mt-2 text-sm text-slate-400">生成时间：{{ report.generatedAt }}</p></div><span class="rounded-full px-3 py-1 text-xs font-bold" :style="riskStyle(report.riskLevel)">{{ getRiskMeta(report.riskLevel).label }}</span></div><div class="mt-5 flex gap-3"><RouterLink :to="`/reports/${report.jobId}`" class="rounded-full bg-gold px-4 py-2 text-sm font-bold text-ink">查看报告</RouterLink><a :href="downloadReportUrl(report.jobId)" class="rounded-full border border-white/15 px-4 py-2 text-sm font-bold text-white">下载PDF</a></div></article></section></template>
<script setup lang="ts">
import { downloadReportUrl } from '@/api/client'
import { getRiskMeta } from '@/utils/risk'
import type { DetectionReport, RiskLevel } from '@/types/domain'
defineProps<{ reports: DetectionReport[] }>()
function riskStyle(level: RiskLevel) { const meta = getRiskMeta(level); return { color: meta.color, background: `${meta.color}20` } }
</script>
