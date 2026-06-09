<template><SiteHeader /><main class="mx-auto max-w-7xl px-5 py-14 lg:px-8"><div class="mb-10 max-w-3xl"><p class="text-sm font-bold uppercase tracking-[0.35em] text-gold">Detection Upload</p><h1 class="mt-4 text-4xl font-black text-white md:text-6xl">上传商品资料，生成风险预警</h1><p class="mt-5 text-base leading-7 text-slate-400">至少上传一张商品图或输入商品链接，同时填写品牌、类目和目标市场。</p></div><DetectionForm /></main><SiteFooter /></template>
<script setup lang="ts">
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import DetectionForm from '@/components/detect/DetectionForm.vue'
</script>
