<template><div class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]"><section class="rounded-[2rem] border border-white/10 bg-panel/75 p-5"><label class="text-sm font-semibold text-white">搜索管理员任务<input v-model="keyword" class="mt-2 w-full rounded-2xl border border-white/10 bg-ink-2 px-4 py-3 text-slate-100" /></label><div class="mt-5 space-y-3"><button v-for="job in filteredJobs" :key="job.id" type="button" class="w-full rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left hover:border-gold/40" @click="selectedId = job.id"><div class="flex justify-between gap-4"><span class="font-bold text-white">{{ job.title }}</span><span :style="{ color: getRiskMeta(job.riskLevel).color }">{{ getRiskMeta(job.riskLevel).label }}</span></div><p class="mt-2 text-sm text-slate-400">用户：{{ job.ownerName }} · 任务 {{ job.id }}</p><p v-if="job.reviewStatus === 'pending'" class="mt-2 text-xs font-bold text-gold">待人工复核</p></button></div></section><aside class="rounded-[2rem] border border-gold/20 bg-gold/10 p-6"><h2 class="text-xl font-bold text-white">任务详情</h2><div v-if="selectedJob" class="mt-5 space-y-3 text-sm text-slate-300"><p>任务ID：{{ selectedJob.id }}</p><p>用户：{{ selectedJob.ownerName }}</p><p>品牌：{{ selectedJob.brand }}</p><p>市场：{{ selectedJob.market }}</p><p>复核状态：{{ reviewLabels[selectedJob.reviewStatus ?? 'none'] }}</p><p v-if="selectedJob.reviewNote">复核备注：{{ selectedJob.reviewNote }}</p><img v-if="selectedJob.fileUrl" :src="assetUrl(selectedJob.fileUrl)" :alt="selectedJob.title" class="h-36 w-full rounded-2xl border border-gold/20 bg-ink-2 object-cover" /><div v-else class="grid h-36 place-items-center rounded-2xl border border-gold/20 bg-ink-2 text-gold">暂无原始文件</div></div></aside></div></template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { getRiskMeta } from '@/utils/risk'
import type { DetectionJob, ReviewStatus } from '@/types/domain'
const props = defineProps<{ jobs: DetectionJob[] }>()
const keyword = ref('')
const selectedId = ref(props.jobs[0]?.id ?? '')
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const reviewLabels: Record<ReviewStatus, string> = { none: '未申请', pending: '待人工复核', approved: '已通过复核', rejected: '已驳回复核' }
const selectedJob = computed(() => props.jobs.find((job) => job.id === selectedId.value) ?? props.jobs[0])
const filteredJobs = computed(() => props.jobs.filter((job) => `${job.ownerName} ${job.title} ${job.id}`.toLowerCase().includes(keyword.value.toLowerCase())))
function assetUrl(path: string) { return path.startsWith('http') ? path : `${API_BASE_URL}${path}` }
</script>
