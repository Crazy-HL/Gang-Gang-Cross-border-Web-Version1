<template>
  <section class="overflow-hidden rounded-[1.75rem] border border-orange-200 bg-white shadow-sm shadow-orange-900/5">
    <div class="border-b border-orange-100 bg-[linear-gradient(135deg,#fff7ed_0%,#ffffff_58%,#eff6ff_100%)] p-6">
      <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p class="text-sm font-black text-orange-800">官方数据库查询</p>
          <h2 class="mt-1 text-2xl font-black text-slate-950">USPTO 美国商标查询结果</h2>
        </div>
        <span class="w-fit rounded-full border border-orange-200 bg-white px-4 py-2 text-xs font-black text-orange-800">
          {{ hasPositiveHit ? `${positiveHitCount} 条明确命中` : '未发现明确命中' }}
        </span>
      </div>
      <p class="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
        这里展示的是美国官方商标库查询结果。判断重点不是泛化评分，而是：是否有明确商标记录、商标是否有效、名称和类别是否接近。
      </p>
    </div>

    <div class="grid gap-4 p-5">
      <article
        v-for="(item, index) in evidence"
        :key="item.id"
        class="rounded-2xl border border-slate-200/80 bg-slate-50/70 p-5"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <span class="grid h-7 w-7 place-items-center rounded-full bg-orange-500 text-xs font-black text-white">{{ index + 1 }}</span>
              <h3 class="text-xl font-black text-slate-950">{{ item.matched }}</h3>
            </div>
            <p class="mt-2 text-sm font-bold text-slate-500">来源：{{ item.source }}</p>
          </div>
          <span class="w-fit rounded-full px-4 py-2 text-sm font-black" :class="item.similarity > 0 ? 'bg-orange-100 text-orange-800' : 'bg-blue-50 text-blue-700'">
            名称相似度 {{ formatPercent(item.similarity) }}
          </span>
        </div>

        <p class="mt-4 text-sm leading-7 text-slate-700">{{ item.description }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatPercent } from '@/utils/risk'
import type { EvidenceItem } from '@/types/domain'

const props = defineProps<{ evidence: EvidenceItem[] }>()
const positiveHitCount = computed(() => props.evidence.filter((item) => item.similarity > 0).length)
const hasPositiveHit = computed(() => positiveHitCount.value > 0)
</script>
