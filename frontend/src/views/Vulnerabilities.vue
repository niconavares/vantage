<template>
  <div class="space-y-5 animate-entry">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">Vulnerabilidades</h1>
        <p class="page-subtitle">Todas las amenazas detectadas en los engagements</p>
      </div>
      <!-- Severity KPIs -->
      <div class="flex items-center gap-2">
        <div v-for="s in ['critical','high','medium','low']" :key="s"
          class="flex flex-col items-center px-3 py-1.5 rounded-xl" :style="SCOUNT_STYLE[s]">
          <span class="text-lg font-bold" :style="`color:${SCOLOR[s]};font-family:'Rajdhani',sans-serif;`">{{ counts[s] }}</span>
          <span class="text-[9px] uppercase tracking-wider" :style="`color:${SCOLOR[s]}80;font-family:'Rajdhani',sans-serif;`">{{ s }}</span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex gap-3 flex-wrap items-center">
      <div class="relative flex-1 max-w-sm">
        <input v-model="search" type="text" placeholder="Buscar vuln, host, CVE..." class="input pl-8" />
        <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5" style="color:#4b6277;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
      </div>
      <div class="flex gap-2">
        <button v-for="s in ['all','critical','high','medium','low','info']" :key="s"
          @click="severityFilter = s === 'all' ? '' : s"
          class="px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all"
          :style="(severityFilter === s || (s==='all' && !severityFilter))
            ? `background:${SCOLOR[s] || '#00d4ff'}20;border:1px solid ${SCOLOR[s] || '#00d4ff'}40;color:${SCOLOR[s] || '#00d4ff'};`
            : 'background:rgba(0,0,0,0.3);border:1px solid #1e2d3d;color:#4b6277;'"
          style-override="font-family:'Rajdhani',sans-serif;">
          {{ s === 'all' ? 'TODOS' : s }}
        </button>
      </div>
      <select v-model="statusFilter" class="input max-w-[160px]">
        <option value="">Todos los estados</option>
        <option value="open">Abierta</option>
        <option value="confirmed">Confirmada</option>
        <option value="false_positive">Falso Positivo</option>
        <option value="mitigated">Mitigada</option>
        <option value="accepted">Aceptada</option>
      </select>
    </div>

    <!-- Table -->
    <div class="card p-0 overflow-hidden">
      <table class="vtable w-full">
        <thead>
          <tr>
            <th class="pl-5 w-8"></th>
            <th>Severidad</th>
            <th>Vulnerabilidad</th>
            <th>Host</th>
            <th>CVE</th>
            <th>CVSS</th>
            <th>Estado</th>
            <th class="pr-5">Fuente</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="8" class="text-center py-16" style="color:#4b6277;">Cargando vulnerabilidades...</td>
          </tr>
          <tr v-else-if="!filtered.length">
            <td colspan="8" class="text-center py-16" style="color:#4b6277;">
              <div class="text-3xl mb-2 opacity-30">🛡</div>
              Sin vulnerabilidades
            </td>
          </tr>
          <tr v-for="v in filtered" :key="v.id">
            <td class="pl-5">
              <div class="w-2 h-2 rounded-full" :style="`background:${SCOLOR[v.severity]};box-shadow:0 0 6px ${SCOLOR[v.severity]}80`"></div>
            </td>
            <td>
              <span :class="`badge-${v.severity}`">{{ v.severity }}</span>
            </td>
            <td class="max-w-xs">
              <RouterLink :to="`/vulns/${v.id}`" class="text-sm font-semibold hover:text-cyan transition-colors block truncate max-w-[280px]" style="color:#c9d8e5;font-family:'Rajdhani',sans-serif;letter-spacing:0.02em;" :title="v.title">{{ v.title }}</RouterLink>
              <div v-if="v.template_id" class="text-[10px] font-mono mt-0.5" style="color:#4b6277;">{{ v.template_id }}</div>
            </td>
            <td><span class="font-mono text-xs text-cyan">{{ v.host_ip }}</span></td>
            <td>
              <a v-if="v.cve_id" :href="`https://nvd.nist.gov/vuln/detail/${v.cve_id}`" target="_blank"
                class="font-mono text-xs hover:underline" style="color:#4cc9f0;">{{ v.cve_id }}</a>
              <span v-else class="font-mono text-xs" style="color:#2d4356;">—</span>
            </td>
            <td>
              <span v-if="v.cvss_score" class="font-mono text-xs font-bold"
                :style="`color:${v.cvss_score >= 9 ? '#ff3864' : v.cvss_score >= 7 ? '#ff6b35' : v.cvss_score >= 4 ? '#f59e0b' : '#00ff9d'}`">
                {{ v.cvss_score.toFixed(1) }}
              </span>
              <span v-else class="font-mono text-xs" style="color:#2d4356;">—</span>
            </td>
            <td>
              <span class="text-xs px-2 py-0.5 rounded border font-bold uppercase tracking-wider"
                :style="STATUS_STYLE[v.status]"
                style-font="font-family:'Rajdhani',sans-serif;letter-spacing:0.06em;">
                {{ STATUS_SHORT[v.status] || v.status }}
              </span>
            </td>
            <td class="pr-5">
              <span class="text-xs font-mono" style="color:#4b6277;">{{ v.source || '—' }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/composables/api'

const vulns          = ref([])
const loading        = ref(true)
const search         = ref('')
const severityFilter = ref('')
const statusFilter   = ref('')

const SCOLOR = {
  critical: '#ff3864', high: '#ff6b35', medium: '#f59e0b',
  low: '#4cc9f0', info: '#4b6277', all: '#00d4ff',
}
const SCOUNT_STYLE = {
  critical: 'background:rgba(255,56,100,0.08);border:1px solid rgba(255,56,100,0.15);',
  high:     'background:rgba(255,107,53,0.08);border:1px solid rgba(255,107,53,0.15);',
  medium:   'background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.15);',
  low:      'background:rgba(76,201,240,0.08);border:1px solid rgba(76,201,240,0.15);',
}
const STATUS_SHORT = { open: 'OPEN', confirmed: 'CONFIRMED', false_positive: 'FP', mitigated: 'FIXED', accepted: 'ACCEPTED' }
const STATUS_STYLE = {
  open:           'border-color:rgba(255,56,100,0.25);color:#ff3864;background:rgba(255,56,100,0.08);',
  confirmed:      'border-color:rgba(255,107,53,0.25);color:#ff6b35;background:rgba(255,107,53,0.08);',
  false_positive: 'border-color:#1e2d3d;color:#4b6277;background:transparent;',
  mitigated:      'border-color:rgba(0,255,157,0.25);color:#00ff9d;background:rgba(0,255,157,0.08);',
  accepted:       'border-color:rgba(76,201,240,0.25);color:#4cc9f0;background:rgba(76,201,240,0.08);',
}

const counts = computed(() => ({
  critical: vulns.value.filter(v => v.severity === 'critical').length,
  high:     vulns.value.filter(v => v.severity === 'high').length,
  medium:   vulns.value.filter(v => v.severity === 'medium').length,
  low:      vulns.value.filter(v => v.severity === 'low').length,
}))

const filtered = computed(() => {
  let list = vulns.value
  if (severityFilter.value) list = list.filter(v => v.severity === severityFilter.value)
  if (statusFilter.value)   list = list.filter(v => v.status   === statusFilter.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(v =>
      v.title.toLowerCase().includes(q) ||
      (v.host_ip || '').includes(q) ||
      (v.cve_id || '').toLowerCase().includes(q)
    )
  }
  return list
})

onMounted(async () => {
  try {
    const res = await api.get('/vulns/?page_size=500')
    vulns.value = res.data.results || res.data
  } finally { loading.value = false }
})
</script>
