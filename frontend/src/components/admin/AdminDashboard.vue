<template><div class="space-y-8"><div class="grid gap-5 md:grid-cols-4"><article v-for="item in statItems" :key="item.label" class="rounded-3xl border border-white/10 bg-panel/75 p-6"><p class="text-sm text-slate-400">{{ item.label }}</p><div class="mt-3 text-3xl font-black text-gold">{{ item.value }}</div></article></div><section class="rounded-[2rem] border border-white/10 bg-panel/75 p-6"><h2 class="text-xl font-bold text-white">风险分布</h2><div class="mt-5 h-4 overflow-hidden rounded-full bg-white/10"><div class="h-full w-[31%] bg-red-500" /></div><p class="mt-3 text-sm text-slate-400">高风险任务占比 31%，建议运营优先处理。</p></section><ModelConfigPanel /><AdminTaskTable :jobs="jobs" /></div></template>
<script setup lang="ts">
import { computed } from 'vue'
import AdminTaskTable from '@/components/admin/AdminTaskTable.vue'
import ModelConfigPanel from '@/components/admin/ModelConfigPanel.vue'
import type { AdminStats, DetectionJob } from '@/types/domain'
const props = defineProps<{ stats: AdminStats; jobs: DetectionJob[] }>()
const statItems = computed(() => [['总任务数', props.stats.totalJobs], ['总用户数', props.stats.totalUsers], ['已完成', props.stats.completedJobs], ['高风险占比', `${Math.round(props.stats.highRiskRate * 100)}%`]].map(([label, value]) => ({ label, value })))
</script>
