<template>
  <div class="space-y-6">
    <ServiceReportViewer v-if="isServiceReport" :report="report" @contact="$emit('contact')" />
    <template v-else>
    <div class="flex flex-col gap-3 rounded-3xl border border-slate-200/80 bg-white/80 p-5 shadow-sm shadow-blue-900/5 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p class="text-sm font-black text-blue-700">检测报告</p>
        <p class="mt-1 text-sm text-slate-500">报告日期：{{ report.generatedAt }}</p>
      </div>
      <span class="rounded-full bg-blue-50 px-4 py-2 text-sm font-black text-blue-700">报告编号：{{ report.id }}</span>
    </div>

    <RiskSummary :risk-level="report.riskLevel" :risk-score="report.riskScore ?? 0" :title="report.title" :summary="report.summary" />
    <OfficialTrademarkPanel v-if="officialEvidence.length" :evidence="officialEvidence" />
    <CategoryScoreGrid v-else :scores="report.categoryScores" />
    <SuggestionList :suggestions="report.suggestions" />
    <ReportActions :job-id="report.jobId" :review-status="report.reviewStatus ?? 'none'" :review-note="report.reviewNote ?? ''" />
    </template>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import RiskSummary from '@/components/results/RiskSummary.vue'
import CategoryScoreGrid from '@/components/results/CategoryScoreGrid.vue'
import OfficialTrademarkPanel from '@/components/results/OfficialTrademarkPanel.vue'
import SuggestionList from '@/components/results/SuggestionList.vue'
import ReportActions from '@/components/results/ReportActions.vue'
import ServiceReportViewer from '@/components/results/ServiceReportViewer.vue'
import type { DetectionReport } from '@/types/domain'
const props = defineProps<{ report: DetectionReport; mode?: 'result' | 'report' }>()
defineEmits<{ contact: [] }>()
const officialEvidence = computed(() => props.report.evidence.filter((item) => item.source.includes('USPTO')))
const isServiceReport = computed(() => props.report.reportType === 'appeal' || props.report.reportType === 'tro_settlement')
</script>
