<template>
  <section class="grid gap-5 md:grid-cols-3" aria-label="分项风险评分">
    <article
      v-for="score in scores"
      :key="score.type"
      class="rounded-[1.75rem] border bg-white/85 p-5 shadow-sm shadow-blue-900/5"
      :class="tone(score).card"
    >
      <div class="flex items-start justify-between gap-4">
        <div>
          <h2 class="text-lg font-black text-slate-950">{{ score.label }}</h2>
          <p class="mt-1 text-xs font-bold text-slate-500">{{ description(score.type) }}</p>
        </div>
        <span class="rounded-full px-3 py-1 text-xs font-black" :class="tone(score).badge">{{ riskText(score.score) }}</span>
      </div>

      <div class="mt-6 flex items-end gap-2">
        <span class="text-5xl font-black text-slate-950">{{ score.score }}</span>
        <span class="pb-2 text-sm font-bold text-slate-400">/100</span>
      </div>

      <div class="mt-5 h-2.5 overflow-hidden rounded-full bg-slate-100">
        <div class="h-full rounded-full transition-all duration-500" :class="tone(score).bar" :style="{ width: `${score.score}%` }" />
      </div>

      <p class="mt-4 text-sm leading-6 text-slate-600">{{ hint(score) }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import type { CategoryScore } from '@/types/domain'

defineProps<{ scores: CategoryScore[] }>()

function riskText(score: number) {
  if (score >= 75) return '重点处理'
  if (score >= 45) return '建议确认'
  return '风险较低'
}

function tone(score: CategoryScore) {
  if (score.score >= 75) return { card: 'border-orange-200', badge: 'bg-orange-100 text-orange-800', bar: 'bg-orange-500' }
  if (score.score >= 45) return { card: 'border-amber-200', badge: 'bg-amber-100 text-amber-800', bar: 'bg-amber-400' }
  return { card: 'border-blue-100', badge: 'bg-blue-50 text-blue-700', bar: 'bg-blue-500' }
}

function description(type: CategoryScore['type']) {
  const map = {
    trademark: '品牌名、Logo、联名表达',
    design: '外观造型、包装和结构',
    copyright: '图片、图案、文案和素材',
  }
  return map[type] ?? '上架前常见风险'
}

function hint(score: CategoryScore) {
  if (score.score >= 75) return '建议先处理这一项，再继续上架或投放。'
  if (score.score >= 45) return '建议补充资料或人工复核后再推进。'
  return '当前预检压力较小，仍建议保留来源证明。'
}
</script>
