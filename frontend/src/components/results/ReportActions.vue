<template><div class="no-print rounded-3xl border border-slate-200/80 bg-white/80 p-5"><div class="mb-4 rounded-2xl border border-gold/20 bg-gold/10 p-4"><p class="text-sm font-bold text-slate-950">人工复核状态：{{ currentReviewLabel }}</p><p v-if="currentReviewNote" class="mt-2 text-sm text-slate-600">复核备注：{{ currentReviewNote }}</p></div><div class="flex flex-col gap-3 sm:flex-row"><button type="button" :disabled="downloading" @click="downloadPdf" class="rounded-full bg-gold px-5 py-3 text-center text-sm font-bold text-white transition hover:bg-gold/80 disabled:opacity-60">{{ downloading ? '下载中' : '下载PDF报告' }}</button><button type="button" @click="share" class="rounded-full border border-slate-200 px-5 py-3 text-sm font-bold text-slate-950 transition hover:border-gold hover:text-slate-700">复制分享链接</button><button v-if="canRequestReview" type="button" :disabled="reviewing" @click="requestReview" class="rounded-full border border-slate-200 px-5 py-3 text-sm font-bold text-slate-950 transition hover:border-gold hover:text-slate-700 disabled:opacity-60">{{ reviewing ? '提交中' : '申请人工复核' }}</button></div><p v-if="message" class="mt-4 text-sm text-slate-700" role="status">{{ message }}</p></div></template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { downloadReportPdf, requestJobReview } from '@/api/client'
import type { ReviewStatus } from '@/types/domain'
const props = defineProps<{ jobId: string; reviewStatus: ReviewStatus; reviewNote: string }>()
const message = ref('')
const reviewing = ref(false)
const downloading = ref(false)
const localReviewStatus = ref<ReviewStatus>(props.reviewStatus)
const reviewLabels: Record<ReviewStatus, string> = { none: '未申请', pending: '待人工复核', approved: '已通过复核', rejected: '已驳回复核' }
const currentReviewLabel = computed(() => reviewLabels[localReviewStatus.value])
const currentReviewNote = computed(() => props.reviewNote)
const canRequestReview = computed(() => localReviewStatus.value === 'none' || localReviewStatus.value === 'rejected')
async function downloadPdf() { if (downloading.value) return; downloading.value = true; message.value = ''; try { const { blob, filename } = await downloadReportPdf(props.jobId); const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = filename; document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url); message.value = 'PDF报告已开始下载' } catch { message.value = '下载失败，请稍后重试' } finally { downloading.value = false } }
async function share() { const url = window.location.href; if (navigator.share) { await navigator.share({ title: '港港跨境风险报告', url }); message.value = '分享面板已打开'; return } await navigator.clipboard.writeText(url); message.value = '分享链接已复制' }
async function requestReview() { if (reviewing.value) return; reviewing.value = true; message.value = ''; try { const result = await requestJobReview(props.jobId, '请人工复核该任务风险'); localReviewStatus.value = result.reviewStatus as ReviewStatus; message.value = '人工复核申请已提交' } catch { message.value = '提交失败，请稍后重试' } finally { reviewing.value = false } }
</script>
