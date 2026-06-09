import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import DetectView from '@/views/DetectView.vue'
import DashboardView from '@/views/DashboardView.vue'
import ResultsView from '@/views/ResultsView.vue'
import ReportsView from '@/views/ReportsView.vue'
import AuthView from '@/views/AuthView.vue'
import AdminView from '@/views/AdminView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/detect', component: DetectView },
    { path: '/dashboard', component: DashboardView },
    { path: '/results/:id', component: ResultsView },
    { path: '/reports/:id', component: ReportsView },
    { path: '/auth', component: AuthView },
    { path: '/admin', component: AdminView }
  ]
})
