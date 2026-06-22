<template>
  <section class="bg-slate-50 px-5 py-20 lg:px-8">
    <SectionHeading
      eyebrow="怎么开始"
      title="三步就能先查一遍"
      description="适合上架前、投广告前、备货前，先做一次简单排查。"
    />

    <div class="mx-auto mt-12 grid max-w-6xl gap-5 md:grid-cols-3">
      <article
        v-for="(step, index) in steps"
        :key="step.title"
        class="relative overflow-hidden rounded-[1.75rem] border border-white bg-white p-7 shadow-sm shadow-blue-900/5"
      >
        <div class="absolute right-5 top-5 text-6xl font-black text-blue-50">0{{ index + 1 }}</div>
        <div class="relative">
          <span class="grid h-12 w-12 place-items-center rounded-2xl text-sm font-black" :class="step.tone">
            0{{ index + 1 }}
          </span>
          <h3 class="mt-7 text-xl font-bold text-slate-950">{{ step.title }}</h3>
          <p class="mt-3 text-sm leading-6 text-slate-500">{{ step.description }}</p>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import SectionHeading from '@/components/ui/SectionHeading.vue'

const steps = [
  {
    title: '发商品资料',
    description: '商品图、包装图、标题、详情文案都可以。',
    tone: 'bg-blue-50 text-blue-700'
  },
  {
    title: '帮你看风险',
    description: '重点看品牌名、图片、外观和素材来源。',
    tone: 'bg-sky-50 text-sky-700'
  },
  {
    title: '给你建议',
    description: '哪里要小心，先处理什么，都会直接写清楚。',
    tone: 'bg-orange-50 text-orange-700'
  }
]
</script>
