<template><section class="grid gap-5 md:grid-cols-3" aria-label="分项风险评分"><article v-for="score in scores" :key="score.type" class="rounded-3xl border border-white/10 bg-white/[0.04] p-6"><div class="flex items-center justify-between"><h2 class="text-lg font-bold text-white">{{ score.label }}</h2><span class="text-sm text-slate-400">命中 {{ score.hits }}</span></div><div class="mt-6 flex items-end gap-2"><span class="text-5xl font-black text-gold">{{ score.score }}</span><span class="pb-2 text-slate-500">/100</span></div><div class="mt-5 h-2 rounded-full bg-white/10"><div class="h-2 rounded-full bg-gradient-to-r from-gold to-ember" :style="{ width: `${score.score}%` }" /></div></article></section></template>
<script setup lang="ts">
import type { CategoryScore } from '@/types/domain'
defineProps<{ scores: CategoryScore[] }>()
</script>
