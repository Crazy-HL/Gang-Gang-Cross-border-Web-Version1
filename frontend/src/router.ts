import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import DetectView from '@/views/DetectView.vue'
import DashboardView from '@/views/DashboardView.vue'
import ResultsView from '@/views/ResultsView.vue'
import ReportsView from '@/views/ReportsView.vue'
import AuthView from '@/views/AuthView.vue'
import AdminView from '@/views/AdminView.vue'
import NotificationsView from '@/views/NotificationsView.vue'
import AppealView from '@/views/AppealView.vue'
import TroSettlementView from '@/views/TroSettlementView.vue'
import { isAuthenticated, loadCurrentUser } from '@/stores/auth'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/detect', component: DetectView, meta: { requiresAuth: true } },
    { path: '/appeal', component: AppealView, meta: { requiresAuth: true } },
    { path: '/tro-settlement', component: TroSettlementView, meta: { requiresAuth: true } },
    { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/results/:id', component: ResultsView },
    { path: '/reports/:id', component: ReportsView, meta: { requiresAuth: true } },
    { path: '/auth', component: AuthView },
    { path: '/notifications', component: NotificationsView, meta: { requiresAuth: true } },
    { path: '/admin', component: AdminView, meta: { requiresAuth: true, requiresAdmin: true } }
  ]
})

router.beforeEach(async (to) => {
  if (to.path === '/auth' && isAuthenticated.value) return '/dashboard'
  if (!to.meta.requiresAuth) return true

  const currentUser = await loadCurrentUser()
  if (!currentUser) return `/auth?redirect=${encodeURIComponent(to.fullPath)}`
  if (to.meta.requiresAdmin && currentUser.role !== 'admin') return '/dashboard'

  return true
})
