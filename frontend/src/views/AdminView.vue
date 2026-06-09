<template><SiteHeader /><main class="mx-auto max-w-7xl px-5 py-12 lg:px-8"><div class="mb-8"><p class="text-sm font-bold uppercase tracking-[0.35em] text-gold">Admin</p><h1 class="mt-4 text-4xl font-black text-white">运营管理后台</h1></div><AdminDashboard v-if="stats && jobs" :stats="stats" :jobs="jobs" /></main><SiteFooter /></template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import AdminDashboard from '@/components/admin/AdminDashboard.vue'
import { getAdminJobs } from '@/api/client'
import type { AdminStats, DetectionJob } from '@/types/domain'
const stats = ref<AdminStats | null>(null)
const jobs = ref<DetectionJob[] | null>(null)
onMounted(async () => { const data = await getAdminJobs(); stats.value = data.stats; jobs.value = data.jobs })
</script>
