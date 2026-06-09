import { computed, ref } from 'vue'
import { getMe, logout as logoutRequest, setAuthToken } from '@/api/client'
import type { AuthUser } from '@/types/domain'

const TOKEN_KEY = 'ganggang_auth_token'

const token = ref(localStorage.getItem(TOKEN_KEY) ?? '')
const currentUser = ref<AuthUser | null>(null)
const loadingUser = ref(false)

setAuthToken(token.value)

export const isAuthenticated = computed(() => Boolean(token.value && currentUser.value))
export const user = computed(() => currentUser.value)
export const isLoadingUser = computed(() => loadingUser.value)

export function saveAuth(tokenValue: string, authUser: AuthUser) {
  token.value = tokenValue
  currentUser.value = authUser
  localStorage.setItem(TOKEN_KEY, tokenValue)
  setAuthToken(tokenValue)
}

export async function loadCurrentUser() {
  if (!token.value) return null
  loadingUser.value = true
  try {
    currentUser.value = await getMe()
    return currentUser.value
  } catch {
    clearAuth()
    return null
  } finally {
    loadingUser.value = false
  }
}

export async function logout() {
  try {
    if (token.value) await logoutRequest()
  } finally {
    clearAuth()
  }
}

export function clearAuth() {
  token.value = ''
  currentUser.value = null
  localStorage.removeItem(TOKEN_KEY)
  setAuthToken('')
}
