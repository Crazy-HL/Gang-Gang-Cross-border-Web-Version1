import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import DetectView from '@/views/DetectView.vue'
import DashboardView from '@/views/DashboardView.vue'
import ResultsView from '@/views/ResultsView.vue'
import ReportsView from '@/views/ReportsView.vue'
import AuthView from '@/views/AuthView.vue'
import AdminView from '@/views/AdminView.vue'
import { isAuthenticated, loadCurrentUser } from '@/stores/auth'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/detect', component: DetectView, meta: { requiresAuth: true } },
    { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/results/:id', component: ResultsView },
    { path: '/reports/:id', component: ReportsView },
    { path: '/auth', component: AuthView },
    { path: '/admin', component: AdminView, meta: { requiresAuth: true } }
  ]
})

router.beforeEach(async (to) => {
  if (to.path === '/auth' && isAuthenticated.value) return '/dashboard'
  if (!to.meta.requiresAuth) return true
  if (isAuthenticated.value) return true
  const user = await loadCurrentUser()
  return user ? true : `/auth?redirect=${encodeURIComponent(to.fullPath)}`
})
