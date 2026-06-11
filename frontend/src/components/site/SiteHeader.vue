<template>
  <header class="no-print sticky top-0 z-40 border-b border-white/10 bg-ink/85 backdrop-blur-xl">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
      <RouterLink to="/" class="flex items-center gap-3" aria-label="港港跨境首页">
        <span class="grid h-10 w-10 place-items-center rounded-2xl bg-gradient-to-br from-gold to-ember text-lg font-black text-ink shadow-glow">G</span>
        <span><span class="block text-base font-bold tracking-wide text-white">港港跨境</span><span class="block text-xs text-slate-400">IP Risk Command</span></span>
      </RouterLink>
      <nav class="hidden items-center gap-1 md:flex" aria-label="主导航">
        <RouterLink v-for="item in navItems" :key="item.href" :to="item.href" class="rounded-full px-4 py-2 text-sm text-slate-300 transition hover:bg-white/10 hover:text-white">{{ item.label }}</RouterLink>
      </nav>
      <div class="flex items-center gap-3">
        <div v-if="user" class="hidden items-center gap-3 sm:flex"><span class="text-sm text-slate-300">{{ user.name }}</span><RouterLink to="/notifications" class="relative rounded-full border border-white/15 px-4 py-2 text-sm text-slate-200 transition hover:border-gold/60 hover:text-gold">消息<span v-if="unreadCount" class="absolute -right-2 -top-2 rounded-full bg-gold px-1.5 py-0.5 text-xs font-bold text-ink">{{ unreadCount }}</span></RouterLink><button type="button" class="rounded-full border border-white/15 px-4 py-2 text-sm text-slate-200 transition hover:border-gold/60 hover:text-gold" @click="handleLogout">退出</button></div>
        <RouterLink v-else to="/auth" class="hidden rounded-full border border-white/15 px-4 py-2 text-sm text-slate-200 transition hover:border-gold/60 hover:text-gold sm:inline-flex">登录</RouterLink>
        <RouterLink to="/detect" class="rounded-full bg-gold px-5 py-2.5 text-sm font-bold text-ink shadow-glow transition hover:bg-amber-300">快速上传检测</RouterLink>
      </div>
    </div>
    <nav class="border-t border-white/10 px-5 pb-3 md:hidden" aria-label="移动端导航">
      <div class="flex gap-2 overflow-x-auto text-sm text-slate-300">
        <RouterLink v-for="item in navItems" :key="item.href" :to="item.href" class="shrink-0 rounded-full border border-white/10 px-3 py-1.5">{{ item.label }}</RouterLink>
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getUnreadNotificationCount } from '@/api/client'
import { logout, user } from '@/stores/auth'

const router = useRouter()
const unreadCount = ref(0)
const navItems = [
  { href: '/', label: '首页' },
  { href: '/detect', label: '检测上传' },
  { href: '/dashboard', label: '用户中心' },
  { href: '/reports/1001', label: '报告' },
  { href: '/admin', label: '后台' }
]

async function loadUnreadCount() {
  if (!user.value) {
    unreadCount.value = 0
    return
  }
  try {
    unreadCount.value = (await getUnreadNotificationCount()).unreadCount
  } catch {
    unreadCount.value = 0
  }
}

onMounted(loadUnreadCount)
watch(user, loadUnreadCount)

async function handleLogout() {
  await logout()
  router.push('/auth')
}
</script>
