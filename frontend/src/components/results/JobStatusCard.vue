<template><section class="rounded-[2rem] border border-white/10 bg-panel/75 p-6"><div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"><div><p class="text-sm font-bold uppercase tracking-[0.3em] text-gold">任务进度</p><h2 class="mt-2 text-2xl font-black text-white">{{ statusLabel }}</h2></div><span class="rounded-full px-4 py-2 text-sm font-bold" :class="statusClass">{{ statusLabel }}</span></div><div class="mt-6 grid gap-4 md:grid-cols-3"><div class="rounded-2xl border border-white/10 bg-white/[0.04] p-4"><p class="text-xs uppercase tracking-[0.25em] text-slate-400">风险等级</p><p class="mt-2 text-lg font-bold text-white">{{ riskLabel }}</p></div><div class="rounded-2xl border border-white/10 bg-white/[0.04] p-4"><p class="text-xs uppercase tracking-[0.25em] text-slate-400">风险分</p><p class="mt-2 text-lg font-bold text-white">{{ riskScoreLabel }}</p></div><div class="rounded-2xl border border-white/10 bg-white/[0.04] p-4"><p class="text-xs uppercase tracking-[0.25em] text-slate-400">复核状态</p><p class="mt-2 text-lg font-bold text-white">{{ reviewLabel }}</p></div></div><div v-if="reviewNote" class="mt-4 rounded-2xl border border-gold/20 bg-gold/10 p-4 text-sm text-slate-200">复核备注：{{ reviewNote }}</div></section></template>
<script setup lang="ts">
import { computed } from 'vue'
import { getRiskMeta } from '@/utils/risk'
import type { DetectionJob } from '@/types/domain'
const props = defineProps<{ job: DetectionJob | null }>()
const statusMap: Record<DetectionJob['status'], { label: string; className: string }> = {
  queued: { label: '待检测', className: 'bg-white/8 text-slate-300 border border-white/10' },
  processing: { label: '检测中', className: 'bg-blue-500/15 text-blue-200 border border-blue-400/20' },
  done: { label: '已完成', className: 'bg-emerald-500/15 text-emerald-200 border border-emerald-400/20' },
  failed: { label: '检测失败', className: 'bg-red-500/15 text-red-200 border border-red-400/20' },
}
const reviewMap = { none: '未申请', pending: '待人工复核', approved: '已通过复核', rejected: '已驳回复核' } as const
const statusLabel = computed(() => (props.job ? statusMap[props.job.status].label : '加载中'))
const statusClass = computed(() => (props.job ? statusMap[props.job.status].className : 'bg-white/8 text-slate-300 border border-white/10'))
const riskLabel = computed(() => (props.job ? getRiskMeta(props.job.riskLevel).label : '—'))
const riskScoreLabel = computed(() => (props.job?.riskScore ?? '—'))
const reviewLabel = computed(() => reviewMap[props.job?.reviewStatus ?? 'none'])
const reviewNote = computed(() => props.job?.reviewNote ?? '')
</script>
