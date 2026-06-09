<template><section class="px-5 py-16 lg:px-8"><SectionHeading eyebrow="FAQ" title="上线前常见问题" /><div class="mx-auto mt-12 max-w-4xl divide-y divide-white/10 rounded-3xl border border-white/10 bg-panel/70"><div v-for="[q, a] in faqs" :key="q" class="p-6"><h3 class="font-bold text-white">{{ q }}</h3><p class="mt-2 text-sm leading-6 text-slate-400">{{ a }}</p></div></div></section></template>
<script setup lang="ts">
import SectionHeading from '@/components/ui/SectionHeading.vue'
const faqs = [['适合哪些团队？', '适合跨境卖家、品牌方、工厂和代运营团队在选品、上架、投放前做风险预检。'], ['是否替代律师意见？', '系统提供风险线索和证据整理，不替代正式法律意见；高风险任务建议提交人工复核。'], ['没有后端能运行吗？', '当前版本由 FastAPI 后端提供 mock 数据，可本地演示并等待真实接口接入。']]
</script>
