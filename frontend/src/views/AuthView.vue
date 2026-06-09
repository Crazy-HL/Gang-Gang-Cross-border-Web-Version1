<template><SiteHeader /><main class="mx-auto max-w-7xl px-5 py-14 lg:px-8"><div class="mb-10 text-center"><p class="text-sm font-bold uppercase tracking-[0.35em] text-gold">Auth</p><h1 class="mt-4 text-4xl font-black text-white md:text-5xl">登录或注册账号</h1></div><AuthForm /></main><SiteFooter /></template>
<script setup lang="ts">
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import AuthForm from '@/components/auth/AuthForm.vue'
</script>
