<template>
  <div v-if="eng" class="space-y-5 animate-entry">

    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 text-sm">
      <RouterLink to="/engagements" class="hover:text-cyan transition-colors" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:600;">ENGAGEMENTS</RouterLink>
      <svg class="w-3 h-3" style="color:#2d4356;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
      <span class="text-sm" style="color:#8ba5bc;font-family:'Rajdhani',sans-serif;font-weight:600;">{{ eng.name }}</span>
    </div>

    <!-- Header -->
    <div class="card" style="background:linear-gradient(135deg,rgba(0,212,255,0.04),rgba(0,0,0,0.6));">
      <div class="flex items-start justify-between gap-6 flex-wrap">
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-3 flex-wrap">
            <select v-model="eng.status" @change="updateStatus"
              class="text-xs font-bold uppercase px-2 py-0.5 rounded cursor-pointer outline-none transition-all"
              :style="`font-family:'Rajdhani',sans-serif;letter-spacing:0.06em;border:1px solid ${eng.status==='active'?'rgba(0,212,255,0.3)':eng.status==='completed'?'rgba(0,255,157,0.3)':eng.status==='paused'?'rgba(245,158,11,0.3)':'rgba(75,98,119,0.4)'};background:${eng.status==='active'?'rgba(0,212,255,0.08)':eng.status==='completed'?'rgba(0,255,157,0.08)':eng.status==='paused'?'rgba(245,158,11,0.08)':'rgba(0,0,0,0.4)'};color:${eng.status==='active'?'#00d4ff':eng.status==='completed'?'#00ff9d':eng.status==='paused'?'#f59e0b':'#4b6277'}`">
              <option value="planning">Planificación</option>
              <option value="active">Activo</option>
              <option value="paused">Pausado</option>
              <option value="completed">Completado</option>
              <option value="archived">Archivado</option>
            </select>
            <span class="text-xs font-bold uppercase px-2 py-0.5 rounded" style="color:#4b6277;background:rgba(0,0,0,0.4);border:1px solid #1e2d3d;font-family:'Rajdhani',sans-serif;letter-spacing:0.08em;">{{ eng.client }}</span>
            <span v-if="eng.start_date" class="font-mono text-xs" style="color:#2d4356;">{{ eng.start_date }} → {{ eng.end_date || 'ongoing' }}</span>
          </div>
          <h1 class="page-title" style="font-size:24px;">{{ eng.name }}</h1>
          <div v-if="eng.targets?.length" class="flex flex-wrap gap-2 mt-3">
            <span v-for="t in eng.targets" :key="t.id"
              class="font-mono text-xs px-2 py-1 rounded"
              :style="t.in_scope ? 'color:#00d4ff;background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.15);' : 'color:#4b6277;background:rgba(0,0,0,0.3);border:1px solid #1e2d3d;'">
              {{ t.value }}
            </span>
          </div>
        </div>
        <!-- Actions -->
        <div class="flex items-center gap-2 flex-wrap">
          <RouterLink :to="`/engagements/${id}/scan`" class="btn-primary text-sm">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            NUEVO SCAN
          </RouterLink>
          <RouterLink :to="`/engagements/${id}/network`" class="btn-ghost text-sm">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/></svg>
            MAPA RED
          </RouterLink>
          <RouterLink :to="`/engagements/${id}/report`" class="btn-ghost text-sm">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            INFORME
          </RouterLink>
          <button @click="deleteEngagement"
            class="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-bold uppercase tracking-wider transition-all hover:scale-105"
            style="color:#ff3864;background:rgba(255,56,100,0.1);border:1px solid rgba(255,56,100,0.25);font-family:'Rajdhani',sans-serif;">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            BORRAR
          </button>
        </div>
      </div>
    </div>

    <!-- KPI row -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
      <div class="stat-card animate-entry-1"><div class="stat-value text-cyan">{{ dash.totals?.hosts || 0 }}</div><div class="stat-label">Hosts</div></div>
      <div class="stat-card animate-entry-1"><div class="stat-value" style="color:#4cc9f0;">{{ dash.totals?.ports || 0 }}</div><div class="stat-label">Puertos</div></div>
      <div class="stat-card animate-entry-2"><div class="stat-value text-red">{{ dash.by_severity?.critical || 0 }}</div><div class="stat-label">Críticas</div></div>
      <div class="stat-card animate-entry-2"><div class="stat-value text-orange">{{ dash.by_severity?.high || 0 }}</div><div class="stat-label">Altas</div></div>
      <div class="stat-card animate-entry-3"><div class="stat-value text-green">{{ dash.totals?.creds || 0 }}</div><div class="stat-label">Credenciales</div></div>
    </div>

    <!-- AI Analysis -->
    <div v-if="aiAnalysis" class="card border-glow-cyan animate-entry-2" style="background:linear-gradient(135deg,rgba(0,212,255,0.04),rgba(0,0,0,0.5));">
      <div class="flex items-center gap-2 mb-3">
        <span class="text-cyan text-sm font-bold" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.06em;">🤖 ANÁLISIS CLAUDE AI</span>
      </div>
      <div class="text-sm leading-relaxed whitespace-pre-wrap" style="color:#8ba5bc;">{{ aiAnalysis }}</div>
    </div>

    <div v-else-if="aiLoading" class="card border-glow-cyan" style="background:rgba(0,212,255,0.03);">
      <div class="flex items-center gap-4">
        <svg class="w-6 h-6 animate-spin text-cyan flex-shrink-0" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
        <div>
          <div class="text-sm font-bold text-cyan" style="font-family:'Rajdhani',sans-serif;">CLAUDE ANALIZANDO RESULTADOS...</div>
          <div class="text-xs mt-0.5" style="color:#4b6277;">Generando cadena de ataque, impacto de negocio y recomendaciones</div>
        </div>
      </div>
    </div>

    <div v-else class="card border-glow-cyan animate-entry-3" style="background:rgba(0,212,255,0.02);">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="text-3xl opacity-40">🤖</div>
          <div>
            <div class="text-sm font-bold text-cyan" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.04em;">Análisis profundo con Claude AI</div>
            <div class="text-xs mt-0.5" style="color:#4b6277;">Cadena de ataque, impacto de negocio, recomendaciones priorizadas</div>
          </div>
        </div>
        <button @click="runAiAnalysis" class="btn-primary text-sm flex-shrink-0">
          Analizar con IA
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b" style="border-color:#1e2d3d;">
      <div class="flex gap-0">
        <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
          class="px-5 py-3 text-sm font-bold uppercase tracking-wider transition-all relative"
          :style="activeTab === tab.id
            ? 'color:#00d4ff;font-family:Rajdhani,sans-serif;letter-spacing:0.06em;'
            : 'color:#4b6277;font-family:Rajdhani,sans-serif;letter-spacing:0.06em;'">
          {{ tab.label }}
          <span v-if="tab.count" class="ml-2 text-[10px] px-1.5 py-0.5 rounded-full" style="background:#1e2d3d;color:#8ba5bc;">{{ tab.count }}</span>
          <div v-if="activeTab === tab.id" class="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan rounded-t"></div>
        </button>
      </div>
    </div>

    <!-- Tab: Hosts -->
    <div v-show="activeTab === 'hosts'">
      <div class="card p-0 overflow-hidden">
        <table class="vtable w-full">
          <thead>
            <tr>
              <th class="pl-5">IP / Hostname</th>
              <th>OS</th>
              <th>Puertos</th>
              <th>Críticas</th>
              <th>Altas</th>
              <th>Risk Score</th>
              <th class="pr-5"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!hosts.length"><td colspan="7" class="text-center py-12" style="color:#4b6277;">Sin hosts descubiertos</td></tr>
            <tr v-for="h in hosts" :key="h.id">
              <td class="pl-5">
                <div class="flex items-center gap-2">
                  <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="h.is_alive ? 'bg-green' : 'bg-muted'"></span>
                  <div>
                    <div class="font-mono text-sm text-cyan">{{ h.ip_address }}</div>
                    <div class="text-xs mt-0.5" style="color:#4b6277;">{{ h.hostname || '—' }}</div>
                  </div>
                </div>
              </td>
              <td>
                <span class="text-xs" style="color:#8ba5bc;">{{ h.os_name || 'Desconocido' }}</span>
              </td>
              <td><span class="font-mono font-bold text-cyan">{{ h.open_ports }}</span></td>
              <td>
                <span v-if="h.vuln_counts?.critical" class="badge-critical">{{ h.vuln_counts.critical }}</span>
                <span v-else style="color:#2d4356;">—</span>
              </td>
              <td>
                <span v-if="h.vuln_counts?.high" class="badge-high">{{ h.vuln_counts.high }}</span>
                <span v-else style="color:#2d4356;">—</span>
              </td>
              <td>
                <div class="flex items-center gap-2">
                  <div class="h-1 rounded-full overflow-hidden" style="background:#1e2d3d;width:60px;">
                    <div class="h-full rounded-full transition-all"
                      :style="`width:${Math.min(h.risk_score || 0, 100)}%;background:${(h.risk_score || 0) > 70 ? '#ff3864' : (h.risk_score || 0) > 40 ? '#ff6b35' : '#00ff9d'}`"></div>
                  </div>
                  <span class="font-mono text-xs" :style="`color:${(h.risk_score || 0) > 70 ? '#ff3864' : (h.risk_score || 0) > 40 ? '#ff6b35' : '#00ff9d'}`">{{ (h.risk_score || 0).toFixed(0) }}</span>
                </div>
              </td>
              <td class="pr-5">
                <RouterLink :to="`/hosts/${h.id}`" class="text-xs font-bold hover:text-cyan transition-colors" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">VER →</RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab: Vulns -->
    <div v-show="activeTab === 'vulns'">
      <div class="card p-0 overflow-hidden">
        <table class="vtable w-full">
          <thead>
            <tr>
              <th class="pl-5">Sev</th>
              <th>Vulnerabilidad</th>
              <th>Host</th>
              <th>CVE</th>
              <th>CVSS</th>
              <th class="pr-5">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!vulns.length"><td colspan="6" class="text-center py-12" style="color:#4b6277;">Sin vulnerabilidades detectadas</td></tr>
            <tr v-for="v in vulns" :key="v.id">
              <td class="pl-5">
                <div class="flex items-center gap-2">
                  <div class="w-1.5 h-1.5 rounded-full flex-shrink-0" :style="`background:${SCOLOR[v.severity]};box-shadow:0 0 6px ${SCOLOR[v.severity]}80`"></div>
                  <span :class="`badge-${v.severity}`">{{ v.severity }}</span>
                </div>
              </td>
              <td class="max-w-xs">
                <RouterLink :to="`/vulns/${v.id}`" class="text-sm font-semibold hover:text-cyan transition-colors truncate block max-w-[280px]" style="color:#c9d8e5;font-family:'Rajdhani',sans-serif;">{{ v.title }}</RouterLink>
              </td>
              <td><span class="font-mono text-xs text-cyan">{{ v.host_ip }}</span></td>
              <td>
                <a v-if="v.cve_id" :href="`https://nvd.nist.gov/vuln/detail/${v.cve_id}`" target="_blank"
                  class="font-mono text-xs hover:underline" style="color:#4cc9f0;">{{ v.cve_id }}</a>
                <span v-else class="font-mono text-xs" style="color:#2d4356;">—</span>
              </td>
              <td>
                <span v-if="v.cvss_score" class="font-mono text-xs font-bold"
                  :style="`color:${v.cvss_score >= 9 ? '#ff3864' : v.cvss_score >= 7 ? '#ff6b35' : '#f59e0b'}`">
                  {{ v.cvss_score.toFixed(1) }}
                </span>
                <span v-else style="color:#2d4356;">—</span>
              </td>
              <td class="pr-5">
                <span class="text-xs font-bold uppercase" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">{{ v.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab: Scan Jobs -->
    <div v-show="activeTab === 'jobs'">
      <div class="space-y-3">
        <div v-if="!jobs.length" class="card text-center py-12" style="color:#4b6277;">Sin jobs ejecutados</div>
        <div v-for="job in jobs" :key="job.id" class="card flex items-center gap-4">
          <!-- Status icon -->
          <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 text-lg"
            :style="job.status === 2 ? 'background:rgba(0,255,157,0.08);border:1px solid rgba(0,255,157,0.2);' :
                    job.status === 1 ? 'background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.2);' :
                    job.status === 0 ? 'background:rgba(255,56,100,0.08);border:1px solid rgba(255,56,100,0.2);' :
                    'background:rgba(75,98,119,0.1);border:1px solid #1e2d3d;'">
            {{ job.status === 2 ? '✅' : job.status === 1 ? '⏳' : job.status === 0 ? '❌' : '🕐' }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-1">
              <div class="text-sm font-bold" style="color:#fff;font-family:'Rajdhani',sans-serif;letter-spacing:0.04em;">{{ SCAN_LABELS[job.scan_type] || job.scan_type }}</div>
              <div v-if="job.status === 1" class="h-0.5 flex-1 rounded-full overflow-hidden" style="background:#1e2d3d;max-width:120px;">
                <div class="h-full animate-shimmer rounded-full" style="background:linear-gradient(90deg,rgba(0,212,255,0.2),rgba(0,212,255,0.8),rgba(0,212,255,0.2));background-size:200% 100%;width:75%;"></div>
              </div>
            </div>
            <div class="flex items-center gap-4 text-xs" style="color:#4b6277;">
              <span class="font-mono">{{ (Array.isArray(job.targets) ? job.targets : [job.targets]).join(', ') }}</span>
              <span>{{ job.hosts_found }} hosts</span>
              <span>{{ job.ports_found }} puertos</span>
              <span>{{ job.vulns_found }} vulns</span>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <RouterLink to="/scan-jobs" class="text-xs font-bold hover:text-cyan transition-colors" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">LOGS →</RouterLink>
            <button v-if="job.status !== 1" @click="deleteJob(job)"
              class="w-7 h-7 rounded-lg flex items-center justify-center transition-all hover:scale-105"
              style="color:#ff3864;background:rgba(255,56,100,0.08);border:1px solid rgba(255,56,100,0.15);"
              title="Eliminar">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="flex items-center justify-center h-64">
    <div class="flex items-center gap-3" style="color:#4b6277;">
      <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
      Cargando engagement...
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/composables/api'

const route  = useRoute()
const router = useRouter()
const id     = route.params.id

const eng        = ref(null)
const dash       = ref({})
const hosts      = ref([])
const vulns      = ref([])
const jobs       = ref([])
const activeTab  = ref('hosts')
const aiAnalysis = ref('')
const aiLoading  = ref(false)

const SCAN_LABELS = {
  discovery: 'Host Discovery', port: 'Port Scan', service: 'Service Detection',
  vuln: 'Vuln Scan', ssl: 'SSL Audit', smb: 'SMB Audit', ad: 'AD Audit',
  brute: 'Credential Brute Force', snmp: 'SNMP Audit', full: 'Full Audit',
}

const SCOLOR = {
  critical: '#ff3864', high: '#ff6b35', medium: '#f59e0b',
  low: '#4cc9f0', info: '#4b6277',
}

const tabs = computed(() => [
  { id: 'hosts', label: 'Hosts',           count: hosts.value.length },
  { id: 'vulns', label: 'Vulnerabilidades', count: vulns.value.length },
  { id: 'jobs',  label: 'Scan Jobs',        count: jobs.value.length },
])

onMounted(async () => {
  try {
    const [engRes, dashRes, hostsRes, vulnsRes, jobsRes] = await Promise.all([
      api.get(`/engagements/${id}/`),
      api.get(`/engagements/${id}/dashboard/`).catch(() => ({ data: {} })),
      api.get(`/hosts/?engagement=${id}&page_size=100`).catch(() => ({ data: [] })),
      api.get(`/vulns/by_engagement/?engagement=${id}`).catch(() => ({ data: [] })),
      api.get(`/scan-jobs/?engagement=${id}`).catch(() => ({ data: [] })),
    ])
    eng.value   = engRes.data
    dash.value  = dashRes.data || {}
    hosts.value = hostsRes.data.results || hostsRes.data || []
    vulns.value = vulnsRes.data.results || vulnsRes.data || []
    jobs.value  = jobsRes.data.results  || jobsRes.data  || []

    if (eng.value.notes) aiAnalysis.value = eng.value.notes
  } catch (e) {
    console.error('Error cargando engagement:', e)
  }
})

async function updateStatus() {
  try {
    await api.patch(`/engagements/${id}/`, { status: eng.value.status })
  } catch (e) {
    alert('Error al actualizar estado: ' + (e.response?.data?.detail || e.message))
  }
}

async function deleteJob(job) {
  if (!confirm(`¿Eliminar escaneo "${SCAN_LABELS[job.scan_type] || job.scan_type}"?\nEsta acción no se puede deshacer.`)) return
  try {
    await api.delete(`/scan-jobs/${job.id}/`)
    jobs.value = jobs.value.filter(j => j.id !== job.id)
  } catch (e) {
    alert('Error al eliminar: ' + (e.response?.data?.detail || e.message))
  }
}

async function deleteEngagement() {
  if (!confirm(`¿Eliminar "${eng.value?.name}"?\nSe borrarán todos los hosts, vulnerabilidades y escaneos asociados. Esta acción no se puede deshacer.`)) return
  try {
    await api.delete(`/engagements/${id}/`)
    router.push('/engagements')
  } catch (e) {
    alert('Error al eliminar: ' + (e.response?.data?.detail || e.message))
  }
}

async function runAiAnalysis() {
  aiLoading.value = true
  try {
    await api.post(`/ai/engagement/${id}/`)
    const poll = setInterval(async () => {
      const engRes = await api.get(`/engagements/${id}/`)
      if (engRes.data.notes) {
        aiAnalysis.value = engRes.data.notes
        aiLoading.value  = false
        clearInterval(poll)
      }
    }, 3000)
    setTimeout(() => { clearInterval(poll); aiLoading.value = false }, 120000)
  } catch { aiLoading.value = false }
}
</script>
