<template>
  <SiteHeader />
  <main class="mx-auto max-w-7xl px-5 py-12 lg:px-8">
    <DashboardClient v-if="jobs && reports && serviceRequests" :jobs="jobs" :reports="reports" :service-requests="serviceRequests" />
  </main>
  <SiteFooter />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import DashboardClient from '@/components/dashboard/DashboardClient.vue'
import { getJobs, getReports, getServiceRequests } from '@/api/client'
import type { DetectionJob, DetectionReport, ServiceRequestItem } from '@/types/domain'

const jobs = ref<DetectionJob[] | null>(null)
const reports = ref<DetectionReport[] | null>(null)
const serviceRequests = ref<ServiceRequestItem[] | null>(null)

onMounted(async () => {
  [jobs.value, reports.value, serviceRequests.value] = await Promise.all([getJobs(), getReports(), getServiceRequests()])
})
</script>
