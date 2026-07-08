<template>
  <section
    class="overflow-hidden rounded-[2rem] border p-6 shadow-2xl md:p-8"
    :style="{ background: meta.surfaceColor, borderColor: meta.borderColor }"
  >
    <div class="grid gap-7 lg:grid-cols-[220px_1fr] lg:items-center">
      <div
        class="grid place-items-center rounded-[1.5rem] border bg-white/75 p-5 text-center"
        :style="{ borderColor: meta.borderColor }"
      >
        <div
          class="grid h-36 w-36 place-items-center rounded-full"
          :style="{ background: scoreRing }"
        >
          <div class="grid h-28 w-28 place-items-center rounded-full bg-white">
            <div>
              <div class="text-5xl font-black" :style="{ color: meta.color }">{{ riskScore }}</div>
              <div class="text-xs font-bold text-slate-400">/ 100</div>
            </div>
          </div>
        </div>
        <div class="mt-4 min-w-[4.5rem] whitespace-nowrap rounded-full px-4 py-2 text-center text-sm font-black" :style="{ color: meta.color, background: meta.backgroundColor }">{{ meta.label }}</div>
      </div>

      <div>
        <div class="flex flex-wrap items-center gap-3">
          <span class="rounded-full bg-white/80 px-4 py-2 text-sm font-black text-slate-700">检测结论</span>
          <span class="whitespace-nowrap rounded-full px-4 py-2 text-sm font-black" :style="{ color: meta.color, background: meta.backgroundColor }">{{ conclusion }}</span>
        </div>
        <h1 class="mt-5 text-3xl font-black leading-tight text-slate-950 md:text-5xl">{{ title }}</h1>
        <p class="mt-5 max-w-3xl text-base leading-8 text-slate-700">{{ summary }}</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getRiskMeta } from '@/utils/risk'
import type { RiskLevel } from '@/types/domain'

const props = defineProps<{ riskLevel: RiskLevel; riskScore: number; title: string; summary: string }>()
const meta = computed(() => getRiskMeta(props.riskLevel))
const scoreRing = computed(() => `conic-gradient(${meta.value.color} ${props.riskScore * 3.6}deg, #E2E8F0 0deg)`)
const conclusion = computed(() => {
  if (props.riskLevel === 'high') return '建议先处理再上架'
  if (props.riskLevel === 'medium') return '建议复核后上架'
  if (props.riskLevel === 'low') return '可继续推进'
  return '等待生成'
})
</script>
