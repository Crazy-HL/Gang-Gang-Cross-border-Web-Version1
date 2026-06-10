<template><div v-if="evidence.length === 0" class="rounded-3xl border border-white/10 bg-panel/70 p-8 text-center text-slate-400">未发现疑似侵权</div><section v-else class="space-y-4" aria-label="命中证据列表"><article v-for="item in evidence" :key="item.id" class="overflow-hidden rounded-3xl border border-white/10 bg-panel/75"><button type="button" :aria-expanded="openId === item.id" class="flex w-full flex-col gap-4 p-6 text-left transition hover:bg-white/[0.04] md:flex-row md:items-center md:justify-between" @click="openId = openId === item.id ? null : item.id"><span><span class="block text-lg font-bold text-white">{{ item.matched }}</span><span class="mt-1 block text-sm text-slate-400">来源：{{ item.source }}</span></span><span class="rounded-full bg-gold/15 px-4 py-2 text-sm font-bold text-gold">相似度 {{ formatPercent(item.similarity) }}</span></button><div v-if="openId === item.id" class="border-t border-white/10 p-6"><div class="grid gap-5 md:grid-cols-[160px_1fr]"><img :src="assetUrl(item.imageUrl)" :alt="`${item.matched} evidence`" class="h-36 w-full rounded-2xl border border-gold/20 bg-ink-2 object-cover" /><p class="text-sm leading-7 text-slate-300">{{ item.description }}</p></div></div></article></section></template>
<script setup lang="ts">
import { ref } from 'vue'
import { formatPercent } from '@/utils/risk'
import type { EvidenceItem } from '@/types/domain'
defineProps<{ evidence: EvidenceItem[] }>()
const openId = ref<string | null>(null)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
function assetUrl(path: string) { return path.startsWith('http') ? path : `${API_BASE_URL}${path}` }
</script>
