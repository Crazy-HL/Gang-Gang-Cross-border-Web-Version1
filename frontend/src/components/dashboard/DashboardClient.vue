<template>
  <div class="space-y-6">
    <div class="flex flex-col justify-between gap-4 rounded-[2rem] border border-slate-200/80 bg-panel/75 p-6 md:flex-row md:items-center">
      <div>
        <p class="text-sm text-slate-500">你好，张三</p>
        <h1 class="mt-2 text-3xl font-black text-slate-950">用户中心</h1>
      </div>
      <div class="flex flex-wrap gap-3">
        <button type="button" @click="tab = 'tasks'" :class="tab === 'tasks' ? activeClass : inactiveClass">我的任务</button>
        <button type="button" @click="tab = 'serviceRequests'" :class="tab === 'serviceRequests' ? activeClass : inactiveClass">服务工单</button>
        <button type="button" @click="tab = 'reports'" :class="tab === 'reports' ? activeClass : inactiveClass">我的报告</button>
      </div>
    </div>

    <TaskTable v-if="tab === 'tasks'" :jobs="jobs" />
    <ServiceRequestTable v-else-if="tab === 'serviceRequests'" :requests="serviceRequests" />
    <ReportList v-else :reports="reports" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import TaskTable from '@/components/dashboard/TaskTable.vue'
import ReportList from '@/components/dashboard/ReportList.vue'
import ServiceRequestTable from '@/components/dashboard/ServiceRequestTable.vue'
import type { DetectionJob, DetectionReport, ServiceRequestItem } from '@/types/domain'

defineProps<{ jobs: DetectionJob[]; reports: DetectionReport[]; serviceRequests: ServiceRequestItem[] }>()

const route = useRoute()
const tab = ref<'tasks' | 'serviceRequests' | 'reports'>(route.query.tab === 'reports' ? 'reports' : route.query.tab === 'serviceRequests' ? 'serviceRequests' : 'tasks')
const activeClass = 'rounded-full px-5 py-2 text-sm font-bold bg-gold text-white'
const inactiveClass = 'rounded-full px-5 py-2 text-sm font-bold border border-slate-200 text-slate-950'

watch(() => route.query.tab, (value) => {
  if (value === 'reports') tab.value = 'reports'
  else if (value === 'serviceRequests') tab.value = 'serviceRequests'
  else if (value === 'tasks') tab.value = 'tasks'
})
</script>
