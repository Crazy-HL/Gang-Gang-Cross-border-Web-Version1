<template>
  <section class="bg-white px-5 py-20 lg:px-8">
    <SectionHeading
      eyebrow="预检方式"
      title="图片或文字，都可以先查"
      description="上传商品图，或填写商品标题、详情文案，二选一即可开始预检。"
    />

    <div class="mx-auto mt-12 grid max-w-7xl gap-5 md:grid-cols-3">
      <article
        v-for="feature in features"
        :key="feature.title"
        class="group rounded-[1.75rem] border border-slate-200/80 bg-white p-7 shadow-sm shadow-blue-900/5 transition duration-300 hover:-translate-y-1 hover:border-blue-200 hover:shadow-xl hover:shadow-blue-900/10"
      >
        <div class="grid h-14 w-14 place-items-center rounded-2xl ring-1 ring-inset" :class="feature.tone">
          <svg v-if="feature.icon === 'input'" class="h-8 w-8" viewBox="0 0 48 48" fill="none" aria-hidden="true">
            <rect x="7" y="10" width="18" height="16" rx="4" stroke="currentColor" stroke-width="3" />
            <circle cx="15" cy="17" r="2.5" fill="currentColor" />
            <path d="M10 24L16 20L21 24" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
            <rect x="25" y="16" width="16" height="22" rx="4" stroke="currentColor" stroke-width="3" />
            <path d="M30 24H36M30 30H36" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
          </svg>
          <svg v-else-if="feature.icon === 'risk'" class="h-8 w-8" viewBox="0 0 48 48" fill="none" aria-hidden="true">
            <path d="M24 7L38 13V23C38 32 32 38 24 41C16 38 10 32 10 23V13L24 7Z" stroke="currentColor" stroke-width="3" stroke-linejoin="round" />
            <path d="M24 17V26" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
            <circle cx="24" cy="32" r="2" fill="currentColor" />
          </svg>
          <svg v-else class="h-8 w-8" viewBox="0 0 48 48" fill="none" aria-hidden="true">
            <rect x="9" y="9" width="30" height="30" rx="7" stroke="currentColor" stroke-width="3" />
            <path d="M17 24L22 29L32 19" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <h3 class="mt-8 text-xl font-black text-slate-950">{{ feature.title }}</h3>
        <p class="mt-3 text-sm leading-6 text-slate-500">{{ feature.description }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import SectionHeading from '@/components/ui/SectionHeading.vue'

const features = [
  {
    title: '图片或文字提交',
    description: '商品图、包装图、Logo，或标题、详情文案，任选一种即可。',
    icon: 'input',
    tone: 'bg-blue-50 text-blue-700 ring-blue-100'
  },
  {
    title: '上架风险预检',
    description: '初步判断商标近似、外观相似、版权素材等常见风险。',
    icon: 'risk',
    tone: 'bg-orange-50 text-orange-700 ring-orange-100'
  },
  {
    title: '输出处理建议',
    description: '用清楚的风险提示，告诉你上架前建议先确认什么。',
    icon: 'check',
    tone: 'bg-sky-50 text-sky-700 ring-sky-100'
  }
]
</script>
