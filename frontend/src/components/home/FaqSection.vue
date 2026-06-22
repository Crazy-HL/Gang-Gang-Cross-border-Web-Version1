<template>
  <section class="bg-white px-5 py-20 lg:px-8">
    <SectionHeading
      eyebrow="常见问题"
      title="第一次用，也不用准备太多"
      description="能发什么、能得到什么，先说清楚。"
    />

    <div class="mx-auto mt-12 grid max-w-5xl gap-4">
      <article
        v-for="[question, answer] in faqs"
        :key="question"
        class="rounded-[1.5rem] border border-slate-200/80 bg-white p-6 shadow-sm shadow-blue-900/5"
      >
        <h3 class="text-lg font-bold text-slate-950">{{ question }}</h3>
        <p class="mt-2 text-sm leading-6 text-slate-500">{{ answer }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import SectionHeading from '@/components/ui/SectionHeading.vue'

const faqs = [
  ['我不懂商标版权，可以用吗？', '可以。你只要把商品资料发来，我们帮你看重点风险。'],
  ['需要发什么资料？', '商品图、包装图、Logo、标题、详情文案都可以。'],
  ['看完后能得到什么？', '你会知道哪里可能有问题，以及上架前建议先处理什么。']
]
</script>
