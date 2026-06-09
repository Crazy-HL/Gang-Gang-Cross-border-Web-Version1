<template><form class="mx-auto max-w-md rounded-[2rem] border border-white/10 bg-panel/80 p-7 shadow-2xl" @submit.prevent="handleSubmit"><div class="mb-6 flex rounded-full border border-white/10 bg-ink-2 p-1"><button type="button" @click="mode = 'login'" :class="mode === 'login' ? activeTab : inactiveTab">登录</button><button type="button" @click="mode = 'register'" :class="mode === 'register' ? activeTab : inactiveTab">注册</button></div><label class="block text-sm font-semibold text-white">手机号<input v-model="mobile" aria-label="手机号" class="mt-2 w-full rounded-2xl border border-white/10 bg-ink-2 px-4 py-3 text-slate-100" placeholder="13800000000" /></label><div class="mt-5 grid grid-cols-[1fr_auto] gap-3"><label class="block text-sm font-semibold text-white">验证码<input v-model="code" aria-label="验证码" class="mt-2 w-full rounded-2xl border border-white/10 bg-ink-2 px-4 py-3 text-slate-100" /></label><button type="button" :disabled="countdown > 0" @click="handleSendCode" class="mt-7 rounded-2xl border border-gold/35 px-4 py-3 text-sm font-bold text-gold disabled:border-white/10 disabled:text-slate-500">{{ countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}</button></div><p v-if="error" class="mt-4 text-sm text-red-300" role="alert">{{ error }}</p><button type="submit" class="mt-7 w-full rounded-full bg-gold px-5 py-3 text-sm font-black text-ink shadow-glow">{{ mode === 'login' ? '登录用户中心' : '完成注册' }}</button><button type="button" class="mt-4 w-full rounded-full border border-white/15 px-5 py-3 text-sm font-bold text-white">微信小程序登录</button></form></template>
<script setup lang="ts">
import { onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginWithCode, registerWithCode, sendCode } from '@/api/client'
const router = useRouter()
const mode = ref<'login' | 'register'>('login')
const mobile = ref('')
const code = ref('')
const countdown = ref(0)
const error = ref('')
let timer: number | undefined
const activeTab = 'flex-1 rounded-full px-4 py-2 text-sm font-bold bg-gold text-ink'
const inactiveTab = 'flex-1 rounded-full px-4 py-2 text-sm font-bold text-slate-300'
function tick() { window.clearTimeout(timer); if (countdown.value <= 0) return; timer = window.setTimeout(() => { countdown.value -= 1; tick() }, 1000) }
onUnmounted(() => window.clearTimeout(timer))
async function handleSendCode() { if (!/^1\d{10}$/.test(mobile.value)) { error.value = '请输入有效手机号'; return } error.value = ''; countdown.value = 60; tick(); const result = await sendCode(mobile.value); if (!result.ok) { countdown.value = 0; error.value = '验证码发送失败，请重试' } }
async function handleSubmit() { if (!/^1\d{10}$/.test(mobile.value) || code.value.length < 4) { error.value = '请输入手机号和验证码'; return } const result = mode.value === 'login' ? await loginWithCode(mobile.value, code.value) : await registerWithCode(mobile.value, code.value); if (result.ok) { router.push('/dashboard'); return } error.value = mode.value === 'login' ? '登录失败，请检查验证码' : '注册失败，请重新获取验证码' }
</script>
