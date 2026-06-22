<template><section class="rounded-[2rem] border border-slate-200/80 bg-panel/75 p-6"><div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"><div><p class="text-sm font-bold uppercase tracking-[0.3em] text-slate-700">任务进度</p><h2 class="mt-2 text-2xl font-black text-slate-950">{{ statusLabel }}</h2></div><span class="rounded-full px-4 py-2 text-sm font-bold" :class="statusClass">{{ statusLabel }}</span></div><div class="mt-6 grid gap-4 md:grid-cols-3"><div class="rounded-2xl border border-slate-200/80 bg-white/80 p-4"><p class="text-xs uppercase tracking-[0.25em] text-slate-500">风险等级</p><p class="mt-2 text-lg font-bold text-slate-950">{{ riskLabel }}</p></div><div class="rounded-2xl border border-slate-200/80 bg-white/80 p-4"><p class="text-xs uppercase tracking-[0.25em] text-slate-500">风险分</p><p class="mt-2 text-lg font-bold text-slate-950">{{ riskScoreLabel }}</p></div><div class="rounded-2xl border border-slate-200/80 bg-white/80 p-4"><p class="text-xs uppercase tracking-[0.25em] text-slate-500">复核状态</p><p class="mt-2 text-lg font-bold text-slate-950">{{ reviewLabel }}</p></div></div><div v-if="reviewNote" class="mt-4 rounded-2xl border border-gold/20 bg-gold/10 p-4 text-sm text-slate-700">复核备注：{{ reviewNote }}</div></section></template>
<script setup lang="ts">
import { computed } from 'vue'
import { getRiskMeta } from '@/utils/risk'
import type { DetectionJob } from '@/types/domain'
const props = defineProps<{ job: DetectionJob | null }>()
const statusMap: Record<DetectionJob['status'], { label: string; className: string }> = {
  queued: { label: '待检测', className: 'bg-white/80 text-slate-600 border border-slate-200/80' },
  processing: { label: '检测中', className: 'bg-gold/45 text-slate-700 border border-gold/60' },
  done: { label: '已完成', className: 'bg-white/80 text-slate-600 border border-slate-200/80' },
  failed: { label: '检测失败', className: 'bg-white/80 text-slate-600 border border-slate-200/80' },
}
const reviewMap = { none: '未申请', pending: '待人工复核', approved: '已通过复核', rejected: '已驳回复核' } as const
const statusLabel = computed(() => (props.job ? statusMap[props.job.status].label : '加载中'))
const statusClass = computed(() => (props.job ? statusMap[props.job.status].className : 'bg-white/80 text-slate-600 border border-slate-200/80'))
const riskLabel = computed(() => (props.job ? getRiskMeta(props.job.riskLevel).label : '—'))
const riskScoreLabel = computed(() => (props.job?.riskScore ?? '—'))
const reviewLabel = computed(() => reviewMap[props.job?.reviewStatus ?? 'none'])
const reviewNote = computed(() => props.job?.reviewNote ?? '')
</script>
