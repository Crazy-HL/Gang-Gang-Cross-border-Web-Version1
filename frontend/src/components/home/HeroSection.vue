<template>
  <section class="relative overflow-hidden px-5 py-20 lg:px-8 lg:py-28">
    <div class="relative mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
      <div>
        <p class="inline-flex rounded-full border border-gold/30 bg-gold/10 px-4 py-2 text-sm font-semibold text-gold">Cross-border IP Risk Detection</p>
        <h1 class="mt-7 max-w-4xl text-5xl font-black leading-tight tracking-tight text-white md:text-7xl">先查侵权，<span class="block bg-gradient-to-r from-gold via-orange-300 to-ember bg-clip-text text-transparent">再投入成本</span></h1>
        <p class="mt-6 max-w-2xl text-lg leading-8 text-slate-300">面向跨境卖家、品牌方和工厂的商标、外观、版权风险检测平台。上传商品资料后，系统输出风险等级、命中证据和处理建议。</p>
        <div class="mt-9 flex flex-col gap-4 sm:flex-row"><ButtonLink href="/detect">快速上传检测</ButtonLink><ButtonLink href="/reports/1001" variant="secondary">查看示例报告</ButtonLink></div>
      </div>
      <div class="rounded-[2rem] border border-white/10 bg-white/[0.06] p-5 shadow-2xl backdrop-blur">
        <div class="rounded-[1.5rem] border border-gold/20 bg-ink-2 p-6">
          <div class="flex items-center justify-between"><span class="text-sm text-slate-400">总体风险</span><span class="rounded-full bg-red-500/15 px-3 py-1 text-xs font-bold text-red-300">高风险</span></div>
          <div class="mt-8 flex items-end gap-3"><span class="text-7xl font-black text-gold">85</span><span class="pb-3 text-slate-500">/100</span></div>
          <div class="mt-8 space-y-4"><div v-for="item in items" :key="item" class="rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-slate-300">{{ item }}</div></div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import ButtonLink from '@/components/ui/ButtonLink.vue'
const items = ['商标命中 89%', '外观相似 82%', '版权素材 71%']
</script>
