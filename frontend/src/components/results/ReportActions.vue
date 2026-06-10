<template><div class="no-print rounded-3xl border border-white/10 bg-white/[0.04] p-5"><div class="flex flex-col gap-3 sm:flex-row"><a :href="downloadReportUrl(jobId)" class="rounded-full bg-gold px-5 py-3 text-center text-sm font-bold text-ink transition hover:bg-amber-300">下载PDF报告</a><button type="button" @click="share" class="rounded-full border border-white/15 px-5 py-3 text-sm font-bold text-white transition hover:border-gold hover:text-gold">复制分享链接</button><button type="button" :disabled="reviewing" @click="requestReview" class="rounded-full border border-white/15 px-5 py-3 text-sm font-bold text-white transition hover:border-gold hover:text-gold disabled:opacity-60">{{ reviewing ? '提交中' : '申请人工复核' }}</button></div><p v-if="message" class="mt-4 text-sm text-gold" role="status">{{ message }}</p></div></template>
<script setup lang="ts">
import { ref } from 'vue'
import { downloadReportUrl, requestJobReview } from '@/api/client'
const props = defineProps<{ jobId: string }>()
const message = ref('')
const reviewing = ref(false)
async function share() { const url = window.location.href; if (navigator.share) { await navigator.share({ title: '港港跨境风险报告', url }); message.value = '分享面板已打开'; return } await navigator.clipboard.writeText(url); message.value = '分享链接已复制' }
async function requestReview() { if (reviewing.value) return; reviewing.value = true; message.value = ''; try { await requestJobReview(props.jobId, '请人工复核该任务风险'); message.value = '人工复核申请已提交' } catch { message.value = '提交失败，请稍后重试' } finally { reviewing.value = false } }
</script>
