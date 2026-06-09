<template><div class="space-y-8"><div v-if="mode === 'report'" class="rounded-3xl border border-white/10 bg-white/[0.04] p-6"><p class="text-sm text-slate-400">报告日期：{{ report.generatedAt }}</p></div><RiskSummary :risk-level="report.riskLevel" :risk-score="report.riskScore" :title="report.title" :summary="report.summary" /><CategoryScoreGrid :scores="report.categoryScores" /><section><h2 class="mb-5 text-2xl font-black text-white">详细证据</h2><EvidenceList :evidence="report.evidence" /></section><SuggestionList :suggestions="report.suggestions" /><ReportActions :job-id="report.jobId" /></div></template>
<script setup lang="ts">
import RiskSummary from '@/components/results/RiskSummary.vue'
import CategoryScoreGrid from '@/components/results/CategoryScoreGrid.vue'
import EvidenceList from '@/components/results/EvidenceList.vue'
import SuggestionList from '@/components/results/SuggestionList.vue'
import ReportActions from '@/components/results/ReportActions.vue'
import type { DetectionReport } from '@/types/domain'
defineProps<{ report: DetectionReport; mode?: 'result' | 'report' }>()
</script>
