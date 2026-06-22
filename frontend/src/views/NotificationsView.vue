<template><SiteHeader /><main class="mx-auto max-w-5xl px-5 py-12 lg:px-8"><section class="rounded-[2rem] border border-slate-200/80 bg-panel/75 p-6"><div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between"><div><p class="text-sm font-bold uppercase tracking-[0.3em] text-slate-700">Notification Center</p><h1 class="mt-2 text-3xl font-black text-slate-950">消息通知</h1></div><p class="text-sm text-slate-500">未读消息：{{ unreadCount }}</p></div><div class="mt-8 space-y-4"><article v-for="item in notifications" :key="item.id" class="rounded-3xl border border-slate-200/80 bg-white/80 p-5"><div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><div class="flex items-center gap-3"><h2 class="text-lg font-bold text-slate-950">{{ item.title }}</h2><span v-if="!item.isRead" class="rounded-full bg-gold px-2.5 py-1 text-xs font-bold text-white">未读</span></div><p class="mt-2 text-sm text-slate-600">{{ item.content }}</p><p class="mt-3 text-xs text-slate-500">{{ item.createdAt }}</p></div><button v-if="!item.isRead" type="button" class="rounded-full border border-slate-200 px-4 py-2 text-sm font-bold text-slate-950 transition hover:border-gold hover:text-slate-700" @click="markRead(item.id)">标记已读</button></div></article><div v-if="!loading && notifications.length === 0" class="rounded-3xl border border-dashed border-slate-200/80 p-8 text-center text-slate-500">暂无通知</div><div v-if="loading" class="rounded-3xl border border-slate-200/80 p-8 text-center text-slate-500">通知加载中</div></div></section></main><SiteFooter /></template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import { getNotifications, markNotificationRead } from '@/api/client'
import type { NotificationItem } from '@/types/domain'
const notifications = ref<NotificationItem[]>([])
const unreadCount = ref(0)
const loading = ref(true)
onMounted(loadNotifications)
async function loadNotifications() { try { const data = await getNotifications(); notifications.value = data.notifications; unreadCount.value = data.unreadCount } finally { loading.value = false } }
async function markRead(id: number) { await markNotificationRead(id); notifications.value = notifications.value.map((item) => item.id === id ? { ...item, isRead: true } : item); unreadCount.value = Math.max(0, unreadCount.value - 1) }
</script>
