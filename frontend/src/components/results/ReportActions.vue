<template><div class="no-print rounded-3xl border border-white/10 bg-white/[0.04] p-5"><div class="flex flex-col gap-3 sm:flex-row"><a :href="downloadReportUrl(jobId)" class="rounded-full bg-gold px-5 py-3 text-center text-sm font-bold text-ink transition hover:bg-amber-300">下载PDF报告</a><button type="button" @click="share" class="rounded-full border border-white/15 px-5 py-3 text-sm font-bold text-white transition hover:border-gold hover:text-gold">复制分享链接</button><button type="button" @click="message = '人工复核申请已提交'" class="rounded-full border border-white/15 px-5 py-3 text-sm font-bold text-white transition hover:border-gold hover:text-gold">申请人工复核</button></div><p v-if="message" class="mt-4 text-sm text-gold" role="status">{{ message }}</p></div></template>
<script setup lang="ts">
import { ref } from 'vue'
import { downloadReportUrl } from '@/api/client'
defineProps<{ jobId: string }>()
const message = ref('')
async function share() { const url = window.location.href; if (navigator.share) { await navigator.share({ title: '港港跨境风险报告', url }); message.value = '分享面板已打开'; return } await navigator.clipboard.writeText(url); message.value = '分享链接已复制' }
</script>
