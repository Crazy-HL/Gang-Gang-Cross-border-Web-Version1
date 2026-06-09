<template>
  <section class="px-5 py-16 lg:px-8">
    <SectionHeading eyebrow="Capabilities" title="覆盖上架前最常见的三类侵权风险" description="把商标、外观和版权证据集中在同一份报告里，减少团队跨系统检索成本。" />
    <div class="mx-auto mt-12 grid max-w-7xl gap-5 md:grid-cols-3">
      <article v-for="feature in features" :key="feature.title" class="rounded-3xl border border-white/10 bg-panel/80 p-7"><div class="grid h-14 w-14 place-items-center rounded-2xl bg-gold/15 text-sm font-black text-gold">{{ feature.icon }}</div><h3 class="mt-8 text-xl font-bold text-white">{{ feature.title }}</h3><p class="mt-3 text-sm leading-6 text-slate-400">{{ feature.description }}</p></article>
    </div>
  </section>
</template>

<script setup lang="ts">
import SectionHeading from '@/components/ui/SectionHeading.vue'
const features = [
  { title: '商标风险检索', description: '识别品牌词、图形商标和近似名称冲突。', icon: 'TM' },
  { title: '外观专利比对', description: '对比商品形态、包装和关键视觉元素。', icon: '3D' },
  { title: '版权素材检测', description: '检查图片、文案和角色素材的疑似版权风险。', icon: 'CR' }
]
</script>
