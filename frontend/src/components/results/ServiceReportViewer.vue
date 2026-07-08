<template>
  <div class="space-y-6">
    <section class="rounded-[2rem] border p-6 shadow-2xl md:p-8" :class="tone.surface">
      <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="rounded-full px-4 py-2 text-sm font-black" :class="tone.badge">{{ report.typeLabel }}</span>
            <span class="rounded-full bg-white/80 px-4 py-2 text-sm font-black text-slate-700">{{ report.sourceLabel ?? '港港跨境AI' }}</span>
          </div>
          <h1 class="mt-5 text-3xl font-black leading-tight text-slate-950 md:text-5xl">{{ report.title }}</h1>
          <p class="mt-5 max-w-4xl text-base leading-8 text-slate-700">{{ report.summary }}</p>
        </div>
        <span class="inline-flex min-w-[4.5rem] w-fit shrink-0 justify-center whitespace-nowrap rounded-full px-4 py-2 text-sm font-black" :style="riskStyle(report.riskLevel)">
          {{ getRiskMeta(report.riskLevel).label }}
        </span>
      </div>
    </section>

    <section class="grid gap-4 lg:grid-cols-3">
      <article v-for="section in report.sections ?? []" :key="section.title" class="rounded-2xl border border-slate-200/80 bg-white/85 p-5">
        <h2 class="text-base font-black text-slate-950">{{ section.title }}</h2>
        <ul class="mt-3 space-y-2 text-sm leading-6 text-slate-600">
          <li v-for="item in section.items" :key="item">· {{ item }}</li>
        </ul>
      </article>
    </section>

    <section class="grid gap-4 lg:grid-cols-[1fr_0.42fr]">
      <div class="rounded-2xl border border-slate-200/80 bg-white/85 p-5">
        <h2 class="text-base font-black text-slate-950">下一步行动</h2>
        <ol class="mt-3 space-y-2 text-sm leading-6 text-slate-600">
          <li v-for="(item, index) in report.nextActions ?? report.suggestions" :key="item">{{ index + 1 }}. {{ item }}</li>
        </ol>
      </div>
      <aside class="rounded-2xl border border-orange-200 bg-orange-50 p-5">
        <p class="text-xs font-black text-orange-800">需要服务支持</p>
        <h2 class="mt-2 text-xl font-black text-slate-950">联系我们继续处理</h2>
        <p class="mt-2 text-sm leading-6 text-slate-600">如需人工申诉、和解协助或材料整理，请联系港港跨境并提供报告编号。</p>
        <button type="button" class="mt-4 inline-flex rounded-full bg-gold px-5 py-3 text-sm font-black text-white shadow-glow transition hover:bg-blue-600" @click="$emit('contact')">
          联系港港跨境
        </button>
      </aside>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getRiskMeta } from '@/utils/risk'
import type { DetectionReport, RiskLevel, UnifiedReportType } from '@/types/domain'

const props = defineProps<{ report: DetectionReport }>()
defineEmits<{ contact: [] }>()

const tone = computed(() => reportTone(props.report.reportType ?? 'appeal'))

function reportTone(type: UnifiedReportType) {
  if (type === 'tro_settlement') return { surface: 'border-orange-200 bg-orange-50', badge: 'bg-orange-100 text-orange-800' }
  return { surface: 'border-amber-200 bg-amber-50', badge: 'bg-amber-100 text-amber-800' }
}

function riskStyle(level: RiskLevel) {
  const meta = getRiskMeta(level)
  return { color: meta.color, background: meta.backgroundColor }
}
</script>
