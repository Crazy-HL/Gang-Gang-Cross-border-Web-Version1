<template><section class="px-5 py-16 lg:px-8"><SectionHeading eyebrow="Workflow" title="从资料到报告，三步完成" /><div class="mx-auto mt-12 grid max-w-5xl gap-5 md:grid-cols-3"><div v-for="(step, index) in steps" :key="step" class="rounded-3xl border border-white/10 bg-white/[0.04] p-7"><span class="text-5xl font-black text-gold/25">0{{ index + 1 }}</span><h3 class="mt-6 text-xl font-bold text-white">{{ step }}</h3></div></div></section></template>
<script setup lang="ts">
import SectionHeading from '@/components/ui/SectionHeading.vue'
const steps = ['上传商品资料', 'AI 多源检测', '生成风险报告']
</script>
