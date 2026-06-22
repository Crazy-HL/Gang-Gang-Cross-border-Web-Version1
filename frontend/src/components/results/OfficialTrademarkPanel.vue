<template>
  <section class="overflow-hidden rounded-[1.75rem] border border-orange-200 bg-white shadow-sm shadow-orange-900/5">
    <div class="border-b border-orange-100 bg-[linear-gradient(135deg,#fff7ed_0%,#ffffff_58%,#eff6ff_100%)] p-6">
      <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p class="text-sm font-black text-orange-800">官方数据库命中</p>
          <h2 class="mt-1 text-2xl font-black text-slate-950">USPTO 美国商标记录</h2>
        </div>
        <span class="w-fit rounded-full border border-orange-200 bg-white px-4 py-2 text-xs font-black text-orange-800">
          {{ evidence.length }} 条相关记录
        </span>
      </div>
      <p class="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
        这里展示的是美国官方商标库返回的具体记录。判断重点不是泛化评分，而是：是否为有效商标、名称是否接近、类别和你的商品是否接近。
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
          <span class="w-fit rounded-full bg-orange-100 px-4 py-2 text-sm font-black text-orange-800">
            名称相似度 {{ formatPercent(item.similarity) }}
          </span>
        </div>

        <p class="mt-4 text-sm leading-7 text-slate-700">{{ item.description }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { formatPercent } from '@/utils/risk'
import type { EvidenceItem } from '@/types/domain'

defineProps<{ evidence: EvidenceItem[] }>()
</script>
