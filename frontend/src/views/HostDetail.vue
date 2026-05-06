<template>
  <div v-if="host" class="space-y-5 animate-entry">

    <!-- Header -->
    <div class="flex items-start justify-between">
      <div class="flex items-start gap-4">
        <!-- OS icon -->
        <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl flex-shrink-0" style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.15);">
          {{ OS_EMOJI[host.os_family] || '🖥' }}
        </div>
        <div>
          <div class="flex items-center gap-3 mb-1">
            <span class="w-2 h-2 rounded-full" :class="host.is_alive ? 'bg-green animate-pulse' : 'bg-muted'"></span>
            <span class="font-mono text-sm" style="color:#00d4ff;">{{ host.ip_address }}</span>
            <span v-if="host.mac_address" class="font-mono text-xs px-2 py-0.5 rounded" style="color:#4b6277;background:rgba(0,0,0,0.4);border:1px solid #1e2d3d;">{{ host.mac_address }}</span>
          </div>
          <h1 class="page-title" style="font-size:22px;">{{ host.hostname || host.ip_address }}</h1>
          <div class="text-sm mt-1" style="color:#4b6277;">{{ host.os_name || 'Sistema operativo desconocido' }}
            <span v-if="host.os_accuracy" class="ml-2 text-xs" style="color:#2d4356;">({{ host.os_accuracy }}% conf.)</span>
          </div>
        </div>
      </div>

      <!-- Risk score -->
      <div class="card text-center px-6 py-4">
        <div class="text-xs uppercase tracking-wider mb-1" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">Risk Score</div>
        <div class="text-5xl font-bold leading-none" style="font-family:'Rajdhani',sans-serif;"
          :style="`color:${host.risk_score > 70 ? '#ff3864' : host.risk_score > 40 ? '#ff6b35' : '#00ff9d'}`">
          {{ host.risk_score?.toFixed(0) || 0 }}
        </div>
        <div class="mt-2 h-1.5 rounded-full" style="background:#1e2d3d;width:80px;">
          <div class="h-full rounded-full transition-all duration-700"
            :style="`width:${Math.min(host.risk_score, 100)}%;background:${host.risk_score > 70 ? '#ff3864' : host.risk_score > 40 ? '#ff6b35' : '#00ff9d'}`"></div>
        </div>
      </div>
    </div>

    <!-- KPI row -->
    <div class="grid grid-cols-5 gap-3">
      <div class="stat-card"><div class="stat-value text-cyan">{{ host.open_ports }}</div><div class="stat-label">Puertos</div></div>
      <div class="stat-card"><div class="stat-value text-red">{{ vc.critical }}</div><div class="stat-label">Críticas</div></div>
      <div class="stat-card"><div class="stat-value text-orange">{{ vc.high }}</div><div class="stat-label">Altas</div></div>
      <div class="stat-card"><div class="stat-value text-yellow">{{ vc.medium }}</div><div class="stat-label">Medias</div></div>
      <div class="stat-card"><div class="stat-value text-green">{{ host.credentials?.length || 0 }}</div><div class="stat-label">Creds</div></div>
    </div>

    <!-- AI summary -->
    <div v-if="host.ai_summary" class="card border-glow-cyan" style="background:linear-gradient(135deg,rgba(0,212,255,0.04),rgba(0,0,0,0.4));">
      <div class="flex items-center gap-2 mb-3">
        <span class="text-cyan text-sm font-bold" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.06em;">🤖 ANÁLISIS DE RIESGO — CLAUDE AI</span>
      </div>
      <p class="text-sm leading-relaxed whitespace-pre-wrap" style="color:#8ba5bc;">{{ host.ai_summary }}</p>
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

    <!-- Ports tab -->
    <div v-show="activeTab === 'ports'">
      <div class="card p-0 overflow-hidden">
        <table class="vtable w-full">
          <thead><tr><th class="pl-5">Puerto</th><th>Proto</th><th>Estado</th><th>Servicio</th><th>Producto</th><th class="pr-5">Versión</th></tr></thead>
          <tbody>
            <tr v-for="p in host.ports" :key="p.id">
              <td class="pl-5"><span class="font-mono text-base font-bold text-cyan">{{ p.number }}</span></td>
              <td><span class="text-xs uppercase font-bold" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">{{ p.protocol }}</span></td>
              <td>
                <span class="text-xs px-2 py-0.5 rounded font-bold uppercase"
                  :style="p.state === 'open' ? 'background:rgba(0,255,157,0.08);border:1px solid rgba(0,255,157,0.2);color:#00ff9d;' : 'color:#4b6277;background:transparent;border:1px solid #1e2d3d;'">
                  {{ p.state }}
                </span>
              </td>
              <td><span class="text-sm" style="color:#c9d8e5;">{{ p.service || '—' }}</span></td>
              <td><span class="text-sm" style="color:#8ba5bc;">{{ p.product || '—' }}</span></td>
              <td class="pr-5"><span class="font-mono text-xs" style="color:#4b6277;">{{ p.version || '—' }}</span></td>
            </tr>
            <tr v-if="!host.ports?.length"><td colspan="6" class="text-center py-10" style="color:#4b6277;">Sin puertos registrados</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Vulns tab -->
    <div v-show="activeTab === 'vulns'">
      <div class="card p-0 overflow-hidden">
        <table class="vtable w-full">
          <thead><tr><th class="pl-5">Sev</th><th>Título</th><th>CVE</th><th>CVSS</th><th class="pr-5">Estado</th></tr></thead>
          <tbody>
            <tr v-for="v in host.vulnerabilities" :key="v.id">
              <td class="pl-5"><span :class="`badge-${v.severity}`">{{ v.severity }}</span></td>
              <td class="max-w-xs">
                <RouterLink :to="`/vulns/${v.id}`" class="text-sm font-semibold hover:text-cyan transition-colors truncate block max-w-[300px]" style="color:#c9d8e5;font-family:'Rajdhani',sans-serif;">{{ v.title }}</RouterLink>
              </td>
              <td><span class="font-mono text-xs" style="color:#4cc9f0;">{{ v.cve_id || '—' }}</span></td>
              <td><span v-if="v.cvss_score" class="font-mono text-xs font-bold"
                :style="`color:${v.cvss_score>=9?'#ff3864':v.cvss_score>=7?'#ff6b35':'#f59e0b'}`">{{ v.cvss_score.toFixed(1) }}</span>
                <span v-else class="text-xs" style="color:#2d4356;">—</span>
              </td>
              <td class="pr-5"><span class="text-xs font-bold uppercase" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">{{ v.status }}</span></td>
            </tr>
            <tr v-if="!host.vulnerabilities?.length"><td colspan="5" class="text-center py-10" style="color:#4b6277;">Sin vulnerabilidades</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Credentials tab -->
    <div v-show="activeTab === 'creds'">
      <div class="card p-0 overflow-hidden">
        <table class="vtable w-full">
          <thead><tr><th class="pl-5">Servicio</th><th>Usuario</th><th>Contraseña / Hash</th><th>Válida</th><th class="pr-5">Detectada</th></tr></thead>
          <tbody>
            <tr v-for="c in host.credentials" :key="c.id">
              <td class="pl-5"><span class="font-mono text-xs font-bold text-cyan uppercase">{{ c.service }}</span></td>
              <td><span class="font-mono text-sm" style="color:#fff;">{{ c.username }}</span></td>
              <td>
                <span v-if="c.password" class="font-mono text-sm" style="color:#00ff9d;">{{ showPwd ? c.password : '••••••••' }}</span>
                <span v-else-if="c.hash_value" class="font-mono text-xs" style="color:#f59e0b;">{{ c.hash_value.slice(0,24) }}...</span>
                <span v-else style="color:#2d4356;">—</span>
              </td>
              <td><span :class="c.valid ? 'text-green font-bold' : 'text-muted'">{{ c.valid ? '✓' : '✗' }}</span></td>
              <td class="pr-5"><span class="text-xs" style="color:#4b6277;">{{ formatDate(c.found_at) }}</span></td>
            </tr>
            <tr v-if="!host.credentials?.length"><td colspan="5" class="text-center py-10" style="color:#4b6277;">Sin credenciales encontradas</td></tr>
          </tbody>
        </table>
        <div v-if="host.credentials?.length" class="px-4 py-2 border-t" style="border-color:#1e2d3d;">
          <button @click="showPwd = !showPwd" class="text-xs btn-ghost px-3 py-1">{{ showPwd ? '🙈 Ocultar' : '👁 Mostrar' }} contraseñas</button>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="flex items-center justify-center h-64">
    <div class="flex items-center gap-3" style="color:#4b6277;">
      <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
      Cargando host...
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/composables/api'

const route     = useRoute()
const id        = route.params.id
const host      = ref(null)
const loading   = ref(true)
const activeTab = ref('ports')
const showPwd   = ref(false)

const OS_EMOJI = { windows: '🪟', linux: '🐧', macos: '🍎', network: '🌐', embedded: '📟', unknown: '🖥' }

const vc = computed(() => {
  const vulns = host.value?.vulnerabilities || []
  return {
    critical: vulns.filter(v => v.severity === 'critical').length,
    high:     vulns.filter(v => v.severity === 'high').length,
    medium:   vulns.filter(v => v.severity === 'medium').length,
  }
})

const tabs = computed(() => [
  { id: 'ports', label: 'Puertos',          count: host.value?.ports?.length },
  { id: 'vulns', label: 'Vulnerabilidades', count: host.value?.vulnerabilities?.length },
  { id: 'creds', label: 'Credenciales',     count: host.value?.credentials?.length },
])

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(async () => {
  try {
    const res = await api.get(`/hosts/${id}/`)
    host.value = res.data
  } finally { loading.value = false }
})
</script>
