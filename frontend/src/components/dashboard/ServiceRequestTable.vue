<template>
  <section class="rounded-[2rem] border border-slate-200/80 bg-panel/75 p-5">
    <div class="grid gap-4 md:grid-cols-[1fr_220px]">
      <label class="text-sm font-semibold text-slate-950">
        搜索服务工单
        <input v-model="keyword" aria-label="搜索服务工单" class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900" placeholder="输入工单号、平台或标题" />
      </label>
      <label class="text-sm font-semibold text-slate-950">
        类型筛选
        <select v-model="requestType" class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900">
          <option value="all">全部</option>
          <option value="appeal">平台申诉</option>
          <option value="tro_settlement">TRO 和解</option>
        </select>
      </label>
    </div>

    <div class="mt-6 overflow-x-auto">
      <table class="w-full min-w-[860px] text-left text-sm" aria-label="我的服务工单">
        <thead class="text-slate-500">
          <tr class="border-b border-slate-200/80">
            <th class="py-3">工单ID</th>
            <th>类型</th>
            <th>标题</th>
            <th>平台</th>
            <th>联系方式</th>
            <th>状态</th>
            <th>提交时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredRequests" :key="item.id" class="border-b border-white/5 text-slate-600 hover:bg-white/[0.03]">
            <td class="py-4 font-semibold text-slate-700">{{ item.id }}</td>
            <td>{{ typeLabels[item.requestType] }}</td>
            <td>
              <p class="font-semibold text-slate-800">{{ item.title }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ secondaryText(item) }}</p>
              <p v-if="item.adviceReport" class="mt-1 text-xs font-bold text-blue-700">
                已生成建议报告：{{ item.adviceReport.title }}
                <span class="ml-2 text-slate-500">{{ sourceLabels[item.adviceReport.source ?? 'fallback'] }}</span>
              </p>
            </td>
            <td>{{ item.platform }}</td>
            <td>{{ item.contact }}</td>
            <td><span class="rounded-full border border-blue-100 bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700">{{ statusLabels[item.status] }}</span></td>
            <td>{{ item.createdAt }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="filteredRequests.length === 0" class="py-10 text-center text-slate-500">暂无匹配服务工单</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ServiceRequestItem, ServiceRequestStatus, ServiceRequestType } from '@/types/domain'

const props = defineProps<{ requests: ServiceRequestItem[] }>()
const keyword = ref('')
const requestType = ref<ServiceRequestType | 'all'>('all')
const typeLabels: Record<ServiceRequestType, string> = { appeal: '平台申诉', tro_settlement: 'TRO 和解' }
const statusLabels: Record<ServiceRequestStatus, string> = { pending: '待评估', reviewing: '审核中', waiting_user: '待补充', processing: '处理中', done: '已完成' }
const sourceLabels = { model: '港港跨境AI', fallback: '港港跨境基础评估' }
const filteredRequests = computed(() => props.requests.filter((item) => `${item.id} ${item.title} ${item.platform} ${item.contact}`.toLowerCase().includes(keyword.value.trim().toLowerCase()) && (requestType.value === 'all' || item.requestType === requestType.value)))

function secondaryText(item: ServiceRequestItem) {
  if (item.requestType === 'appeal') return item.issueType || item.reference || '申诉资料待评估'
  return item.caseStatus || item.caseNumber || 'TRO 案件待评估'
}
</script>
