<template>
  <section class="overflow-hidden rounded-[2rem] border border-blue-100 bg-[linear-gradient(135deg,#ffffff_0%,#eef7ff_58%,#fff7ed_100%)] p-6 shadow-2xl shadow-blue-900/10 md:p-8">
    <div class="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
      <div>
        <p class="text-sm font-black text-blue-700">报告生成中</p>
        <h1 class="mt-2 text-3xl font-black text-slate-950">{{ stageTitle }}</h1>
        <p class="mt-3 max-w-2xl text-sm leading-6 text-slate-600">{{ stageDescription }}</p>
      </div>
      <div class="grid h-24 w-24 shrink-0 place-items-center rounded-[1.5rem] border border-white bg-white/85 shadow-lg shadow-blue-900/5">
        <span class="text-3xl font-black text-blue-700">{{ progress }}%</span>
      </div>
    </div>

    <div class="mt-7 h-3 overflow-hidden rounded-full bg-white shadow-inner">
      <div
        class="h-full rounded-full bg-[linear-gradient(90deg,#2563eb_0%,#38bdf8_58%,#fb923c_100%)] transition-all duration-500"
        :style="{ width: `${progress}%` }"
      />
    </div>

    <div class="mt-6 grid gap-3 md:grid-cols-3">
      <div
        v-for="step in steps"
        :key="step.label"
        class="rounded-2xl border p-4"
        :class="step.done ? 'border-blue-100 bg-white/90' : 'border-slate-200/80 bg-white/55'"
      >
        <p class="text-sm font-black" :class="step.done ? 'text-slate-950' : 'text-slate-500'">{{ step.label }}</p>
        <p class="mt-1 text-xs font-bold" :class="step.done ? 'text-blue-700' : 'text-slate-400'">{{ step.status }}</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DetectionJob } from '@/types/domain'

const props = defineProps<{ job: DetectionJob | null }>()

const progress = computed(() => {
  if (!props.job) return 18
  if (props.job.status === 'queued') return 36
  if (props.job.status === 'processing') return 76
  if (props.job.status === 'done') return 100
  return 100
})

const stageTitle = computed(() => {
  if (!props.job) return '正在读取任务'
  if (props.job.status === 'queued') return '资料已提交，正在排队'
  if (props.job.status === 'processing') return '正在分析商品风险'
  if (props.job.status === 'failed') return '报告生成失败'
  return '报告已生成'
})

const stageDescription = computed(() => {
  if (!props.job) return '系统正在连接检测任务，请稍候。'
  if (props.job.status === 'queued') return '我们已经收到商品资料，马上进入商标、外观和版权风险预检。'
  if (props.job.status === 'processing') return '系统正在整理商品信息并生成检测结论，完成后会自动打开报告。'
  if (props.job.status === 'failed') return '本次任务没有成功生成报告，可以返回首页重新提交资料。'
  return '报告已经准备好，正在打开结果页。'
})

const steps = computed(() => [
  { label: '提交资料', status: progress.value >= 30 ? '已完成' : '进行中', done: progress.value >= 30 },
  { label: '风险分析', status: progress.value >= 70 ? '已完成' : progress.value >= 36 ? '进行中' : '等待中', done: progress.value >= 70 },
  { label: '生成报告', status: progress.value >= 100 ? '已完成' : progress.value >= 70 ? '进行中' : '等待中', done: progress.value >= 100 },
])
</script>
