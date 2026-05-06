<template>
  <header class="h-13 flex items-center justify-between px-6 sticky top-0 z-40"
    style="background:rgba(6,9,16,0.85);border-bottom:1px solid #1e2d3d;backdrop-filter:blur(16px);height:52px;">

    <!-- Breadcrumb -->
    <nav class="flex items-center gap-2 text-sm">
      <template v-for="(crumb, i) in breadcrumbs" :key="i">
        <RouterLink v-if="i < breadcrumbs.length - 1" :to="crumb.path"
          class="transition-colors hover:text-cyan" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:600;letter-spacing:0.04em;font-size:13px;">
          {{ crumb.label }}
        </RouterLink>
        <span v-else style="color:#e2e8f0;font-family:'Rajdhani',sans-serif;font-weight:700;letter-spacing:0.04em;font-size:13px;">{{ crumb.label }}</span>
        <svg v-if="i < breadcrumbs.length - 1" class="w-3 h-3" style="color:#2d4356;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </template>
    </nav>

    <!-- Right -->
    <div class="flex items-center gap-3">
      <!-- Active scan indicator -->
      <Transition name="v">
        <div v-if="activeJobs > 0" class="scan-running">
          <span class="w-2 h-2 rounded-full bg-cyan animate-pulse"></span>
          {{ activeJobs }} SCAN{{ activeJobs > 1 ? 'S' : '' }} ACTIVO{{ activeJobs > 1 ? 'S' : '' }}
        </div>
      </Transition>

      <!-- Clock -->
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#2d4356;letter-spacing:0.08em;">
        {{ clock }}
      </div>

      <!-- Divider -->
      <div style="width:1px;height:20px;background:#1e2d3d;"></div>

      <!-- User avatar -->
      <div class="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold" style="background:linear-gradient(135deg,rgba(0,212,255,0.15),rgba(0,212,255,0.05));border:1px solid rgba(0,212,255,0.2);color:#00d4ff;font-family:'Rajdhani',sans-serif;">
        {{ auth.user?.username?.slice(0,2).toUpperCase() || 'OP' }}
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/composables/api'

const route      = useRoute()
const auth       = useAuthStore()
const activeJobs = ref(0)
const clock      = ref('')

let clockInterval, pollInterval

function updateClock() {
  clock.value = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
}

const ROUTE_LABELS = {
  '/':            [{ label: 'Dashboard', path: '/' }],
  '/engagements': [{ label: 'Dashboard', path: '/' }, { label: 'Engagements', path: '/engagements' }],
  '/vulns':       [{ label: 'Dashboard', path: '/' }, { label: 'Vulnerabilidades', path: '/vulns' }],
  '/credentials': [{ label: 'Dashboard', path: '/' }, { label: 'Credenciales', path: '/credentials' }],
  '/scan-jobs':   [{ label: 'Dashboard', path: '/' }, { label: 'Scan Jobs', path: '/scan-jobs' }],
  '/ai-assistant':[{ label: 'Dashboard', path: '/' }, { label: 'AI Assistant', path: '/ai-assistant' }],
}

const breadcrumbs = computed(() => {
  const p = route.path
  if (ROUTE_LABELS[p]) return ROUTE_LABELS[p]
  if (p.match(/\/engagements\/[^/]+\/scan/)) return [{ label: 'Dashboard', path: '/' }, { label: 'Engagements', path: '/engagements' }, { label: 'Nuevo Scan', path: p }]
  if (p.match(/\/engagements\/[^/]+\/network/)) return [{ label: 'Dashboard', path: '/' }, { label: 'Engagements', path: '/engagements' }, { label: 'Red', path: p }]
  if (p.match(/\/engagements\/[^/]+\/report/)) return [{ label: 'Dashboard', path: '/' }, { label: 'Engagements', path: '/engagements' }, { label: 'Informe', path: p }]
  if (p.match(/\/engagements\//)) return [{ label: 'Dashboard', path: '/' }, { label: 'Engagements', path: '/engagements' }, { label: 'Detalle', path: p }]
  if (p.match(/\/vulns\//))       return [{ label: 'Dashboard', path: '/' }, { label: 'Vulns', path: '/vulns' }, { label: 'Detalle', path: p }]
  if (p.match(/\/hosts\//))       return [{ label: 'Dashboard', path: '/' }, { label: 'Host', path: p }]
  return [{ label: p, path: p }]
})

async function pollJobs() {
  try {
    const r = await api.get('/scan-jobs/?status=1&page_size=1')
    activeJobs.value = r.data.count || 0
  } catch {}
}

onMounted(() => {
  updateClock()
  clockInterval = setInterval(updateClock, 1000)
  pollJobs()
  pollInterval = setInterval(pollJobs, 10000)
})
onUnmounted(() => { clearInterval(clockInterval); clearInterval(pollInterval) })
</script>
