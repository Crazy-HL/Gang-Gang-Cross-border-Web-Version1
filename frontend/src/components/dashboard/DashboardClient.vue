<template><div class="space-y-6"><div class="flex flex-col justify-between gap-4 rounded-[2rem] border border-slate-200/80 bg-panel/75 p-6 md:flex-row md:items-center"><div><p class="text-sm text-slate-500">你好，张三</p><h1 class="mt-2 text-3xl font-black text-slate-950">用户中心</h1></div><div class="flex gap-3"><button @click="tab = 'tasks'" :class="tab === 'tasks' ? activeClass : inactiveClass">我的任务</button><button @click="tab = 'reports'" :class="tab === 'reports' ? activeClass : inactiveClass">我的报告</button></div></div><TaskTable v-if="tab === 'tasks'" :jobs="jobs" /><ReportList v-else :reports="reports" /></div></template>
<script setup lang="ts">
import { ref } from 'vue'
import TaskTable from '@/components/dashboard/TaskTable.vue'
import ReportList from '@/components/dashboard/ReportList.vue'
import type { DetectionJob, DetectionReport } from '@/types/domain'
defineProps<{ jobs: DetectionJob[]; reports: DetectionReport[] }>()
const tab = ref<'tasks' | 'reports'>('tasks')
const activeClass = 'rounded-full px-5 py-2 text-sm font-bold bg-gold text-white'
const inactiveClass = 'rounded-full px-5 py-2 text-sm font-bold border border-slate-200 text-slate-950'
</script>
