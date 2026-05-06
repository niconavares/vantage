<template>
  <div class="space-y-6">

    <!-- Header -->
    <div class="flex items-center justify-between animate-entry">
      <div>
        <h1 class="page-title">Command Center</h1>
        <p class="page-subtitle mt-0.5">Visión global de todas las operaciones de auditoría</p>
      </div>
      <RouterLink to="/engagements" class="btn-primary">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        Nuevo Engagement
      </RouterLink>
    </div>

    <!-- KPI row -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 animate-entry-1">

      <div class="stat-card border-glow-cyan">
        <div class="flex items-center justify-between mb-1">
          <span class="stat-label">Engagements activos</span>
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.15);">
            <svg class="w-4 h-4 text-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
          </div>
        </div>
        <div class="stat-value text-cyan">{{ stats.active_engagements }}</div>
      </div>

      <div class="stat-card">
        <div class="flex items-center justify-between mb-1">
          <span class="stat-label">Hosts auditados</span>
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background:rgba(76,201,240,0.08);border:1px solid rgba(76,201,240,0.15);">
            <svg class="w-4 h-4 text-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/></svg>
          </div>
        </div>
        <div class="stat-value text-blue">{{ stats.total_hosts }}</div>
      </div>

      <div class="stat-card">
        <div class="flex items-center justify-between mb-1">
          <span class="stat-label">Vulnerabilidades</span>
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background:rgba(255,107,53,0.08);border:1px solid rgba(255,107,53,0.15);">
            <svg class="w-4 h-4 text-orange" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
          </div>
        </div>
        <div class="stat-value text-orange">{{ stats.total_vulns }}</div>
      </div>

      <div class="stat-card" :class="stats.critical_vulns > 0 ? 'card-threat' : ''">
        <div class="flex items-center justify-between mb-1">
          <span class="stat-label">Críticas abiertas</span>
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="stats.critical_vulns > 0 ? 'animate-pulse-red' : ''" style="background:rgba(255,56,100,0.08);border:1px solid rgba(255,56,100,0.15);">
            <svg class="w-4 h-4 text-red" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          </div>
        </div>
        <div class="stat-value text-red">{{ stats.critical_vulns }}</div>
      </div>
    </div>

    <!-- Main content -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-4 animate-entry-2">

      <!-- Recent engagements -->
      <div class="lg:col-span-3 card">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <div class="w-1 h-5 rounded-full bg-cyan"></div>
            <span class="section-title">Engagements Recientes</span>
          </div>
          <RouterLink to="/engagements" class="text-xs hover:text-cyan transition-colors" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:600;letter-spacing:0.06em;">VER TODOS →</RouterLink>
        </div>

        <div class="space-y-2">
          <div v-for="eng in stats.recent_engagements" :key="eng.id" class="relative group/eng">
            <RouterLink
              :to="`/engagements/${eng.id}`"
              class="flex items-center justify-between p-3 rounded-xl transition-all cursor-pointer"
              style="background:rgba(0,0,0,0.3);border:1px solid #1e2d3d;"
              onmouseover="this.style.borderColor='rgba(0,212,255,0.2)'"
              onmouseout="this.style.borderColor='#1e2d3d'">
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 text-base"
                  :style="`background:${eng.stats?.critical > 0 ? 'rgba(255,56,100,0.1)' : eng.stats?.high > 0 ? 'rgba(255,107,53,0.1)' : 'rgba(0,212,255,0.08)'};border:1px solid ${eng.stats?.critical > 0 ? 'rgba(255,56,100,0.2)' : eng.stats?.high > 0 ? 'rgba(255,107,53,0.2)' : 'rgba(0,212,255,0.15)'}`">
                  🎯
                </div>
                <div class="min-w-0">
                  <div class="text-sm font-semibold text-white truncate group-hover/eng:text-cyan transition-colors" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.02em;">{{ eng.name }}</div>
                  <div class="text-xs truncate" style="color:#4b6277;">{{ eng.client }}</div>
                </div>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0 ml-3 pr-7">
                <span v-if="eng.stats?.critical" class="badge-critical">{{ eng.stats.critical }}</span>
                <span v-if="eng.stats?.high"     class="badge-high">{{ eng.stats.high }}</span>
                <span v-if="eng.stats?.medium"   class="badge-medium">{{ eng.stats.medium }}</span>
                <StatusBadge :status="eng.status" />
              </div>
            </RouterLink>
            <!-- Delete button overlaid on top-right -->
            <button @click.prevent="deleteEngagement(eng)"
              class="absolute top-2 right-2 w-7 h-7 rounded-lg flex items-center justify-center transition-all hover:scale-110 opacity-0 group-hover/eng:opacity-100"
              style="color:#ff3864;background:rgba(255,56,100,0.12);border:1px solid rgba(255,56,100,0.25);"
              title="Eliminar engagement">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>

          <div v-if="!stats.recent_engagements?.length" class="text-center py-10">
            <div class="text-4xl mb-3 opacity-50">🎯</div>
            <div class="text-sm" style="color:#4b6277;">No hay engagements aún</div>
            <RouterLink to="/engagements" class="btn-primary mt-4 mx-auto inline-flex">Crear el primero</RouterLink>
          </div>
        </div>
      </div>

      <!-- Risk chart -->
      <div class="lg:col-span-2 card">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-5 rounded-full bg-red"></div>
          <span class="section-title">Distribución de Riesgo</span>
        </div>
        <apexchart v-if="chartReady && chartSeries.some(v => v > 0)" type="donut" height="200" :options="chartOpts" :series="chartSeries" />
        <div v-else class="flex flex-col items-center justify-center h-48 gap-3">
          <div class="text-5xl opacity-30">📊</div>
          <span class="text-sm" style="color:#4b6277;">Sin datos de vulnerabilidades</span>
        </div>

        <!-- Legend -->
        <div v-if="chartSeries.some(v => v > 0)" class="grid grid-cols-2 gap-2 mt-4">
          <div v-for="(item, i) in chartLegend" :key="i" class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full flex-shrink-0" :style="`background:${item.color}`"></div>
            <span class="text-xs" style="color:#4b6277;">{{ item.label }}</span>
            <span class="text-xs font-bold ml-auto" :style="`color:${item.color}`">{{ chartSeries[i] }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Threat feed -->
    <div v-if="recentVulns.length" class="card animate-entry-3">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <div class="w-1 h-5 rounded-full bg-red"></div>
          <span class="section-title">Últimas Amenazas Detectadas</span>
        </div>
        <RouterLink to="/vulns" class="text-xs hover:text-cyan transition-colors" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:600;">VER TODAS →</RouterLink>
      </div>
      <div class="overflow-x-auto">
        <table class="vtable">
          <thead><tr>
            <th>Severidad</th><th>Vulnerabilidad</th><th>Host</th><th>CVE</th><th>Estado</th>
          </tr></thead>
          <tbody>
            <tr v-for="v in recentVulns" :key="v.id">
              <td><span :class="`badge-${v.severity}`">{{ v.severity }}</span></td>
              <td class="max-w-xs">
                <RouterLink :to="`/vulns/${v.id}`" class="text-sm font-medium hover:text-cyan transition-colors truncate block max-w-xs" style="color:#c9d8e5;">{{ v.title }}</RouterLink>
              </td>
              <td><span class="font-mono text-xs text-cyan">{{ v.host_ip }}</span></td>
              <td><span class="font-mono text-xs" style="color:#4b6277;">{{ v.cve_id || '—' }}</span></td>
              <td>
                <span class="text-xs px-2 py-0.5 rounded border" style="border-color:rgba(255,56,100,0.2);color:#ff3864;background:rgba(255,56,100,0.06);">open</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/composables/api'
import StatusBadge from '@/components/StatusBadge.vue'

const stats       = ref({ active_engagements: 0, total_hosts: 0, total_vulns: 0, critical_vulns: 0, recent_engagements: [] })
const recentVulns = ref([])
const chartReady  = ref(false)

const chartSeries = computed(() => {
  const r = stats.value.recent_engagements || []
  return r.reduce((acc, e) => {
    acc[0] += e.stats?.critical || 0
    acc[1] += e.stats?.high     || 0
    acc[2] += e.stats?.medium   || 0
    acc[3] += e.stats?.low      || 0
    return acc
  }, [0, 0, 0, 0])
})

const chartLegend = [
  { label: 'Crítica', color: '#ff3864' },
  { label: 'Alta',    color: '#ff6b35' },
  { label: 'Media',   color: '#f59e0b' },
  { label: 'Baja',    color: '#4cc9f0' },
]

const chartOpts = {
  labels: ['Crítica', 'Alta', 'Media', 'Baja'],
  colors: ['#ff3864', '#ff6b35', '#f59e0b', '#4cc9f0'],
  chart: { background: 'transparent', toolbar: { show: false }, sparkline: { enabled: false } },
  legend: { show: false },
  dataLabels: { enabled: false },
  stroke: { colors: ['#0d1117'], width: 2 },
  plotOptions: { pie: { donut: { size: '72%', labels: {
    show: true,
    total: { show: true, color: '#4b6277', label: 'Total', fontSize: '11px',
      formatter: (w) => w.globals.seriesTotals.reduce((a,b) => a+b, 0)
    }
  }}}},
  tooltip: { theme: 'dark', style: { fontFamily: 'JetBrains Mono' } },
  theme: { mode: 'dark' },
}

async function deleteEngagement(eng) {
  if (!confirm(`¿Eliminar "${eng.name}"?\nSe borrarán todos los hosts, vulnerabilidades y escaneos asociados.`)) return
  try {
    await api.delete(`/engagements/${eng.id}/`)
    stats.value.recent_engagements = stats.value.recent_engagements.filter(e => e.id !== eng.id)
  } catch (e) {
    alert('Error al eliminar: ' + (e.response?.data?.detail || e.message))
  }
}

onMounted(async () => {
  try {
    const [dashRes, vulnRes] = await Promise.all([
      api.get('/dashboard/'),
      api.get('/vulns/?severity=critical&severity=high&status=open&page_size=5').catch(() => ({ data: { results: [] } })),
    ])
    stats.value       = dashRes.data.results?.[0] || dashRes.data
    recentVulns.value = vulnRes.data.results || []
  } catch (e) {
    console.error('Dashboard load error:', e)
  } finally {
    chartReady.value = true
  }
})
</script>
