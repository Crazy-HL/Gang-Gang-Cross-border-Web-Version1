<template>
  <SiteHeader />
  <main class="relative overflow-hidden bg-[radial-gradient(circle_at_78%_10%,rgba(251,146,60,0.14),transparent_28%),linear-gradient(135deg,#ffffff_0%,#eef7ff_54%,#fff8ed_100%)] px-5 py-12 lg:px-8 lg:py-16">
    <div class="pointer-events-none absolute -right-24 top-28 h-80 w-80 rounded-full bg-blue-200/35 blur-3xl" />
    <div class="pointer-events-none absolute bottom-24 left-2 h-64 w-64 rounded-full bg-orange-200/25 blur-3xl" />

    <div class="relative mx-auto max-w-7xl">
      <section class="max-w-4xl">
        <p class="inline-flex rounded-full border border-blue-200 bg-white/80 px-4 py-2 text-sm font-bold text-blue-700 shadow-sm shadow-blue-900/5">
          上架合规预检
        </p>
        <h1 class="mt-6 text-4xl font-black leading-tight tracking-tight text-slate-950 md:text-6xl">
          提交商品资料
        </h1>
        <p class="mt-5 max-w-2xl text-base leading-7 text-slate-600">
          上传图片或填写文案，先做一次上架前预检。
        </p>

        <div class="mt-6 flex flex-wrap gap-3">
          <span v-for="item in steps" :key="item" class="rounded-full border border-white/80 bg-white/75 px-4 py-2 text-sm font-bold text-slate-600 shadow-sm">
            {{ item }}
          </span>
        </div>
      </section>

      <DetectionForm class="mt-10" />
    </div>
  </main>
  <SiteFooter />
</template>

<script setup lang="ts">
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import DetectionForm from '@/components/detect/DetectionForm.vue'

const steps = ['提交资料', '自动预检', '查看建议']
</script>
