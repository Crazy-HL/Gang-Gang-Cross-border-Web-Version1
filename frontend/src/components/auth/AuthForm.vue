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
      <input v-model.trim="mobile" :aria-label="accountLabel" class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-300 focus:ring-4 focus:ring-blue-100" :placeholder="accountPlaceholder" />
    </label>

    <label v-if="(mode === 'login' && loginMethod === 'password') || mode === 'register'" class="mt-5 block text-sm font-semibold text-slate-950">
      密码
      <span class="relative mt-2 block">
        <input v-model="password" :type="showPassword ? 'text' : 'password'" aria-label="密码" class="auth-password-input w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 pr-12 text-slate-900 outline-none transition focus:border-blue-300 focus:ring-4 focus:ring-blue-100" placeholder="至少 6 位密码" />
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
        <input v-model="code" aria-label="验证码" class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-300 focus:ring-4 focus:ring-blue-100" />
      </label>
      <button type="button" :disabled="countdown > 0 || sending" @click="handleSendCode" class="mt-7 rounded-2xl border border-gold/35 px-4 py-3 text-sm font-bold text-slate-700 disabled:border-slate-200/80 disabled:text-slate-500">{{ sending ? '发送中' : countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}</button>
    </div>

    <p v-if="debugCode" class="mt-4 text-sm text-slate-500">开发验证码：{{ debugCode }}</p>
    <p v-if="error" class="mt-4 text-sm text-slate-700" role="alert">{{ error }}</p>
    <button type="submit" :disabled="submitting" class="mt-7 w-full rounded-full bg-gold px-5 py-3 text-sm font-black text-white shadow-glow disabled:opacity-60">{{ submitting ? '处理中' : mode === 'login' ? '登录用户中心' : '完成注册' }}</button>
    <button type="button" :disabled="wechatLoading" class="mt-4 w-full rounded-full border border-slate-200 px-5 py-3 text-sm font-bold text-slate-950 transition hover:border-blue-200 hover:text-blue-700 disabled:opacity-60" @click="startWechatWebLogin">
      {{ wechatLoading ? '正在打开微信' : '微信扫码登陆' }}
    </button>
  </form>

  <div v-if="showPasswordSetup" class="fixed inset-0 z-50 grid place-items-center bg-slate-950/45 px-5">
    <form class="w-full max-w-sm rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl" @submit.prevent="submitPasswordSetup">
      <h2 class="text-xl font-black text-slate-950">设置新密码</h2>
      <p class="mt-2 text-sm leading-6 text-slate-600">检测到该手机号已通过小程序登录，但还没有网页端密码。设置后下次可直接密码登录。</p>
      <label class="mt-5 block text-sm font-semibold text-slate-950">
        新密码
        <span class="relative mt-2 block">
          <input v-model="setupPassword" :type="showSetupPassword ? 'text' : 'password'" aria-label="设置新密码" class="auth-password-input w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 pr-12 text-slate-900 outline-none transition focus:border-blue-300 focus:ring-4 focus:ring-blue-100" placeholder="至少 6 位密码" />
          <button
            type="button"
            class="absolute inset-y-0 right-3 grid place-items-center rounded-full px-2 text-slate-500 transition hover:text-slate-950"
            :aria-label="showSetupPassword ? '隐藏密码' : '显示密码'"
            :title="showSetupPassword ? '隐藏密码' : '显示密码'"
            @click="showSetupPassword = !showSetupPassword"
          >
            <EyeOff v-if="showSetupPassword" class="h-5 w-5" aria-hidden="true" />
            <Eye v-else class="h-5 w-5" aria-hidden="true" />
          </button>
        </span>
      </label>
      <p v-if="setupPasswordError" class="mt-4 text-sm text-slate-700" role="alert">{{ setupPasswordError }}</p>
      <button type="submit" :disabled="settingPassword" class="mt-6 w-full rounded-full bg-gold px-5 py-3 text-sm font-black text-white shadow-glow disabled:opacity-60">{{ settingPassword ? '保存中' : '保存并进入' }}</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { Eye, EyeOff } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import { getWechatWebLoginUrl, loginWithCode, loginWithPassword, loginWithWechatWebCode, registerWithCode, sendCode, setPassword } from '@/api/client'
import { loadCurrentUser, saveAuth } from '@/stores/auth'
import type { AuthUser } from '@/types/domain'
import { getAccountLabel, getAccountPlaceholder } from './authFormCopy'
import { canUseCodeAccount, canUsePasswordLoginAccount, canUseRegisterAccount, normalizeAccount } from './credentialRules'

type LoginResult = {
  ok: boolean
  token: string
  user: AuthUser | null
  needsPasswordSetup?: boolean
  reason?: string
}

const WECHAT_STATE_KEY = 'wechat_login_state'
const WECHAT_REDIRECT_KEY = 'wechat_login_redirect'

const router = useRouter()
const route = useRoute()
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
const wechatLoading = ref(false)
const showPassword = ref(false)
const showPasswordSetup = ref(false)
const setupPassword = ref('')
const setupPasswordError = ref('')
const showSetupPassword = ref(false)
const settingPassword = ref(false)
const postLoginRedirect = ref('/dashboard')
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

onMounted(() => {
  handleWechatWebCallback()
})

function tick() {
  window.clearTimeout(timer)
  if (countdown.value <= 0) return
  timer = window.setTimeout(() => {
    countdown.value -= 1
    tick()
  }, 1000)
}

onUnmounted(() => window.clearTimeout(timer))

function firstQueryValue(value: unknown) {
  if (Array.isArray(value)) return String(value[0] ?? '')
  return typeof value === 'string' ? value : ''
}

function redirectAfterLogin() {
  return firstQueryValue(route.query.redirect) || sessionStorage.getItem(WECHAT_REDIRECT_KEY) || '/dashboard'
}

function createWechatState() {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

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
  if (!canUseCodeAccount(account)) {
    error.value = '请输入有效手机号'
    return
  }
  error.value = ''
  debugCode.value = ''
  countdown.value = 60
  sending.value = true
  tick()
  try {
    const result = await sendCode(account)
    if (!result.ok) {
      countdown.value = 0
      error.value = '验证码发送失败，请重试'
      return
    }
    debugCode.value = result.debugCode ?? ''
  } catch {
    countdown.value = 0
    error.value = '验证码发送失败，请重试'
  } finally {
    sending.value = false
  }
}

function completeLogin(result: LoginResult) {
  if (!result.user) return
  saveAuth(result.token, result.user)
  postLoginRedirect.value = redirectAfterLogin()
  sessionStorage.removeItem(WECHAT_REDIRECT_KEY)
  if (result.needsPasswordSetup) {
    setupPassword.value = ''
    setupPasswordError.value = ''
    showSetupPassword.value = false
    showPasswordSetup.value = true
    return
  }
  router.push(postLoginRedirect.value)
}

function registerErrorMessage(reason?: string) {
  if (reason === 'password_not_set') return '该手机号已注册，但还没有设置密码。请切换到验证码登录，验证码登录后设置密码。'
  if (reason === 'already_registered') return '该手机号已注册，请直接登录。'
  return '注册失败，请检查验证码'
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
      completeLogin(result)
      return
    }
    if (mode.value === 'register') {
      error.value = registerErrorMessage(result.reason)
    } else if (result.reason === 'password_not_set') {
      error.value = '该手机号还没有设置密码，请使用验证码登录后设置密码。'
      loginMethod.value = 'code'
    } else {
      error.value = '登录失败，请检查账号信息'
    }
  } catch {
    error.value = mode.value === 'login' ? '登录失败，请检查账号信息' : '注册失败，请检查验证码'
  } finally {
    submitting.value = false
  }
}

