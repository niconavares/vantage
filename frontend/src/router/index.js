import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login',                   component: () => import('@/views/Login.vue'),      meta: { public: true } },
  { path: '/',                        component: () => import('@/views/Dashboard.vue')   },
  { path: '/engagements',             component: () => import('@/views/Engagements.vue') },
  { path: '/engagements/:id',         component: () => import('@/views/Engagement.vue')  },
  { path: '/engagements/:id/scan',    component: () => import('@/views/NewScan.vue')     },
  { path: '/engagements/:id/network', component: () => import('@/views/NetworkMap.vue')  },
  { path: '/engagements/:id/report',  component: () => import('@/views/Report.vue')      },
  { path: '/hosts/:id',               component: () => import('@/views/HostDetail.vue')  },
  { path: '/vulns',                   component: () => import('@/views/Vulnerabilities.vue') },
  { path: '/vulns/:id',               component: () => import('@/views/VulnDetail.vue')  },
  { path: '/credentials',             component: () => import('@/views/Credentials.vue') },
  { path: '/ai-assistant',            component: () => import('@/views/AIAssistant.vue') },
  { path: '/scan-jobs',               component: () => import('@/views/ScanJobs.vue')    },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.token) return '/login'
})

export default router
