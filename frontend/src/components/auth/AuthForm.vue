<template>
  <form class="mx-auto max-w-md rounded-[2rem] border border-slate-200/80 bg-panel/80 p-7 shadow-2xl" @submit.prevent="handleSubmit">
    <div class="mb-6 flex rounded-full border border-slate-200/80 bg-ink-2 p-1">
      <button type="button" @click="mode = 'login'" :class="mode === 'login' ? activeTab : inactiveTab">登录</button>
      <button type="button" @click="mode = 'register'" :class="mode === 'register' ? activeTab : inactiveTab">注册</button>
    </div>

    <div v-if="mode === 'login'" class="mb-5 flex rounded-full border border-slate-200/80 bg-ink-2 p-1">
      <button type="button" @click="loginMethod = 'password'" :class="loginMethod === 'password' ? activeSmallTab : inactiveSmallTab">密码登录</button>
      <button type="button" @click="loginMethod = 'code'" :class="loginMethod === 'code' ? activeSmallTab : inactiveSmallTab">验证码登录</button>
    </div>

    <label class="block text-sm font-semibold text-slate-950">
      {{ accountLabel }}
      <input v-model.trim="mobile" :aria-label="accountLabel" class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900" :placeholder="accountPlaceholder" />
    </label>

    <label v-if="(mode === 'login' && loginMethod === 'password') || mode === 'register'" class="mt-5 block text-sm font-semibold text-slate-950">
      密码
      <span class="relative mt-2 block">
        <input v-model="password" :type="showPassword ? 'text' : 'password'" aria-label="密码" class="auth-password-input w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 pr-12 text-slate-900" placeholder="至少 6 位密码" />
        <button
          type="button"
          class="absolute inset-y-0 right-3 grid place-items-center rounded-full px-2 text-slate-500 transition hover:text-slate-950"
          :aria-label="showPassword ? '隐藏密码' : '显示密码'"
          :title="showPassword ? '隐藏密码' : '显示密码'"
          @click="showPassword = !showPassword"
        >
          <EyeOff v-if="showPassword" class="h-5 w-5" aria-hidden="true" />
          <Eye v-else class="h-5 w-5" aria-hidden="true" />
        </button>
      </span>
    </label>

    <div v-if="mode === 'register' || loginMethod === 'code'" class="mt-5 grid grid-cols-[1fr_auto] gap-3">
      <label class="block text-sm font-semibold text-slate-950">
        验证码
        <input v-model="code" aria-label="验证码" class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900" />
      </label>
      <button type="button" :disabled="countdown > 0 || sending" @click="handleSendCode" class="mt-7 rounded-2xl border border-gold/35 px-4 py-3 text-sm font-bold text-slate-700 disabled:border-slate-200/80 disabled:text-slate-500">{{ sending ? '发送中' : countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}</button>
    </div>

    <p v-if="debugCode" class="mt-4 text-sm text-slate-500">开发验证码：{{ debugCode }}</p>
    <p v-if="error" class="mt-4 text-sm text-slate-700" role="alert">{{ error }}</p>
    <button type="submit" :disabled="submitting" class="mt-7 w-full rounded-full bg-gold px-5 py-3 text-sm font-black text-white shadow-glow disabled:opacity-60">{{ submitting ? '处理中' : mode === 'login' ? '登录用户中心' : '完成注册' }}</button>
    <button type="button" class="mt-4 w-full rounded-full border border-slate-200 px-5 py-3 text-sm font-bold text-slate-950">微信小程序登录</button>
  </form>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import { Eye, EyeOff } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { loginWithCode, loginWithPassword, registerWithCode, sendCode } from '@/api/client'
import { saveAuth } from '@/stores/auth'
import { getAccountLabel, getAccountPlaceholder } from './authFormCopy'
import { canUseCodeAccount, canUsePasswordLoginAccount, canUseRegisterAccount, normalizeAccount } from './credentialRules'

const router = useRouter()
const mode = ref<'login' | 'register'>('login')
const loginMethod = ref<'password' | 'code'>('password')
const mobile = ref('')
const code = ref('')
const password = ref('')
const countdown = ref(0)
const error = ref('')
const debugCode = ref('')
const sending = ref(false)
const submitting = ref(false)
const showPassword = ref(false)
let timer: number | undefined
const activeTab = 'flex-1 rounded-full px-4 py-2 text-sm font-bold bg-gold text-white'
const inactiveTab = 'flex-1 rounded-full px-4 py-2 text-sm font-bold text-slate-600'
const activeSmallTab = 'flex-1 rounded-full px-3 py-1.5 text-xs font-bold bg-white/15 text-slate-950'
const inactiveSmallTab = 'flex-1 rounded-full px-3 py-1.5 text-xs font-bold text-slate-500'
const accountLabel = computed(() => getAccountLabel(mode.value, loginMethod.value))
const accountPlaceholder = computed(() => getAccountPlaceholder(mode.value, loginMethod.value))

watch([mode, loginMethod], () => {
  showPassword.value = false
})

function tick() { window.clearTimeout(timer); if (countdown.value <= 0) return; timer = window.setTimeout(() => { countdown.value -= 1; tick() }, 1000) }
onUnmounted(() => window.clearTimeout(timer))

function validateBase() {
  const account = normalizeAccount(mobile.value)
  if (mode.value === 'register' && !canUseRegisterAccount(account)) {
    error.value = '请输入有效手机号'
    return false
  }
  if (mode.value === 'login' && loginMethod.value === 'password' && !canUsePasswordLoginAccount(account)) {
    error.value = '请输入有效手机号或管理员账号'
    return false
  }
  if (mode.value === 'login' && loginMethod.value === 'code' && !canUseCodeAccount(account)) {
    error.value = '请输入有效手机号'
    return false
  }
  if ((mode.value === 'register' || loginMethod.value === 'password') && password.value.length < 6) {
    error.value = '请输入至少 6 位密码'
    return false
  }
  if ((mode.value === 'register' || loginMethod.value === 'code') && code.value.length < 4) {
    error.value = '请输入验证码'
    return false
  }
  return true
}

async function handleSendCode() {
  const account = normalizeAccount(mobile.value)
  if (!canUseCodeAccount(account)) { error.value = '请输入有效手机号'; return }
  error.value = ''
  debugCode.value = ''
  countdown.value = 60
  sending.value = true
  tick()
  try {
    const result = await sendCode(account)
    if (!result.ok) { countdown.value = 0; error.value = '验证码发送失败，请重试'; return }
    debugCode.value = result.debugCode ?? ''
  } catch {
    countdown.value = 0
    error.value = '验证码发送失败，请重试'
  } finally {
    sending.value = false
  }
}

async function handleSubmit() {
  error.value = ''
  if (!validateBase()) return
  const account = normalizeAccount(mobile.value)
  submitting.value = true
  try {
    const result = mode.value === 'register'
      ? await registerWithCode(account, code.value, password.value)
      : loginMethod.value === 'password'
        ? await loginWithPassword(account, password.value)
        : await loginWithCode(account, code.value)
    if (result.ok && result.user) {
      saveAuth(result.token, result.user)
      router.push((router.currentRoute.value.query.redirect as string) || '/dashboard')
      return
    }
    error.value = mode.value === 'login' ? '登录失败，请检查账号信息' : '注册失败，请检查验证码'
  } catch {
    error.value = mode.value === 'login' ? '登录失败，请检查账号信息' : '注册失败，请检查验证码'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth-password-input::-ms-reveal,
.auth-password-input::-ms-clear {
  display: none;
  height: 0;
  width: 0;
}
</style>
