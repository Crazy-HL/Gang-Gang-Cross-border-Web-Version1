<template>
  <section class="bg-white px-5 py-20 lg:px-8">
    <div class="mx-auto max-w-6xl overflow-hidden rounded-[2rem] border border-blue-100 bg-[linear-gradient(135deg,#ffffff_0%,#eef7ff_58%,#fff7ed_100%)] p-6 shadow-2xl shadow-blue-900/10 md:p-10">
      <div class="grid gap-8 lg:grid-cols-[minmax(0,1fr)_260px] lg:items-center">
        <div>
          <p class="inline-flex rounded-full border border-orange-200 bg-orange-50 px-4 py-2 text-sm font-bold text-orange-800">
            人工帮看
          </p>
          <h2 class="mt-5 max-w-3xl text-3xl font-black leading-tight text-slate-950 md:text-5xl lg:whitespace-nowrap">
            不确定能不能上架？先问我们
          </h2>
          <p class="mt-4 max-w-2xl text-base leading-7 text-slate-600">
            如果检测结果看不懂，或者商品比较重要，可以提交人工复核。
          </p>
          <div class="mt-7">
            <ButtonLink href="/detect">先发资料</ButtonLink>
          </div>
        </div>

        <div class="hidden rounded-[1.75rem] border border-white/80 bg-white/80 p-4 shadow-xl shadow-blue-900/5 lg:block">
          <div class="grid place-items-center rounded-[1.35rem] bg-white p-4 ring-1 ring-blue-100">
            <img
              src="/wechat-qrcode-cropped.jpg"
              alt="微信二维码"
              class="aspect-square h-52 w-52 rounded-[1.15rem] object-contain"
            />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import ButtonLink from '@/components/ui/ButtonLink.vue'
</script>