async function startWechatWebLogin() {
  error.value = ''
  wechatLoading.value = true
  try {
    const state = createWechatState()
    sessionStorage.setItem(WECHAT_STATE_KEY, state)
    sessionStorage.setItem(WECHAT_REDIRECT_KEY, redirectAfterLogin())
    const redirectUri = `${window.location.origin}/auth?wechat=1`
    const result = await getWechatWebLoginUrl(redirectUri, state)
    if (result.ok && result.url) {
      window.location.href = result.url
      return
    }
    error.value = '微信扫码登录暂未配置，请先使用手机号登录。'
  } catch {
    error.value = '微信扫码登录暂时不可用，请先使用手机号登录。'
  } finally {
    wechatLoading.value = false
  }
}

async function handleWechatWebCallback() {
  const isWechatCallback = firstQueryValue(route.query.wechat) === '1'
  const oauthCode = firstQueryValue(route.query.code)
  if (!isWechatCallback || !oauthCode) return

  const expectedState = sessionStorage.getItem(WECHAT_STATE_KEY)
  const actualState = firstQueryValue(route.query.state)
  if (expectedState && actualState && expectedState !== actualState) {
    error.value = '微信登录状态已失效，请重新扫码。'
    return
  }

  sessionStorage.removeItem(WECHAT_STATE_KEY)
  submitting.value = true
  try {
    const result = await loginWithWechatWebCode(oauthCode)
    if (result.ok && result.user) {
      completeLogin(result)
      return
    }
    error.value = '微信扫码登录失败，请重试。'
  } catch {
    error.value = '微信扫码登录失败，请重试。'
  } finally {
    submitting.value = false
  }
}

async function submitPasswordSetup() {
  setupPasswordError.value = ''
  if (setupPassword.value.length < 6) {
    setupPasswordError.value = '请输入至少 6 位密码'
    return
  }
  settingPassword.value = true
  try {
    const result = await setPassword(setupPassword.value)
    if (!result.ok) {
      setupPasswordError.value = '密码设置失败，请重试'
      return
    }
    if (result.user) await loadCurrentUser()
    showPasswordSetup.value = false
    router.push(postLoginRedirect.value)
  } catch {
    setupPasswordError.value = '密码设置失败，请重试'
  } finally {
    settingPassword.value = false
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
