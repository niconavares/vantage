<template>
  <div v-if="vuln" class="space-y-5 animate-entry">

    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 text-sm">
      <RouterLink to="/vulns" class="hover:text-cyan transition-colors" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:600;">VULNERABILIDADES</RouterLink>
      <svg class="w-3 h-3" style="color:#2d4356;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
      <span class="text-sm truncate max-w-xs" style="color:#8ba5bc;font-family:'Rajdhani',sans-serif;font-weight:600;">{{ vuln.title }}</span>
    </div>

    <!-- Header -->
    <div class="card" :style="vuln.severity === 'critical' ? 'border-color:rgba(255,56,100,0.25);background:linear-gradient(135deg,rgba(255,56,100,0.04),rgba(0,0,0,0.6));' : ''">
      <div class="flex items-start justify-between gap-4">
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-3 flex-wrap">
            <span :class="`badge-${vuln.severity}`" style="font-size:13px;padding:4px 10px;">{{ vuln.severity }}</span>
            <span v-if="vuln.cvss_score" class="text-sm font-bold font-mono px-3 py-1 rounded-lg"
              :style="`color:${vuln.cvss_score>=9?'#ff3864':vuln.cvss_score>=7?'#ff6b35':'#f59e0b'};background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.06);`">
              CVSS {{ vuln.cvss_score.toFixed(1) }}
            </span>
            <a v-if="vuln.cve_id" :href="`https://nvd.nist.gov/vuln/detail/${vuln.cve_id}`" target="_blank"
              class="font-mono text-xs px-3 py-1 rounded-lg hover:underline transition-colors"
              style="color:#4cc9f0;background:rgba(76,201,240,0.08);border:1px solid rgba(76,201,240,0.2);">
              {{ vuln.cve_id }}
            </a>
          </div>
          <h1 class="page-title" style="font-size:20px;line-height:1.3;">{{ vuln.title }}</h1>
          <div class="flex items-center gap-4 mt-2 text-sm" style="color:#4b6277;">
            <span>Host: <span class="text-cyan font-mono">{{ vuln.host_ip }}</span></span>
            <span v-if="vuln.source" style="font-family:'JetBrains Mono',monospace;font-size:11px;">{{ vuln.source }}</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:11px;">{{ formatDate(vuln.discovered_at) }}</span>
          </div>
        </div>
        <!-- Status selector -->
        <select v-model="statusVal" @change="updateStatus"
          class="input w-44 flex-shrink-0 text-xs font-bold uppercase"
          style="font-family:'Rajdhani',sans-serif;letter-spacing:0.06em;">
          <option value="open">ABIERTA</option>
          <option value="confirmed">CONFIRMADA</option>
          <option value="false_positive">FALSO POSITIVO</option>
          <option value="mitigated">MITIGADA</option>
          <option value="accepted">RIESGO ACEPTADO</option>
        </select>
      </div>
    </div>

    <!-- Content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="lg:col-span-2 space-y-4">

        <!-- Description -->
        <div class="card">
          <div class="flex items-center gap-2 mb-3">
            <div class="w-1 h-5 rounded-full bg-cyan"></div>
            <span class="section-title">Descripción</span>
          </div>
          <p class="text-sm leading-relaxed whitespace-pre-wrap" style="color:#8ba5bc;">{{ vuln.description }}</p>
        </div>

        <!-- Evidence -->
        <div v-if="vuln.evidence" class="card">
          <div class="flex items-center gap-2 mb-3">
            <div class="w-1 h-5 rounded-full" style="background:#00ff9d;"></div>
            <span class="section-title">Evidencia</span>
          </div>
          <div class="terminal overflow-x-auto">
            <pre class="text-xs whitespace-pre-wrap" style="color:#00ff9d;">{{ vuln.evidence }}</pre>
          </div>
        </div>

        <!-- Solution -->
        <div v-if="vuln.solution" class="card" style="border-color:rgba(0,255,157,0.15);background:linear-gradient(135deg,rgba(0,255,157,0.02),rgba(0,0,0,0.5));">
          <div class="flex items-center gap-2 mb-3">
            <div class="w-1 h-5 rounded-full" style="background:#00ff9d;"></div>
            <span class="section-title" style="color:#00ff9d80;">Solución Recomendada</span>
          </div>
          <p class="text-sm leading-relaxed whitespace-pre-wrap" style="color:#8ba5bc;">{{ vuln.solution }}</p>
        </div>

        <!-- AI Analysis -->
        <div v-if="vuln.ai_analysis" class="card border-glow-cyan" style="background:linear-gradient(135deg,rgba(0,212,255,0.04),rgba(0,0,0,0.5));">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-cyan text-sm font-bold" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.06em;">🤖 ANÁLISIS CLAUDE AI</span>
          </div>
          <div class="text-sm leading-relaxed whitespace-pre-wrap" style="color:#8ba5bc;">{{ vuln.ai_analysis }}</div>
        </div>

        <!-- Run AI -->
        <div v-if="!vuln.ai_analysis" class="card border-glow-cyan" style="background:rgba(0,212,255,0.03);">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm font-bold text-cyan" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.04em;">🤖 Análisis profundo con Claude AI</div>
              <div class="text-xs mt-0.5" style="color:#4b6277;">Impacto real, CVSS contextual, pasos de explotación y remediación</div>
            </div>
            <button @click="runAi" :disabled="aiLoading" class="btn-primary text-sm flex-shrink-0">
              <svg v-if="aiLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              {{ aiLoading ? 'Analizando...' : 'Analizar' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-4">
        <!-- Tags -->
        <div v-if="vuln.tags?.length" class="card">
          <div class="section-title mb-3">Tags</div>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="tag in vuln.tags" :key="tag"
              class="text-xs px-2 py-0.5 rounded font-mono" style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.12);color:#4cc9f0;">
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- References -->
        <div v-if="vuln.references?.length" class="card">
          <div class="section-title mb-3">Referencias</div>
          <div class="space-y-2">
            <a v-for="ref in vuln.references" :key="ref" :href="ref" target="_blank"
              class="text-xs hover:underline block truncate transition-colors hover:text-cyan"
              style="color:#4cc9f0;font-family:'JetBrains Mono',monospace;">{{ ref }}</a>
          </div>
        </div>

        <!-- Metadata -->
        <div class="card">
          <div class="section-title mb-3">Metadatos</div>
          <div class="space-y-2.5 text-sm">
            <div class="flex justify-between items-start gap-2">
              <span style="color:#4b6277;">Template</span>
              <span class="font-mono text-xs text-right" style="color:#8ba5bc;">{{ vuln.template_id || '—' }}</span>
            </div>
            <div class="flex justify-between">
              <span style="color:#4b6277;">Puerto</span>
              <span class="font-mono text-cyan text-xs">{{ vuln.port || '—' }}</span>
            </div>
            <div class="flex justify-between">
              <span style="color:#4b6277;">Detectada</span>
              <span class="text-xs" style="color:#8ba5bc;">{{ formatDate(vuln.discovered_at) }}</span>
            </div>
            <div class="flex justify-between">
              <span style="color:#4b6277;">Actualizada</span>
              <span class="text-xs" style="color:#8ba5bc;">{{ formatDate(vuln.updated_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/composables/api'

const route     = useRoute()
const id        = route.params.id
const vuln      = ref(null)
const loading   = ref(true)
const aiLoading = ref(false)
const statusVal = ref('open')

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  try {
    const res = await api.get(`/vulns/${id}/`)
    vuln.value  = res.data
    statusVal.value = res.data.status
  } finally { loading.value = false }
})

async function updateStatus() {
  await api.patch(`/vulns/${id}/`, { status: statusVal.value })
  if (vuln.value) vuln.value.status = statusVal.value
}

async function runAi() {
  aiLoading.value = true
  try {
    await api.post(`/ai/vuln/${id}/`)
    const poll = setInterval(async () => {
      const r = await api.get(`/vulns/${id}/`)
      if (r.data.ai_analysis) {
        vuln.value.ai_analysis = r.data.ai_analysis
        aiLoading.value = false
        clearInterval(poll)
      }
    }, 3000)
    setTimeout(() => { clearInterval(poll); aiLoading.value = false }, 60000)
  } catch { aiLoading.value = false }
}
</script>
