<template><section class="rounded-[2rem] border border-white/10 bg-panel/80 p-7 shadow-2xl md:p-10"><div class="grid gap-8 lg:grid-cols-[auto_1fr] lg:items-center"><div class="rounded-[1.5rem] border border-gold/25 bg-ink-2 p-7 text-center"><div class="text-sm font-bold text-slate-400">总体风险</div><div class="mt-4 text-7xl font-black text-gold">{{ riskScore }}</div><div class="mt-3 rounded-full px-4 py-2 text-sm font-bold" :style="{ color: meta.color, background: `${meta.color}20` }">{{ meta.label }}</div></div><div><h1 class="text-3xl font-black text-white md:text-5xl">{{ title }}</h1><p class="mt-5 text-base leading-8 text-slate-300">{{ summary }}</p></div></div></section></template>
<script setup lang="ts">
import { computed } from 'vue'
import { getRiskMeta } from '@/utils/risk'
import type { RiskLevel } from '@/types/domain'
const props = defineProps<{ riskLevel: RiskLevel; riskScore: number; title: string; summary: string }>()
const meta = computed(() => getRiskMeta(props.riskLevel))
</script>
